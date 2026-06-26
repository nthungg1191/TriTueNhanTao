import base64
import binascii
import io
import logging
import time
import traceback
import uuid
from typing import Optional
from flask import Blueprint, current_app, request, jsonify
try:
    from app.services.face_detection import FaceDetector
    from app.services.face_service import FaceService
    face_detector = FaceDetector()
except Exception:
    FaceService = None
    face_detector = None
from app import db
from app.models import Employee
from app.utils.image_utils import ImageProcessor
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

# Create blueprint
face_api = Blueprint('face_api', __name__, url_prefix='/api/face')

# Initialize services
# face_detector already initialized (or None) above

# Legacy /register endpoint removed - use /register-multi instead


@face_api.route('/recognize', methods=['POST'])
def recognize_face():
    request_id = uuid.uuid4().hex[:8]
    route_logger = current_app.logger
    start_time = time.perf_counter()
    route_logger.info(
        "[FACE_RECOGNIZE:%s] Request received: remote_addr=%s content_type=%s content_length=%s user_agent=%s",
        request_id,
        request.remote_addr,
        request.content_type,
        request.content_length,
        request.user_agent.string,
    )
    try:
        data = request.get_json(silent=True)
        
        if not data:
            raw_preview = request.get_data(cache=False, as_text=True)[:120]
            route_logger.warning(
                "[FACE_RECOGNIZE:%s] Returning 400: no/invalid JSON body. raw_preview=%r",
                request_id,
                raw_preview,
            )
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu'
            }), 400
        
        if not isinstance(data, dict):
            route_logger.warning(
                "[FACE_RECOGNIZE:%s] Returning 400: JSON body must be an object. type=%s",
                request_id,
                type(data).__name__,
            )
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu'
            }), 400

        route_logger.info("[FACE_RECOGNIZE:%s] JSON parsed: keys=%s", request_id, sorted(data.keys()))

        image_data = data.get('image')
        
        if not image_data:
            route_logger.warning(
                "[FACE_RECOGNIZE:%s] Returning 400: missing image field. keys=%s",
                request_id,
                sorted(data.keys()),
            )
            return jsonify({
                'success': False,
                'message': 'Dữ liệu ảnh là bắt buộc'
            }), 400
        
        route_logger.info(
            "[FACE_RECOGNIZE:%s] Image payload: %s",
            request_id,
            _describe_image_payload(image_data),
        )
        
        # Decode image
        image = _decode_image(image_data, request_id=request_id)
        if image is None:
            route_logger.warning("[FACE_RECOGNIZE:%s] Returning 400: failed to decode image payload", request_id)
            return jsonify({
                'success': False,
                'message': 'Dữ liệu ảnh không hợp lệ'
            }), 400
        
        route_logger.info("[FACE_RECOGNIZE:%s] Image decoded: %s", request_id, _describe_decoded_image(image))
        
        # Check service availability
        if face_detector is None:
            route_logger.error("[FACE_RECOGNIZE:%s] face_detector is None - face_recognition module not loaded", request_id)
            return jsonify({'success': False, 'message': 'Face recognition service not available on this environment.'}), 500

        # Process image for face detection
        route_logger.info(
            "[FACE_RECOGNIZE:%s] Calling face detection pipeline: model=%s tolerance=%s upsample=%s",
            request_id,
            getattr(face_detector, 'model', None),
            getattr(face_detector, 'tolerance', None),
            getattr(face_detector, 'upsample', None),
        )
        result = _process_image_for_recognition(image, request_id)
        route_logger.info(
            "[FACE_RECOGNIZE:%s] Detection result: attempt=%s faces_found=%s locations=%s encodings=%s names=%s error=%s",
            request_id,
            result.get('detection_attempt'),
            result.get('faces_found'),
            result.get('face_locations'),
            len(result.get('face_encodings') or []),
            result.get('names'),
            result.get('error'),
        )
        
        if result.get('error'):
            route_logger.error("[FACE_RECOGNIZE:%s] Detection error: %s", request_id, result.get('error'))
            return jsonify({
                'success': False,
                'message': f"Lỗi phát hiện khuôn mặt: {result.get('error')}"
            }), 500
        
        if result['faces_found'] == 0:
            route_logger.warning(
                "[FACE_RECOGNIZE:%s] Returning 400: no face detected after fallback. last_attempt=%s image=%s",
                request_id,
                result.get('detection_attempt'),
                _describe_decoded_image(image),
            )
            return jsonify({
                'success': False,
                'message': 'Không có khuôn mặt trong ảnh'
            }), 400
        
        if result['faces_found'] > 1:
            route_logger.warning(
                "[FACE_RECOGNIZE:%s] Returning 400: multiple faces detected. attempt=%s faces_found=%s locations=%s",
                request_id,
                result.get('detection_attempt'),
                result['faces_found'],
                result.get('face_locations'),
            )
            return jsonify({
                'success': False,
                'message': 'Nhiều khuôn mặt được phát hiện. Vui lòng sử dụng ảnh với một khuôn mặt'
            }), 400
        
        # Get face encoding
        face_encoding = result['face_encodings'][0]
        route_logger.info(
            "[FACE_RECOGNIZE:%s] Got face encoding: shape=%s dtype=%s norm=%.6f",
            request_id,
            getattr(face_encoding, 'shape', None),
            getattr(face_encoding, 'dtype', None),
            float(np.linalg.norm(face_encoding)),
        )
        
        # Recognize employee using multi-embedding system
        face_service = FaceService(db.session)

        # Get number of registered faces for debug info
        try:
            _, known_codes = face_service._get_cached_face_embeddings()
            num_registered = len(known_codes)
        except Exception:
            num_registered = 0

        route_logger.info("[FACE_RECOGNIZE:%s] Calling face_service.recognize_employee_multi()", request_id)
        recognition_result = face_service.recognize_employee_multi(face_encoding, use_multi_embedding=True)
        route_logger.info("[FACE_RECOGNIZE:%s] Recognition result: %s", request_id, recognition_result)

        if recognition_result.get('success') and recognition_result.get('employee_code'):
            employee = Employee.query.filter_by(employee_code=recognition_result['employee_code']).first()
            if employee:
                recognition_result['employee_name'] = employee.name
        else:
            # Normalize unrecognized face messages for kiosk display
            recognition_result['message'] = 'Khong nhan dien duoc khuon mat. Vui long lien he quan tri vien.'

        # Always include debug fields
        recognition_result['min_distance'] = recognition_result.get('distance')
        recognition_result['confidence'] = recognition_result.get('confidence')
        recognition_result['tolerance'] = recognition_result.get('tolerance')
        recognition_result['num_registered_faces'] = recognition_result.get('num_registered_faces', num_registered)

        route_logger.info(
            "[FACE_RECOGNIZE:%s] Completed: success=%s employee_code=%s "
            "min_distance=%s confidence=%s tolerance=%s num_registered=%s elapsed_ms=%.1f",
            request_id,
            recognition_result.get('success'),
            recognition_result.get('employee_code'),
            recognition_result.get('min_distance'),
            recognition_result.get('confidence'),
            recognition_result.get('tolerance'),
            recognition_result.get('num_registered_faces'),
            (time.perf_counter() - start_time) * 1000,
        )
        return jsonify(recognition_result), 200

    except Exception as e:
        route_logger.exception(
            "[FACE_RECOGNIZE:%s] Unhandled exception after %.1fms",
            request_id,
            (time.perf_counter() - start_time) * 1000,
        )
        return jsonify({
            'success': False,
            'message': f'Nhận dạng thất bại: {str(e)}'
        }), 500


