from app import create_app
from app.models import User
from app.routes.employee import dashboard
from flask_login import login_user

app = create_app('development')

with app.app_context():
    user = User.query.filter_by(username='EMP001', role='employee').first()
    print('user', user.username if user else None)
    with app.test_request_context('/employee/dashboard'):
        login_user(user)
        try:
            response = dashboard()
            print('dashboard response type', type(response))
            if hasattr(response, 'data'):
                print(response.data[:1000])
            else:
                print(response)
        except Exception as e:
            import traceback
            traceback.print_exc()
