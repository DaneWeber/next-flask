from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/daily_updates')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Models
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    updates = db.relationship('Update', backref='person', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    updates = db.relationship('Update', backref='project', lazy=True)

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    summary_type = db.Column(db.String(20), nullable=False)  # 'person' or 'project'
    reference_id = db.Column(db.Integer, nullable=False)  # person_id or project_id
    date_range_start = db.Column(db.Date, nullable=False)
    date_range_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Daily Updates API'})

@app.route('/api/updates', methods=['GET', 'POST'])
def updates():
    if request.method == 'GET':
        updates = Update.query.all()
        return jsonify([{
            'id': update.id,
            'content': update.content,
            'date': update.date.isoformat(),
            'person': update.person.name,
            'project': update.project.name if update.project else None
        } for update in updates])
    
    elif request.method == 'POST':
        data = request.get_json()
        update = Update(
            content=data['content'],
            person_id=data['person_id'],
            project_id=data.get('project_id')
        )
        db.session.add(update)
        db.session.commit()
        return jsonify({'id': update.id, 'message': 'Update created successfully'}), 201

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([{
        'id': project.id,
        'name': project.name,
        'description': project.description
    } for project in projects])

@app.route('/api/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    return jsonify([{
        'id': person.id,
        'name': person.name,
        'email': person.email
    } for person in people])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)