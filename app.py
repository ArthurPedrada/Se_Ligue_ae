from flask import Flask, render_template, request, redirect, url_for, abort
from models import db, Event, User
from config import Config
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "segredo"

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user:
            error = "Já existe um usuário com este email."
            return render_template('register.html', error=error)

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )

        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))

    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/')
        else:
            error = 'Email ou senha incorretos.'

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/')
@login_required
def agenda():
    events = Event.query.filter_by(user_id=current_user.id)\
                        .order_by(Event.date, Event.time).all()

    hoje = datetime.today().date()
    
    return render_template('agenda.html', events=events, hoje=hoje)


@app.route('/create', methods=['POST'])
@login_required
def create():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    date_str = request.form.get('date', '').strip()
    time_str = request.form.get('time', '').strip()

    error = None
    hoje = datetime.today().date()

    if not title or not description or not date_str or not time_str:
        error = "Todos os campos são obrigatórios."
        events = Event.query.filter_by(user_id=current_user.id)\
                            .order_by(Event.date, Event.time).all()
        return render_template('agenda.html', events=events, hoje=hoje, error=error)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M').time()
        
        
        novo_evento = Event(
            title=title, 
            description=description, 
            date=date, 
            time=time, 
            user_id=current_user.id
        )
        db.session.add(novo_evento)
        db.session.commit()
        return redirect('/')

    except ValueError:
        error = "Data ou hora inválida."
        events = Event.query.filter_by(user_id=current_user.id)\
                            .order_by(Event.date, Event.time).all()
        return render_template('agenda.html', events=events, hoje=hoje, error=error)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    
    event = Event.query.get_or_404(id)

    if event.user_id != current_user.id:
        abort(403)

    db.session.delete(event)
    db.session.commit()

    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    event = Event.query.get_or_404(id)
    
    
    if event.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        error = None

        if not title or not description or not date_str or not time_str:
            error = "Todos os campos são obrigatórios."
            return render_template('edit_event.html', event=event, error=error)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
            
            
            event.title = title
            event.description = description
            event.date = date
            event.time = time

            db.session.commit()
            return redirect('/')
        except ValueError:
            error = "Data ou hora inválida."
            return render_template('edit_event.html', event=event, error=error)

   
    return render_template('edit_event.html', event=event)


with app.app_context():
    db.create_all()


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    
    
    app.run(host="0.0.0.0", port=port, debug=True)