#!/usr/bin/env python
"""Test reports functionality"""
from app import create_app, db
from datetime import date
from flask import render_template_string

app = create_app()
with app.app_context():
    from app.services.reports_service import ReportsService
    
    # Test get_daily_report
    report = ReportsService.get_daily_report(date.today())
    print('✓ get_daily_report works')
    
    if report.get('attendances'):
        att = report['attendances'][0]
        print(f'✓ First attendance keys: {list(att.keys())}')
    else:
        print('✓ No attendances today')
    
    # Now test template rendering
    try:
        template_string = """
        {% for att in attendances[:2] %}
        <tr>
            <td>{{ att.working_hours_display }}</td>
        </tr>
        {% endfor %}
        """
        result = render_template_string(template_string, attendances=report.get('attendances', []))
        print('✓ Template rendering works')
    except Exception as e:
        print(f'✗ Template error: {e}')
        import traceback
        traceback.print_exc()
