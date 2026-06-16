#!/usr/bin/env python
"""Test reports route rendering"""
from app import create_app, db
from app.models import User
from datetime import date
import sys

app = create_app()

# Create test user if needed
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Admin not found")
        sys.exit(1)

# Test the route
with app.test_client() as client:
    # Login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    print(f"Login status: {response.status_code}")
    
    # Access reports
    response = client.get('/admin/reports?type=daily')
    print(f"Reports status: {response.status_code}")
    
    if response.status_code != 200:
        print("Error response:")
        print(response.get_data(as_text=True)[:1000])
