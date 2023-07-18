from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, UserMixin, current_user, LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from Forms import CreateApiForm, RegisterUserForm, LoginUserForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
app.config['SECRET_KEY'] = 'secretKEY123'
db = SQLAlchemy(app)
migration = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET'])
def main():
    return render_template('greeting_page.html')


@app.route('/add_api', methods=['GET', 'POST'])
@login_required
def add_api():
    form = CreateApiForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            api_body = form.api_body.data
            author = current_user.id
            description = form.description.data
            new_api = CreateApi(api_body=api_body, author=author, description=description)
            try:
                db.session.add(new_api)
                db.session.commit()
            except Exception:
                flash('Problem with connection with database, please try later...', 'error')
                return redirect(url_for('add_api'))
            flash('Api added successfully...')
            return redirect(url_for('add_api'))
    else:
        return render_template('create_api.html', form=form)


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    users_endpoints = CreateApi.query.filter_by(author=current_user.id)
    return render_template('dashboard.html', users_endpoints=users_endpoints)


@app.route('/endpoint/<int:endpoint_id>', methods=['GET'])
def return_api_endpoint(endpoint_id):
    endpoint = CreateApi.query.filter_by(id=endpoint_id).first()
    return endpoint.api_body if endpoint is not None else 'Could not find endpoint...'


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_user_mail = User.query.filter_by(mail=form.mail.data).first()
            existing_user_login = User.query.filter_by(login=form.login.data).first()
            if existing_user_mail is None and existing_user_login is None:
                user = User(name=form.name.data, surname=form.surname.data, mail=form.mail.data, login=form.login.data,
                            password=form.password.data)
                try:
                    db.session.add(user)
                    db.session.commit()
                except Exception:
                    flash('Problem with connection with database, please try later...', 'error')
                    return redirect(url_for('add_api'))
                flash('User created successfully...')
                return redirect(url_for('add_api'))
            else:
                flash('User with entered mail or login already exists......', 'error')
                return redirect(url_for('register_user'))
    else:
        return render_template('register_user.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(login=form.login.data).first()
            user_password = form.password.data
            if user is not None and user.verify_password(user_password):
                login_user(user)
                return redirect(url_for('dashboard'))
    else:
        return render_template('login_user.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash("You were logged out successfully...")
    return redirect(url_for('login'))


# Models Creation
class CreateApi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_body = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    added_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f'{self.id} - {self.author}'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=False, unique=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    user_apis = db.relationship('CreateApi', backref='api')

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'{self.login} - {self.mail}'


if __name__ == '__main__':
    app.run(debug=True)