@face_api.route('/detect', methods=['POST'])
def detect_faces():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu'
            }), 400
        
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu ảnh là bắt buộc'
            }), 400
        
        # Decode image
        image = _decode_image(image_data)
        if image is None:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu ảnh không hợp lệ'
            }), 400
        
        if face_detector is None:
            return jsonify({'success': False, 'message': 'Face recognition service not available on this environment.'}), 500

        # Detect faces
        result = face_detector.process_image(image)
        
        # Convert face locations to serializable format
        face_locations = []
        for (top, right, bottom, left) in result['face_locations']:
            face_locations.append({
                'top': int(top),
                'right': int(right),
                'bottom': int(bottom),
                'left': int(left)
            })
        
        return jsonify({
            'success': True,
            'faces_found': result['faces_found'],
            'face_locations': face_locations,
            'names': result['names']
        }), 200
        
    except Exception as e:
        logger.error(f"Lỗi phát hiện khuôn mặt: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Phát hiện thất bại: {str(e)}'
        }), 500


# Legacy endpoints removed (not used by frontend):
# - /enroll: Use /register-multi instead
# - /capture: Not used, requires camera_service
# - /encodings: Not used


@face_api.route('/employee/<employee_code>', methods=['GET'])
def get_employee_face(employee_code):
    try:
        if FaceService is None:
            return jsonify({'success': False, 'message': 'Face service not available on this environment.'}), 500
        face_service = FaceService(db.session)
        encoding = face_service.get_employee_face_encoding(employee_code)
        
        if encoding is None:
            return jsonify({
                'success': False,
                'message': f'Không tìm thấy khuôn mặt cho nhân viên {employee_code}'
            }), 404
        
        return jsonify({
            'success': True,
            'employee_code': employee_code,
            'has_encoding': True
        }), 200
        
    except Exception as e:
        logger.error(f"Lỗi lấy khuôn mặt nhân viên: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lấy thất bại: {str(e)}'
        }), 500


