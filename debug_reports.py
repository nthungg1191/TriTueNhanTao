from app import create_app

app = create_app('development')

with app.app_context():
    from app.routes import admin
    from flask import Request
    try:
        with app.test_request_context('/admin/reports'):
            # Call underlying view function to bypass login_required
            result = admin.reports.__wrapped__()
            print('Rendered without exception. Type:', type(result))
    except Exception as e:
        import traceback
        traceback.print_exc()
