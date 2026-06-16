from run import app, seed_db

if __name__ == '__main__':
    with app.app_context():
        seed_db()
