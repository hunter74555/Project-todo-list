from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Todo
from . import todos_bp

@todos_bp.route('/')
@login_required
def index():
    tasks = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

@todos_bp.route('/add', methods=['POST'])
@login_required
def add():
    task_text = request.form.get("task")
    new_task = Todo(text=task_text, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('todos.index'))

@todos_bp.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    task = Todo.query.get(task_id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('todos.index'))