@face_api.route('/employee/<employee_code>', methods=['DELETE'])
def delete_employee_face(employee_code):
    try:
        face_service = FaceService(db.session)
        result = face_service.delete_employee_face(employee_code)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Lỗi xóa khuôn mặt nhân viên: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Xóa thất bại: {str(e)}'
        }), 500


# Legacy /statistics endpoint removed - using /statistics with get_embedding_statistics() instead

# Backup/restore endpoints removed (not used by frontend):
# - /backup: Not used
# - /restore: Not used


@face_api.route('/register-multi', methods=['POST'])
def register_face_multi():
    route_logger = current_app.logger
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu'
            }), 400
        
        employee_code = data.get('employee_code')
        image_data = data.get('image')
        variant_type = data.get('variant_type', 'default')
        description = data.get('description')
        set_as_primary = data.get('set_as_primary', False)
        
        if not employee_code:
            return jsonify({
                'success': False,
                'message': 'Mã nhân viên là bắt buộc'
            }), 400
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu ảnh là bắt buộc'
            }), 400
        
        # Decode image
        image = _decode_image(image_data)
        if image is None:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu ảnh không hợp lệ',
                'error_type': 'decode'
            }), 400
        
        face_service = FaceService(db.session)
        
        if face_detector is None:
            return jsonify({'success': False, 'message': 'Face recognition service not available on this environment.'}), 500
        # Detect and encode face
        result_detect = face_detector.process_image(image)
        if result_detect['faces_found'] == 0:
            return jsonify({
                'success': False,
                'message': 'Không nhận diện được khuôn mặt. Hãy chụp lại với ánh sáng tốt hơn.',
                'error_type': 'detect'
            }), 400
        if result_detect['faces_found'] > 1:
            return jsonify({
                'success': False,
                'message': 'Ảnh có nhiều hơn 1 khuôn mặt. Vui lòng dùng ảnh chỉ có 1 khuôn mặt.',
                'error_type': 'detect'
            }), 400
        
        face_encoding = result_detect['face_encodings'][0]

        # --- Duplicate face check ---
        try:
            recognition = face_service.recognize_employee_multi(face_encoding, use_multi_embedding=True, exclude_employee_code=employee_code)
            route_logger.info(
                "[REGISTER-MULTI:%s] Duplicate check result: success=%s matched=%s distance=%.4f tolerance=%.4f confidence=%.4f",
                employee_code,
                recognition.get('success'),
                recognition.get('employee_code'),
                recognition.get('distance'),
                recognition.get('tolerance'),
                recognition.get('confidence'),
            )
            route_logger.info(
                "[REGISTER-MULTI:%s] Check condition: recognition['success']=%s, recognition['employee_code']=%r, employee_code=%s",
                employee_code,
                bool(recognition.get('success')),
                recognition.get('employee_code'),
                employee_code,
            )
            if recognition.get('success') and recognition.get('employee_code'):
                matched_code = recognition['employee_code']
                route_logger.info(
                    "[REGISTER-MULTI:%s] matched_code=%s != employee_code=%s ? %s -> WILL REJECT",
                    employee_code, matched_code, employee_code, matched_code != employee_code
                )
                if matched_code != employee_code:
                    route_logger.warning(
                        "[REGISTER-MULTI:%s] Duplicate face detected: matched=%s (not self), distance=%.4f",
                        employee_code, matched_code, recognition.get('distance')
                    )
                    return jsonify({
                        'success': False,
                        'message': 'Khuon mat nay da dang ky cho nhan vien %s' % matched_code,
                        'error_type': 'duplicate',
                        'employee_code': employee_code,
                        'matched_employee_code': matched_code,
                        'min_distance': recognition.get('distance'),
                        'confidence': recognition.get('confidence'),
                        'tolerance': recognition.get('tolerance'),
                    }), 409
            else:
                route_logger.info(
                    "[REGISTER-MULTI:%s] No duplicate found (or recognition failed). Proceeding with registration. success=%s emp_code=%r",
                    employee_code, recognition.get('success'), recognition.get('employee_code')
                )
        except Exception as e:
            route_logger.error("[REGISTER-MULTI:%s] Recognition check threw exception: %s. Allowing registration to proceed.", employee_code, str(e))
            # Do NOT silently pass - log but still allow through

        result = face_service.add_face_embedding(
            employee_code=employee_code,
            embedding=face_encoding,
            variant_type=variant_type,
            embedding_type='standard',
            description=description,
            set_as_primary=set_as_primary
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            result['error_type'] = 'embedding'
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"lỗi đăng ký khuôn mặt: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Đăng ký thất bại: {str(e)}',
            'error_type': 'unknown'
        }), 500


