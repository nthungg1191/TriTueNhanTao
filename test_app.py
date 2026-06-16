#!/usr/bin/env python3
"""Check if Flask app can import and run without errors."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from app import create_app
    print('Creating app...')
    app = create_app()
    print('App created successfully!')
    
    # Test the attendance route
    with app.test_request_context('/admin/attendance'):
        from app.routes.admin import attendance
        print('Attendance route imported successfully!')
        
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
