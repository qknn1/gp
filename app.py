from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


import pymysql
pymysql.install_as_MySQLdb()
# Initialize Flask app
app = Flask(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

#
# MySQL Configuration - update with your credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/gp?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'staff' or 'it'
    tickets = db.relationship('Ticket', backref='reporter', lazy=True)

class Lab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    computers = db.relationship('Computer', backref='lab', lazy=True)

class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pc_id = db.Column(db.String(20), nullable=False)
    specs = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Working')
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)
    tickets = db.relationship('Ticket', backref='computer', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    resolution = db.Column(db.Text)
    reported_date = db.Column(db.DateTime, default=datetime.utcnow)
    closed_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False)

with app.app_context():
    db.create_all()
    
    if User.query.count() == 0:
        admin = User(username='abdullah', password='123', role='it')
        staff = User(username='fahad', password='098', role='staff')
        db.session.add_all([admin, staff])
        
        lab_a = Lab(name='Computer Lab A')
        lab_b = Lab(name='Computer Lab B')
        db.session.add_all([lab_a, lab_b])
        db.session.commit()
        
        computers_a = [
            Computer(pc_id='PC-A1', specs='i5, 16GB RAM, 512GB SSD', status='Working', lab_id=lab_a.id),
            Computer(pc_id='PC-A2', specs='i7, 32GB RAM, 1TB SSD', status='Working', lab_id=lab_a.id),
            Computer(pc_id='PC-A3', specs='i5, 8GB RAM, 256GB SSD', status='Not Working', lab_id=lab_a.id)
        ]
        
        computers_b = [
            Computer(pc_id='PC-B1', specs='i7, 16GB RAM, 512GB SSD', status='Working', lab_id=lab_b.id),
            Computer(pc_id='PC-B2', specs='i5, 16GB RAM, 512GB SSD', status='Working', lab_id=lab_b.id)
        ]
        
        db.session.add_all(computers_a + computers_b)
        db.session.commit()


with app.app_context():
    db.create_all()
    
    # Add debugging to see if users are created
    user_count = User.query.count()
    print(f"Current user count: {user_count}")
    
    if user_count == 0:
        # Create default users
        admin = User(username='abdullah', password='123', role='it')
        staff = User(username='fahad', password='098', role='staff')
        db.session.add_all([admin, staff])
        db.session.commit()
        
        # Verify users were created
        print(f"After adding users, count: {User.query.count()}")
        print(f"Users: {[u.username for u in User.query.all()]}")


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/check_hash/<username>')
def check_hash(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return f"User {username} not found"
    
    return f"Username: {user.username}, Hash: {user.password}..."  # Show part of the hash for security


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found, checking password")
            print(f"this is the user {user}")
            password_check = True if password == user.password else False
            print(f"Password check result: {password_check}")
            
            if password_check:
                session['user_id'] = user.id
                session['username'] =  user.username
                session['role'] =  user.role
                return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_role = session.get('role')
    
    if user_role == 'staff':
        return redirect(url_for('staff_dashboard'))
    elif user_role == 'it':
        return redirect(url_for('it_dashboard'))
    
    return redirect(url_for('login'))

# Staff Routes
@app.route('/staff')
def staff_dashboard():
    if 'user_id' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))
    
    labs = Lab.query.all()
    return render_template('staff/dashboard.html', labs=labs)

@app.route('/staff/labs/<int:lab_id>')
def staff_view_lab(lab_id):
    if 'user_id' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))
    
    lab = Lab.query.get_or_404(lab_id)
    computers = Computer.query.filter_by(lab_id=lab_id).all()
    return render_template('staff/lab_details.html', lab=lab, computers=computers)

@app.route('/staff/tickets')
def staff_tickets():
    if 'user_id' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    tickets = Ticket.query.filter_by(user_id=user_id).order_by(Ticket.reported_date.desc()).all()
    return render_template('staff/tickets.html', tickets=tickets)

@app.route('/staff/create_ticket/<int:computer_id>', methods=['GET', 'POST'])
def create_ticket(computer_id):
    if 'user_id' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))
    
    computer = Computer.query.get_or_404(computer_id)
    
    if request.method == 'POST':
        issue = request.form.get('issue')
        
        if issue:
            ticket = Ticket(
                issue=issue,
                user_id=session.get('user_id'),
                computer_id=computer.id
            )
            db.session.add(ticket)
            db.session.commit()
            
            flash('Ticket created successfully')
            return redirect(url_for('staff_tickets'))
    
    return render_template('staff/create_ticket.html', computer=computer)

# IT Routes
@app.route('/it')
def it_dashboard():
    if 'user_id' not in session or session.get('role') != 'it':
        return redirect(url_for('login'))
    
    # Count statistics
    open_tickets = Ticket.query.filter_by(status='Open').count()
    closed_tickets = Ticket.query.filter_by(status='Closed').count()
    total_computers = Computer.query.count()
    working_computers = Computer.query.filter_by(status='Working').count()
    
    return render_template('it/dashboard.html', 
                           open_tickets=open_tickets, 
                           closed_tickets=closed_tickets,
                           total_computers=total_computers,
                           working_computers=working_computers)

@app.route('/it/tickets')
def it_tickets():
    if 'user_id' not in session or session.get('role') != 'it':
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter.lower() == 'open':
        tickets = Ticket.query.filter_by(status='Open').order_by(Ticket.reported_date.desc()).all()
    elif status_filter.lower() == 'closed':
        tickets = Ticket.query.filter_by(status='Closed').order_by(Ticket.closed_date.desc()).all()
    else:
        tickets = Ticket.query.order_by(Ticket.reported_date.desc()).all()
    
    return render_template('it/tickets.html', tickets=tickets, current_filter=status_filter)

@app.route('/it/resolve_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def resolve_ticket(ticket_id):
    if 'user_id' not in session or session.get('role') != 'it':
        return redirect(url_for('login'))
    
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if request.method == 'POST':
        resolution = request.form.get('resolution')
        
        if resolution:
            ticket.status = 'Closed'
            ticket.resolution = resolution
            ticket.closed_date = datetime.utcnow()
            db.session.commit()
            
            flash('Ticket resolved successfully')
            return redirect(url_for('it_tickets'))
    
    return render_template('it/resolve_ticket.html', ticket=ticket)

@app.route('/it/labs')
def it_labs():
    if 'user_id' not in session or session.get('role') != 'it':
        return redirect(url_for('login'))
    
    labs = Lab.query.all()
    return render_template('it/labs.html', labs=labs)

@app.route('/it/lab/<int:lab_id>')
def it_lab_details(lab_id):
    if 'user_id' not in session or session.get('role') != 'it':
        return redirect(url_for('login'))
    
    lab = Lab.query.get_or_404(lab_id)
    computers = Computer.query.filter_by(lab_id=lab_id).all()
    return render_template('it/lab_details.html', lab=lab, computers=computers)

if __name__ == '__main__':
    app.run(debug=True)