@face_api.route('/embeddings/<employee_code>', methods=['GET'])
def get_employee_embeddings(employee_code):
    try:
        face_service = FaceService(db.session)
        embeddings = face_service.get_employee_embeddings(employee_code, active_only=True)
        
        embeddings_data = [emb.to_dict() for emb in embeddings]
        
        return jsonify({
            'success': True,
            'employee_code': employee_code,
            'total_embeddings': len(embeddings_data),
            'embeddings': embeddings_data
        }), 200
        
    except Exception as e:
        logger.error(f"Lỗi lấy khuôn mặt nhân viên: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lấy thất bại: {str(e)}'
        }), 500


@face_api.route('/embedding/<int:embedding_id>', methods=['DELETE'])
def delete_face_embedding(embedding_id):
    try:
        face_service = FaceService(db.session)
        result = face_service.delete_face_embedding(embedding_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Lỗi xóa khuôn mặt nhân viên: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Xóa thất bại: {str(e)}'
        }), 500


@face_api.route('/embedding/<int:embedding_id>/primary', methods=['PUT'])
def set_primary_embedding(embedding_id):
    try:
        face_service = FaceService(db.session)
        result = face_service.set_primary_embedding(embedding_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Lỗi đặt khuôn mặt chính: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Đặt thất bại: {str(e)}'
        }), 500


@face_api.route('/statistics', methods=['GET'])
def get_embedding_statistics():
    try:
        face_service = FaceService(db.session)
        stats = face_service.get_embedding_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Lỗi lấy thống kê khuôn mặt: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lấy thất bại: {str(e)}'
        }), 500


# ========== HELPER FUNCTIONS ==========
# Note: Video registration endpoint and helper functions removed
# System now uses static photo capture (2-3 images) via /register-multi endpoint


