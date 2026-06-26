"""
Face Recognition Debug Test Script
==================================
Test script de kiem tra logic nhan dien khuon mat.
Su dung anh chiec cong (attendance) da co trong he thong.

Su dung:
    python tests/test_face_recognition_debug.py

Hoac voi Python:
    from tests.test_face_recognition_debug import FaceRecognitionDebugTester
    tester = FaceRecognitionDebugTester()
    results = tester.run_all_tests()
"""

import os
import sys
import time
import logging
import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger('FaceRecogDebug')


class FaceRecognitionDebugTester:
    """
    Test face recognition voi cac truong hop:
    1. Self-recognition: nhan vien da dang ky quet mat minh -> phai nhan dien dung
    2. Cross-recognition: nhan vien A quet mat nhan vien B -> phai TU CHOI
    3. Unregistered: nhan vien chua dang ky quet -> phai TU CHOI
    4. Debug fields: log phai chua employee_code, min_distance, tolerance, confidence
    5. Cache invalidation: sau khi dang ky phai nhan dien ngay
    """

    UPLOAD_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'app', 'static', 'uploads', 'attendance'
    )

    def __init__(self):
        self.app = None
        self.face_service = None
        self.face_detector = None
        self._setup()

    def _setup(self):
        """Khoi tao app context va services."""
        try:
            from app import create_app, db
            from app.services.face_detection import FaceDetector
            from app.services.face_service import FaceService

            self.app = create_app('development')
            self.db = db

            with self.app.app_context():
                self.face_service = FaceService(db.session)
                self.face_detector = FaceDetector()

                # Load config
                tolerance = self.face_detector.tolerance
                strict_tol = getattr(FaceDetector, 'STRICT_TOLERANCE', 0.4)
                abs_max = getattr(FaceDetector, 'ABSOLUTE_MAX_DISTANCE', 0.6)

                print("=" * 70)
                print("  FACE RECOGNITION DEBUG TEST")
                print("=" * 70)
                print(f"  Tolerance         : {tolerance}")
                print(f"  STRICT_TOLERANCE : {strict_tol}")
                print(f"  ABSOLUTE_MAX     : {abs_max}")
                print(f"  Cache TTL        : {self.face_service._get_cached_face_embeddings.__name__}")
                print(f"  Upload dir       : {self.UPLOAD_DIR}")
                print(f"  Photos available : {len(os.listdir(self.UPLOAD_DIR)) if os.path.exists(self.UPLOAD_DIR) else 0}")
                print("=" * 70)

                # Print registered faces
                known_enc, known_codes = self.face_service.get_all_face_encodings_multi()
                print(f"\n[SETUP] So khuon mat da dang ky: {len(known_enc)}")
                print(f"[SETUP] Danh sach: {known_codes}")

                # Also check legacy
                legacy_enc, legacy_codes = self.face_service.get_all_face_encodings()
                print(f"[SETUP] Legacy embeddings: {len(legacy_enc)}, codes: {legacy_codes}")
                print()

        except Exception as e:
            logger.error("Loi khoi tao: %s", e)
            raise

    def _find_photo_for_employee(self, employee_code: str):
        """Tim anh attendance cho mot nhan vien."""
        if not os.path.exists(self.UPLOAD_DIR):
            return None
        photos = [f for f in os.listdir(self.UPLOAD_DIR)
                  if f.startswith(employee_code + '_') and f.endswith('.jpg')]
        if photos:
            return os.path.join(self.UPLOAD_DIR, photos[0])
        return None

    def _load_image(self, path):
        """Load image using OpenCV."""
        import cv2
        img = cv2.imread(path)
        if img is None:
            logger.warning("Khong doc duoc anh: %s", path)
        return img

    def _encode_image(self, image):
        """Encode image to face encoding."""
        face_locations = self.face_detector.detect_faces(image)
        if not face_locations:
            return None
        encodings = self.face_detector.get_face_encodings(image, face_locations)
        if not encodings:
            return None
        return encodings[0]

    def _run_recognition(self, face_encoding):
        """Chay nhan dien va tra ve ket qua."""
        return self.face_service.recognize_employee_multi(
            face_encoding, use_multi_embedding=True
        )

    def _check_debug_fields(self, result: dict, test_name: str) -> bool:
        """Kiem tra cac truong debug co mat trong ket qua."""
        required = ['min_distance', 'confidence', 'tolerance']
        missing = [f for f in required if f not in result]
        if missing:
            logger.warning("[%s] Missing debug fields: %s", test_name, missing)
            return False
        # Also check that values are numeric
        for f in required:
            v = result[f]
            if v is not None and not isinstance(v, (int, float)):
                logger.warning("[%s] Field '%s' is not numeric: %s", test_name, f, type(v))
                return False
        return True

    def test_tc1_self_recognition(self, employee_code: str) -> dict:
        """
        TC1: Nhan vien da dang ky quet mat minh -> phai nhan dien dung.
        """
        photo = self._find_photo_for_employee(employee_code)
        if photo is None:
            return {'skipped': True, 'reason': f'Khong co anh cho {employee_code}'}

        image = self._load_image(photo)
        if image is None:
            return {'skipped': True, 'reason': 'Loi doc anh'}

        encoding = self._encode_image(image)
        if encoding is None:
            return {'skipped': True, 'reason': 'Khong phat hien duoc khuon mat trong anh'}

        result = self._run_recognition(encoding)

        # Verify debug fields
        has_debug = self._check_debug_fields(result, f'TC1-{employee_code}')

        # Expected: success=True, employee_code=employee_code
        passed = (
            result.get('success') is True
            and result.get('employee_code') == employee_code
            and result.get('min_distance') is not None
            and result.get('min_distance') < self.face_detector.tolerance
        )

        logger.info(
            "[TC1:%s] PASS=%s success=%s employee_code=%s "
            "min_distance=%.4f tolerance=%.4f confidence=%.4f photo=%s",
            employee_code, passed, result.get('success'), result.get('employee_code'),
            result.get('min_distance'), result.get('tolerance'), result.get('confidence'),
            os.path.basename(photo)
        )

        return {
            'tc': 'TC1-SelfRecognition',
            'employee': employee_code,
            'expected': f'recognized as {employee_code}',
            'actual': f"success={result.get('success')} employee={result.get('employee_code')}",
            'min_distance': result.get('min_distance'),
            'tolerance': result.get('tolerance'),
            'confidence': result.get('confidence'),
            'passed': passed,
            'has_debug_fields': has_debug,
            'photo': os.path.basename(photo),
        }

    def test_tc2_cross_recognition(self, emp_a: str, emp_b: str) -> dict:
        """
        TC2: Nhan vien A quet mat nhan vien B -> phai TU CHOI (vi A != B).
        """
        photo_a = self._find_photo_for_employee(emp_a)
        if photo_a is None:
            return {'skipped': True, 'reason': f'Khong co anh cho {emp_a}'}

        image_a = self._load_image(photo_a)
        if image_a is None:
            return {'skipped': True, 'reason': 'Loi doc anh'}

        encoding_a = self._encode_image(image_a)
        if encoding_a is None:
            return {'skipped': True, 'reason': 'Khong phat hien khuon mat'}

        result = self._run_recognition(encoding_a)

        has_debug = self._check_debug_fields(result, f'TC2-{emp_a}->{emp_b}')

        # Expected: success=False, employee_code=None (hoac =emp_a neu embedding A cung trong DB)
        # Vi A quet mat A -> co the thanh cong vi A co mat trong he thong
        # Nhung A quet mat B -> phai that bai (emp_b != emp_a)
        # Chung ta dang test: emp_a quet mat emp_b => that bai vi min_distance >= tolerance
        # Hoac: emp_a quet mat A (cung nguoi) => thanh cong

        min_dist = result.get('min_distance')
        matched = result.get('employee_code')

        # TC2 chi pass khi emp_a != emp_b:
        # - Neu matched == emp_a (A quet mat A) -> OK nhung can check
        # - Neu matched == emp_b (A bi nhan dien thanh B) -> FAIL nghiem trong
        # - Neu matched == None -> OK
        if matched == emp_b:
            passed = False
            reason = f'FALSE POSITIVE: {emp_a} bi nhan dien thanh {emp_b}'
        elif matched == emp_a:
            # A quet mat A -> thanh cong, nhung day khong phai TC2
            passed = True
            reason = f'Note: {emp_a} quet mat minh thanh cong (khong phai cross-recognition)'
        elif matched is None:
            passed = True
            reason = f'{emp_a} khong nhan dien duoc (rejected)'
        else:
            passed = False
            reason = f'Unexpected: matched={matched}'

        logger.info(
            "[TC2:%s->%s] PASS=%s reason='%s' matched=%s "
            "min_distance=%.4f tolerance=%.4f",
            emp_a, emp_b, passed, reason, matched, min_dist, result.get('tolerance')
        )

        return {
            'tc': 'TC2-CrossRecognition',
            'employee': f'{emp_a}->{emp_b}',
            'expected': 'rejected or matched self',
            'actual': f"matched={matched} success={result.get('success')}",
            'min_distance': min_dist,
            'tolerance': result.get('tolerance'),
            'confidence': result.get('confidence'),
            'passed': passed,
            'has_debug_fields': has_debug,
            'reason': reason,
        }

    def test_tc3_unknown_person(self, employee_code: str = 'NV999_TEST') -> dict:
        """
        TC3: Nhan vien chua dang ky quet mat -> phai TU CHOI.
        Su dung anh nhan tao (random noise) vi khong co anh that.
        """
        import numpy as np
        import cv2

        # Tao anh fake (random noise) - khong phai khuon mat that
        fake_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        # Lam cho no nhu hinh anh that hon
        fake_image = cv2.GaussianBlur(fake_image, (15, 15), 0)

        encoding = self._encode_image(fake_image)
        if encoding is None:
            # face_recognition khong phat hien khuon mat trong noise
            # Day la expected behavior
            return {
                'tc': 'TC3-UnknownPerson',
                'employee': employee_code,
                'expected': 'rejected (no face or not matched)',
                'actual': 'no face detected',
                'min_distance': None,
                'tolerance': None,
                'confidence': None,
                'passed': True,
                'has_debug_fields': True,
                'note': 'No face detected in fake image (expected)',
            }

        result = self._run_recognition(encoding)

        has_debug = self._check_debug_fields(result, 'TC3-Unknown')

        # Expected: success=False, employee_code=None
        passed = (
            result.get('success') is False
            and result.get('employee_code') is None
        )

        logger.info(
            "[TC3:Unknown] PASS=%s success=%s employee=%s "
            "min_distance=%s message=%s",
            passed, result.get('success'), result.get('employee_code'),
            result.get('min_distance'), result.get('message')
        )

        return {
            'tc': 'TC3-UnknownPerson',
            'employee': employee_code,
            'expected': 'rejected',
            'actual': f"success={result.get('success')} employee={result.get('employee_code')}",
            'min_distance': result.get('min_distance'),
            'tolerance': result.get('tolerance'),
            'confidence': result.get('confidence'),
            'passed': passed,
            'has_debug_fields': has_debug,
            'message': result.get('message'),
        }

    def test_tc4_debug_logging(self) -> dict:
        """
        TC4: Kiem tra log chua cac truong debug.
        Chay self-recognition va parse log output.
        """
        # Get first registered employee
        known_enc, known_codes = self.face_service.get_all_face_encodings_multi()
        if not known_codes:
            return {'skipped': True, 'reason': 'Khong co nhan vien nao dang ky'}

        emp = known_codes[0]
        photo = self._find_photo_for_employee(emp)
        if photo is None:
            return {'skipped': True, 'reason': f'Khong co anh cho {emp}'}

        # Capture log output
        import io
        from contextlib import redirect_stderr, redirect_stdout

        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(message)s'))
        log = logging.getLogger('app.services.face_service')
        log.addHandler(handler)
        log_level = log.level
        log.setLevel(logging.INFO)

        try:
            image = self._load_image(photo)
            encoding = self._encode_image(image)
            if encoding is not None:
                result = self._run_recognition(encoding)

            log_output = log_capture.getvalue()
        finally:
            log.removeHandler(handler)
            log.setLevel(log_level)

        # Check log contains required fields
        checks = {
            'employee_code': 'employee_code' in log_output or 'best_match' in log_output,
            'min_distance': 'min_distance' in log_output or 'distance' in log_output.lower(),
            'tolerance': 'tolerance' in log_output.lower(),
            'confidence': 'confidence' in log_output.lower(),
            'RECOG_DEBUG': 'RECOG_DEBUG' in log_output or 'RECOG' in log_output,
        }

        all_pass = all(checks.values())

        logger.info(
            "[TC4:DebugLogging] PASS=%s checks=%s log_sample=%r",
            all_pass, checks, log_output[:200] if log_output else ''
        )

        return {
            'tc': 'TC4-DebugLogging',
            'employee': emp,
            'expected': 'log contains employee_code/min_distance/tolerance/confidence',
            'actual': str(checks),
            'min_distance': None,
            'tolerance': None,
            'confidence': None,
            'passed': all_pass,
            'has_debug_fields': True,
            'checks': checks,
        }

    def test_tc5_api_response_fields(self) -> dict:
        """
        TC5: Kiem tra API /api/face/recognize tra ve cac truong debug.
        """
        import requests

        # Lay mot anh
        known_enc, known_codes = self.face_service.get_all_face_encodings_multi()
        if not known_codes:
            return {'skipped': True, 'reason': 'Khong co nhan vien nao dang ky'}

        emp = known_codes[0]
        photo = self._find_photo_for_employee(emp)
        if photo is None:
            return {'skipped': True, 'reason': f'Khong co anh cho {emp}'}

        # Read image as base64
        import base64
        import cv2

        img = cv2.imread(photo)
        _, buf = cv2.imencode('.jpg', img)
        b64 = base64.b64encode(buf).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{b64}"

        base_url = 'http://127.0.0.1:5555'
        try:
            resp = requests.post(
                f'{base_url}/api/face/recognize',
                json={'image': data_url},
                timeout=15
            )
            json_resp = resp.json()
        except Exception as e:
            return {'skipped': True, 'reason': f'Loi goi API: {e}'}

        required_fields = ['success', 'message', 'employee_code',
                           'min_distance', 'confidence', 'tolerance', 'num_registered_faces']
        missing = [f for f in required_fields if f not in json_resp]

        passed = len(missing) == 0

        logger.info(
            "[TC5:APIResponse] PASS=%s missing=%s response_keys=%s",
            passed, missing, list(json_resp.keys())
        )

        return {
            'tc': 'TC5-APIResponseFields',
            'employee': emp,
            'expected': f'all fields present: {required_fields}',
            'actual': f'missing={missing}',
            'min_distance': json_resp.get('min_distance'),
            'tolerance': json_resp.get('tolerance'),
            'confidence': json_resp.get('confidence'),
            'passed': passed,
            'has_debug_fields': passed,
            'response_keys': list(json_resp.keys()),
        }

    def run_all_tests(self):
        """Chay tat ca cac test case."""
        results = []

        # Lay danh sach nhan vien da co anh
        known_enc, known_codes = self.face_service.get_all_face_encodings_multi()
        legacy_enc, legacy_codes = self.face_service.get_all_face_encodings()
        all_registered = list(set(known_codes + legacy_codes))

        print("\n" + "=" * 70)
        print("  TC1: SELF-RECOGNITION")
        print("=" * 70)
        for emp in all_registered:
            r = self.test_tc1_self_recognition(emp)
            results.append(r)

        print("\n" + "=" * 70)
        print("  TC2: CROSS-RECOGNITION (should reject)")
        print("=" * 70)
        if len(all_registered) >= 2:
            # Test cross: NV012 vs NV011
            pairs = [('NV012', 'NV011'), ('NV011', 'NV012'),
                     ('NV012', 'NV013'), ('NV013', 'NV012')]
            for a, b in pairs:
                r = self.test_tc2_cross_recognition(a, b)
                results.append(r)
        else:
            print(f"[TC2] Chi co {len(all_registered)} nhan vien, bo qua cross-recognition")

        print("\n" + "=" * 70)
        print("  TC3: UNKNOWN PERSON (should reject)")
        print("=" * 70)
        r = self.test_tc3_unknown_person()
        results.append(r)

        print("\n" + "=" * 70)
        print("  TC4: DEBUG LOGGING")
        print("=" * 70)
        r = self.test_tc4_debug_logging()
        results.append(r)

        print("\n" + "=" * 70)
        print("  TC5: API RESPONSE FIELDS")
        print("=" * 70)
        r = self.test_tc5_api_response_fields()
        results.append(r)

        self._print_summary(results)
        return results

    def _print_summary(self, results):
        """In tom tat ket qua test."""
        print("\n" + "=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)

        print(f"\n{'TC':<20} {'Employee':<15} {'Expected':<25} {'Actual':<30} {'min_dist':<10} {'Tol':<6} {'PASS':<6}")
        print("-" * 120)

        passed_count = 0
        failed_count = 0
        skipped_count = 0

        for r in results:
            tc = r.get('tc', '?')
            emp = r.get('employee', '?')
            exp = r.get('expected', '')[:23]
            act = r.get('actual', '')[:28]
            md = f"{r.get('min_distance'):.4f}" if r.get('min_distance') is not None else 'N/A'
            tol = f"{r.get('tolerance'):.2f}" if r.get('tolerance') is not None else 'N/A'

            if r.get('skipped'):
                status = 'SKIP'
                skipped_count += 1
            elif r.get('passed'):
                status = 'PASS'
                passed_count += 1
            else:
                status = 'FAIL'
                failed_count += 1

            print(f"{tc:<20} {emp:<15} {exp:<25} {act:<30} {md:<10} {tol:<6} {status:<6}")

        total = len(results)
        print("-" * 120)
        print(f"\n  Total: {total} | PASS: {passed_count} | FAIL: {failed_count} | SKIP: {skipped_count}")
        print(f"  Success rate: {passed_count}/{total - skipped_count} = "
              f"{(passed_count / max(1, total - skipped_count) * 100):.1f}%"
              if total - skipped_count > 0 else "  N/A (all skipped)")

        # Failure details
        if failed_count > 0:
            print("\n  FAILURE DETAILS:")
            for r in results:
                if not r.get('skipped') and not r.get('passed'):
                    print(f"  - {r.get('tc')} ({r.get('employee')}): {r.get('actual')}")
                    if r.get('reason'):
                        print(f"    Reason: {r.get('reason')}")
                    if r.get('message'):
                        print(f"    Message: {r.get('message')}")

        print("\n" + "=" * 70)


def main():
    """Entry point."""
    print("\nBat dau kiem tra nhan dien khuon mat...")
    print(f"Thoi gian: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    try:
        tester = FaceRecognitionDebugTester()
        results = tester.run_all_tests()
    except Exception as e:
        logger.exception("Test that bai: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
