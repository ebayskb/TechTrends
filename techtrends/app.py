import sqlite3
import logging
from datetime import datetime

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count +=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      log(message="Article Not Found")
      return render_template('404.html'), 404
    else:
      log(message=f"Article {post['title']} found")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    log(message="About Us")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            log(f"Article {title} created")
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute('select id from posts')
        connection.close()
        return dict(result = 'OK - healthy')
    except Exception:
        return dict(result = 'Error - unhealthy'), 500
    
@app.route('/metrics')
def metrics():
    try:
        connection = get_db_connection()
        counts = connection.execute('select count(id) from posts').fetchone()[0]
        connection.close()
        return dict(post_count = counts, db_connection_count = connection_count)
    except Exception:
        return dict(result = 'Error - unhealthy'), 500

def log(message):
    date = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    app.logger.info(f'{date} - {message}')

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