def _process_image_for_recognition(image: np.ndarray, request_id: Optional[str] = None) -> dict:
    """
    Run face detection with fallbacks for small webcam frames.

    Kiosk cameras may provide 320x240 frames. HOG with upsample=0 often misses
    smaller faces, so retry with a modest upsample and a 2x frame before
    returning "no face".
    """
    route_logger = current_app.logger

    attempts = [
        {
            'name': 'original',
            'image': image,
            'upsample': getattr(face_detector, 'upsample', 0),
        },
        {
            'name': 'original_upsample_1',
            'image': image,
            'upsample': max(getattr(face_detector, 'upsample', 0), 1),
        },
    ]

    height, width = image.shape[:2]
    if max(height, width) < 720:
        scaled = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        attempts.append({
            'name': 'upscaled_2x_upsample_1',
            'image': scaled,
            'upsample': 1,
        })

        enhanced = ImageProcessor.enhance_for_face_recognition(scaled)
        attempts.append({
            'name': 'upscaled_2x_enhanced_upsample_1',
            'image': enhanced,
            'upsample': 1,
        })

    last_result = None
    for attempt in attempts:
        detector = face_detector
        if attempt['name'] != 'original' or attempt['upsample'] != getattr(face_detector, 'upsample', 0):
            detector = FaceDetector(
                model=getattr(face_detector, 'model', 'hog'),
                tolerance=getattr(face_detector, 'tolerance', None),
                upsample=attempt['upsample'],
            )

        route_logger.info(
            "[FACE_RECOGNIZE:%s] Detection attempt: name=%s image=%s model=%s upsample=%s",
            request_id,
            attempt['name'],
            _describe_decoded_image(attempt['image']),
            getattr(detector, 'model', None),
            getattr(detector, 'upsample', None),
        )
        result = detector.process_image(attempt['image'])
        result['detection_attempt'] = attempt['name']
        last_result = result

        route_logger.info(
            "[FACE_RECOGNIZE:%s] Detection attempt result: name=%s faces_found=%s encodings=%s error=%s",
            request_id,
            attempt['name'],
            result.get('faces_found'),
            len(result.get('face_encodings') or []),
            result.get('error'),
        )

        if result.get('error') or result.get('faces_found', 0) > 0:
            return result

    return last_result or {
        'faces_found': 0,
        'face_locations': [],
        'face_encodings': [],
        'names': [],
    }


def _describe_image_payload(image_data: str) -> str:
    if not isinstance(image_data, str):
        return f"type={type(image_data).__name__}"

    prefix, base64_data = ('', image_data)
    if ',' in image_data:
        prefix, base64_data = image_data.split(',', 1)

    return (
        f"type=str length={len(image_data)} has_data_url={bool(prefix)} "
        f"prefix={prefix[:60]!r} base64_length={len(base64_data)}"
    )


def _describe_decoded_image(image: np.ndarray) -> str:
    if image is None:
        return "None"

    summary = f"shape={image.shape} dtype={image.dtype}"
    if image.size:
        summary += f" min={int(np.min(image))} max={int(np.max(image))}"
    return summary


def _decode_image(image_data: str, request_id: Optional[str] = None) -> Optional[np.ndarray]:

    try:
        decode_logger = current_app.logger
        if not isinstance(image_data, str):
            decode_logger.warning(
                "[FACE_RECOGNIZE:%s] Image payload is not a string: type=%s",
                request_id,
                type(image_data).__name__,
            )
            return None

        # Remove data URL prefix if present
        if ',' in image_data:
            prefix, image_data = image_data.split(',', 1)
            decode_logger.info(
                "[FACE_RECOGNIZE:%s] Stripped data URL prefix: %s",
                request_id,
                prefix[:80],
            )
        
        # Decode base64
        image_bytes = base64.b64decode(image_data, validate=True)
        decode_logger.info("[FACE_RECOGNIZE:%s] Base64 decoded: bytes=%s", request_id, len(image_bytes))
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_bytes))
        decode_logger.info(
            "[FACE_RECOGNIZE:%s] PIL image opened: format=%s mode=%s size=%s",
            request_id,
            pil_image.format,
            pil_image.mode,
            pil_image.size,
        )
        
        # Convert to numpy array
        if pil_image.mode not in ('RGB', 'L'):
            decode_logger.info(
                "[FACE_RECOGNIZE:%s] Converting PIL mode from %s to RGB",
                request_id,
                pil_image.mode,
            )
            pil_image = pil_image.convert('RGB')

        image_array = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_array
        
    except (binascii.Error, ValueError) as e:
        current_app.logger.warning("[FACE_RECOGNIZE:%s] Invalid base64 image payload: %s", request_id, str(e))
        return None
    except Exception:
        current_app.logger.exception("[FACE_RECOGNIZE:%s] Error decoding image", request_id)
        return None
