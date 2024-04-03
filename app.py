from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# 연결 설정
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'post.db')

# SQLAlchemy 초기화
db = SQLAlchemy(app)


# 모델 정의
class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(100), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    post_created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now())
    post_author = db.Column(db.String(50), nullable=False,
                            default='Anonymous')


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, nullable=False)
    comment_content = db.Column(db.String, nullable=False)
    comment_writer = db.Column(db.String, nullable=False)
    comment_write_date = db.Column(db.DateTime, nullable=False,
                                default=db.func.now())


# 테이블 생성
with app.app_context():
    db.create_all()


# 게시판 글 조회
@app.route('/')
def index():
    image_url = "https://postfiles.pstatic.net/MjAyNDA0MDJfMjA0/MDAxNzEyMDUzNTg2MzA4.bBTRt6qjNaELTNrH9sOoF14WWyarzjSCQ1fmgWObFVgg.cLeRNAaZEJjN9Dqhx-oN0DJeIlNIQ6cfwhngGlGLQMYg.PNG/%EC%8A%A4%ED%8C%8C%EB%A5%B4%ED%83%80%EC%9E%84_%EB%A1%9C%EA%B3%A0.png?type=w966"
    posts = Post.query.order_by(Post.post_created_at.desc()).all()
    print(posts)
    return render_template('index.html', image_url=image_url, posts=posts)


# 글 작성
@app.route('/post', methods=['POST'])
def create_post():
    title = request.form['title']
    content = request.form['content']
    author = request.form.get('author', 'Anonymous')
    new_post = Post(post_title=title, post_content=content, post_author=author)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/post/<int:id>')
def view_post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/writing.html')
def writing():
    return render_template('writing.html')


# 글 수정
@app.route('/edit/<int:id>', methods=['POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.post_title = request.form['title']
        post.post_content = request.form['content']
        post.post_author = request.form['author']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', post=post)


# 글 삭제
@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


# 댓글 추가
@app.route('/comment/<int:id>', methods=['POST'])
def add_comment(id):
    content = request.form['comment']
    writer = request.form.get('writer', 'Anonymous')
    new_comment = Comment(post_id=id, comment_content=content,
                          comment_writer=writer, comment_write_date=datetime.now())
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('view_post', id=id))


# 댓글 수정
@app.route('/comment/<int:id>/edit', methods=['POST'])
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    if request.method == 'POST':
        comment.comment_content = request.form['comment']
        comment.comment_write_date = datetime.now()
        db.session.commit()
        return redirect(url_for('view_post', id=comment.post_id))
    return render_template('edit_comment.html', comment=comment)


# 댓글 삭제
@app.route('/comment/<int:id>/delete', methods=['POST'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('view_post', id=post_id))


# 정적 파일(css) 제공
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)


if __name__ == '__main__':
    app.run(debug=True)
