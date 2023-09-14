
# אתר אינטרנט שממנו לקחתי את המידע 
# https://www.youtube.com/watch?v=Z1RJmh_OqeA


from multiprocessing import process
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime


app = Flask(__name__)

# Get the current directory of your Python script
#current_directory = os.path.dirname(__file__)

# Define the relative path to your database file within the current directory
db_file = './instance/MySqliteDb.db'
db_connection_string = f'sqlite:///MySqliteDb.db'


if not app.config.get('SQLALCHEMY_DATABASE_URI'):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_string

db = SQLAlchemy(app)

class todoTaskList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable=False) 
    complete = db.Column(db.Integer, default = 0)
    date_created = db.Column(db.DateTime, default = datetime.utcnow )

    def __repr__ (self):
        return f'Task %r' % self.id

print(db_file)

if not os.path.exists(db_file):
    with app.app_context():
        db.create_all()

@app.route('/CreateTask', methods=['POST'])
def create_tasks():
    try:
        # Get the AutoCreateTask parameter from the request
        auto_create = request.args.get('AutoCreateTask', type=bool, default=False)
        if auto_create == True:
            # Check if the database is empty and AutoCreateTask is set to True
            if todoTaskList.query.count() == 0:
                starting_id = 1
            else:
                # Calculate the starting ID based on the highest existing task
                highest_task = todoTaskList.query.order_by(todoTaskList.id.desc()).first()
                if highest_task:
                    starting_id = highest_task.id + 1

                # Create 5 tasks with continuous IDs
                for i in range(starting_id, starting_id + 5):
                    new_task = todoTaskList(id=i, content=f'Task {i}', complete=0)
                    db.session.add(new_task)
                    db.session.commit()

                return jsonify({'message': 'Tasks created successfully'}), 201
        else:
            # Handle the case where AutoCreateTask is False or there are tasks in the database
            # You can proceed with the logic to create tasks from the request data
            data = request.json
            if 'tasks' in data and isinstance(data['tasks'], list):
                for task_info in data['tasks']:
                    new_task = todoTaskList(content=task_info.get('content', ''), complete=task_info.get('complete', 0))
                    db.session.add(new_task)
                    db.session.commit()
                return jsonify({'message': 'Tasks created successfully'}), 201
            else:
                return jsonify({'error': 'Invalid request data'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return 'Hello'
    else:
        if request.method == 'GET':
                    # Retrieve all tasks from the database
            tasks = todoTaskList.query.all()

            # Convert the tasks to a list of dictionaries for JSON response
            #task_dict = {task.id: {'complete': task.complete, 'content': task.content, 'date_created': task.date_created}
             #for task in tasks}
            task_list = [{'id': task.id, 'complete': task.complete, 'content': task.content, 'date_created': task.date_created}
                for task in tasks]

            # Return the list of tasks as JSON
            return jsonify({'tasks': task_list}), 200

            return render_template('index.html')
        

if (__name__ == "__main__"):
    app.run(debug = True, port=8000 )

