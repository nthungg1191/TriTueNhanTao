#!/usr/bin/env python
"""Test reports route with exception details"""
import traceback
from app import create_app, db
from datetime import date

app = create_app()
app.config['TESTING'] = True

with app.test_client() as client:
    # Login
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    # Access reports with error handling
    try:
        response = client.get('/admin/reports?type=daily')
        print(f"Reports status: {response.status_code}")
        
        if response.status_code != 200:
            # Try to extract error from response
            html = response.get_data(as_text=True)
            if '500' in html:
                print("\n500 Error detected in response")
                # Look for traceback info
                import re
                error_match = re.search(r'<h2>(.*?)</h2>', html)
                if error_match:
                    print(f"Error: {error_match.group(1)}")
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
