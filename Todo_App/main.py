from flask import Flask, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from db import todo_collection
from bson import ObjectId

app = Flask(__name__)
bootstrap = Bootstrap(app)

# HOME
@app.route('/')
def index():
    todos = list(todo_collection.find())
    return render_template('index.html', todos=todos)

# ADD
@app.route('/add', methods=['POST'])
def add():
    task = request.form['todo']
    todo_collection.insert_one({
        "task": task,
        "done": False
    })
    return redirect(url_for('index'))

# DELETE ✅ FIXED
@app.route('/remove/<id>')
def remove(id):
    todo_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

# EDIT ✅ FIXED
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        todo = todo_collection.find_one({"_id": ObjectId(id)})
        return render_template('edit.html', todo=todo)
    else:
        task = request.form['todo']
        todo_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"task": task}}
        )
        return redirect(url_for('index'))

# REQUIRED for VS Code debugging
if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
