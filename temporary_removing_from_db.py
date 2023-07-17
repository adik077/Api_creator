from app import app, db, User

with app.app_context():
    task_to_remove = db.session.query(User).get_or_404(2)
    db.session.delete(task_to_remove)
    db.session.commit()
