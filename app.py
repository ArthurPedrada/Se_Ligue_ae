from flask import Flask, render_template, request, redirect
from models import db, Event
from config import Config
from datetime import datetime 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

# 🔹 LISTAR
@app.route('/')
def agenda():
    events = Event.query.order_by(Event.date, Event.time).all()
    return render_template('agenda.html', events=events)

# 🔹 CRIAR
@app.route('/create', methods=['POST'])
def create():
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    time = datetime.strptime(request.form['time'], '%H:%M').time()

    event = Event(
        title=request.form['title'],
        description=request.form['description'],
        date=date,
        time=time
    )

    db.session.add(event)
    db.session.commit()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)