from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL 연결 설정
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Jinwon'
app.config['MYSQL_PASSWORD'] = 'jin7254'
app.config['MYSQL_DB'] = 'Jinwon'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

# 게시판 글 조회
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = cur.fetchall()
    cur.close()
    return render_template('index.html', posts=posts)

# 글 작성


@app.route('/post', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO posts (title, content) VALUES (%s, %s)", (title, content))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# 글 수정


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cur.execute(
            "UPDATE posts SET title = %s, content = %s WHERE id = %s", (title, content, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    else:
        cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
        post = cur.fetchone()
        cur.close()
        return render_template('edit.html', post=post)

# 글 삭제
@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)