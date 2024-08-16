import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

# Configuração inicial
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('danielly.nakano@aluno.ifsp.edu.br')  # Use a variável de ambiente para o usuário
app.config['MAIL_PASSWORD'] = os.getenv('Euamoorafa071019@')  # Use a variável de ambiente para a senha
app.config['FLASKY_ADMIN'] = os.getenv('flaskaulasweb@zohomail.com')  # E-mail do administrador
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = app.config['MAIL_USERNAME']  # O mesmo do 'MAIL_USERNAME'

mail = Mail(app)

def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox0d2fdb35f8bb4ba797d1e6b2c23288db.mailgun.org/messages",
  		auth=("api", "3fe75aa0470a64709935c1386155ee82-911539ec-03c25f91"),
  		data={"from": "danielly.nakano@zohomail.com",
  			"to": ["flaskaulasweb@zohomail.com", "danielly.nakano@zohomail.com"],
  			"subject": "Hello",
  			"text": "Testing some Mailgun awesomeness!"})

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name='User').first()
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            # Enviar e-mail para o administrador, se configurado
            if app.config['FLASKY_ADMIN']:
                send_email(
                    app.config['FLASKY_ADMIN'],  # E-mail do administrador
                    'New User',                 # Assunto do e-mail
                    'mail/new_user',            # Template do e-mail
                    user=user                   # Dados adicionais para o template
                )
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    try:
        mail.send(msg)
        print(f"Email sent to {to} successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")



# mail = Mail(app)

# app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
# app.config['FLASKY_MAIL_SENDER'] = 'danielly.nakano@zohomail.com'

# def send_email(to,subject,template, **kwargs):
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
#                 sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.html = render_template(template + '.html', **kwargs)
#     mail.send(msg)


# # app.config['MAIL_SERVER'] = 'smtp.zoho.com'
# # app.config['MAIL_PORT'] = 587
# # app.config['MAIL_USE_TLS'] = True
# # app.config['MAIL_USERNAME'] = os.environ.get('danielly.nakano@zohomail.com')
# # app.config['MAIL_PASSWORD'] = os.environ.get('Rafa071019@')
# # app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
# # app.config['FLASKY_MAIL_SENDER'] = 'danielly.nakano@zohomail.com'

# def send_email(to,subject,template, **kwargs):
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
#                 sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.html = render_template(template + '.html', **kwargs)
#     mail.send(msg)
