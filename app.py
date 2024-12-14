from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime

app = Flask(__name__)


def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='hong',
        database='first_board_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/')
def index():
    search_title = request.args.get('title', '').strip()
    search_author = request.args.get('author', '').strip()
    search_query = request.args.get('search', '').strip()
    connection = get_connection()
    with connection.cursor() as cursor:
        if search_title:
            sql = """
                SELECT id, author, title, create_date  
                FROM board 
                WHERE title LIKE %s
                ORDER BY create_date DESC
            """
            cursor.execute(sql, (f"%{search_title}%",))
        elif search_author:
            sql = """
                SELECT id, author, title, create_date 
                FROM board 
                WHERE author LIKE %s
                ORDER BY create_date DESC
            """
            cursor.execute(sql, (f"%{search_author}%",))
        elif search_query:
            sql = """
                SELECT id, author, title, create_date 
                FROM board 
                WHERE title LIKE %s OR author LIKE %s OR content LIKE %s
                ORDER BY create_date DESC
            """
            search_pattern = f"%{search_query}%"
            cursor.execute(sql, (search_pattern, search_pattern, search_pattern))
        else:
            sql = "SELECT id, author, title, create_date FROM board ORDER BY create_date DESC"
            cursor.execute(sql)

        posts = cursor.fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/board_write.html', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        author = request.form['author']
        title = request.form['title']
        content = request.form['content']
        now = datetime.now()

        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO board (author, title, content, create_date, update_date)
            VALUES (%s, %s, %s, %s, %s)
            """, (author, title, content, now, now))
            connection.commit()
        connection.close()
        return redirect(url_for('index'))
    return render_template('board_write.html')



@app.route('/view/<int:post_id>')
def view(post_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM board WHERE id = %s", (post_id,))
        post = cursor.fetchone()
    connection.close()
    return render_template('view.html', post=post)


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    connection = get_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        now = datetime.now()

        with connection.cursor() as cursor:
            sql = """
            UPDATE board 
            SET title = %s, content = %s, update_date = %s 
            WHERE id = %s
            """
            cursor.execute(sql, (title, content, now, post_id))
            connection.commit()
        connection.close()
        return redirect(url_for('view', post_id=post_id))
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM board WHERE id = %s", (post_id,))
            post = cursor.fetchone()
        connection.close()
        return render_template('edit.html', post=post)

@app.route('/delete/<int:post_id>')
def delete_confirm_page(post_id):

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title FROM board WHERE id = %s", (post_id,))
        post = cursor.fetchone()
    connection.close()
    return render_template('delete.html', post=post)

@app.route('/delete_confirm/<int:post_id>', methods=['POST'])
def delete_post(post_id):

    connection = get_connection()
    with connection.cursor() as cursor:
        sql = "DELETE FROM board WHERE id = %s"
        cursor.execute(sql, (post_id,))
        connection.commit()
    connection.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
