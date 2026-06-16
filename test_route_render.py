#!/usr/bin/env python3
"""Test the full attendance route including template rendering."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app

app = create_app()

try:
    with app.test_client() as client:
        print('Making request to /admin/attendance...')
        response = client.get('/admin/attendance')
        
        print(f'Status code: {response.status_code}')
        
        if response.status_code == 200:
            print('✓ Attendance page loaded successfully!')
            
            # Check if the response contains expected content
            html = response.get_data(as_text=True)
            
            if 'Phạm Thị Thảo' in html or 'Nguyễn' in html or 'chấm công' in html:
                print('✓ Template rendered with employee data!')
            else:
                print('⚠ Template rendered but missing expected content')
                
        elif response.status_code == 302:
            print('⚠ Redirect (probably to login)')
        else:
            print(f'✗ Error: {response.status_code}')
            print(response.get_data(as_text=True)[:500])
            
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
