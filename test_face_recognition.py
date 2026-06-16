"""
Test face recognition - quick diagnostic script
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Employee
from app.services.face_service import FaceService
from app.services.face_detection import FaceDetector
import numpy as np

app = create_app('development')

with app.app_context():
    print("=" * 60)
    print("FACE RECOGNITION DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Check FaceDetector
    print("\n[1] FaceDetector initialization:")
    try:
        detector = FaceDetector()
        print(f"    ✓ FaceDetector created")
        print(f"    Tolerance: {detector.tolerance}")
        print(f"    Model: {detector.model}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 2. Check FaceService
    print("\n[2] FaceService initialization:")
    try:
        face_service = FaceService(db.session)
        print(f"    ✓ FaceService created")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 3. Check employees with face data
    print("\n[3] Employees with legacy face_encoding:")
    employees = Employee.query.filter(Employee.face_encoding.isnot(None)).all()
    print(f"    Found: {len(employees)}")
    for emp in employees:
        print(f"    - {emp.employee_code}: {emp.name}")
    
    # 4. Check face_embeddings table
    print("\n[4] Face embeddings table:")
    try:
        from app.models.face_embedding import FaceEmbedding
        embeddings = FaceEmbedding.query.filter_by(is_active=True).all()
        print(f"    Found: {len(embeddings)} active embeddings")
        for emb in embeddings:
            emb_data = emb.get_embedding()
            shape = emb_data.shape if emb_data is not None else "None"
            print(f"    - ID:{emb.id} {emb.employee_code} (type:{emb.embedding_type}, shape:{shape})")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 5. Test get_all_face_embeddings_multi
    print("\n[5] Testing get_all_face_embeddings_multi():")
    try:
        encodings, codes = face_service.get_all_face_embeddings_multi()
        print(f"    ✓ Retrieved {len(encodings)} embeddings")
        print(f"    Employee codes: {codes}")
        if encodings:
            print(f"    First encoding shape: {encodings[0].shape}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 6. Test get_all_face_encodings (legacy)
    print("\n[6] Testing get_all_face_encodings() (legacy):")
    try:
        encodings, codes = face_service.get_all_face_encodings()
        print(f"    ✓ Retrieved {len(encodings)} embeddings")
        print(f"    Employee codes: {codes}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 7. Test caching
    print("\n[7] Testing cache:")
    from app.services.face_service import _FACE_EMBEDDING_CACHE
    print(f"    Cache encodings: {len(_FACE_EMBEDDING_CACHE['encodings'])}")
    print(f"    Cache codes: {_FACE_EMBEDDING_CACHE['employee_codes']}")
    print(f"    Cache timestamp: {_FACE_EMBEDDING_CACHE['timestamp']}")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
