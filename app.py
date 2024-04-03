from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
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
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_title = db.Column(db.String(100), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    post_created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now())
    post_author = db.Column(db.String(50), nullable=False,
                            default='Anonymous')  # 작성자 열 추가

    def __repr__(self):
        return f'{self.post_id} {self.post_title} {self.post_content}'


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    comment_content = db.Column(db.Text, nullable=False)
    comment_writer = db.Column(db.String(50), nullable=False)
    comment_created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now())


# 테이블 생성
with app.app_context():
    db.create_all()

# 게시판 글 조회


@app.route('/')
def index():
    posts = Post.query.order_by(Post.post_created_at.desc()).all()
    return render_template('index.html', data=posts)

# 글 작성


@app.route('/post', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    author = request.form['author']  # 작성자 정보 가져오기
    new_post = Post(post_title=title, post_content=content,
                    post_author=author)  # 작성자 정보 추가
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('index'))

# 글 작성 페이지로 이동


@app.route('/write')
def write_post():
    return render_template('writing.html')

# 게시글


@app.route('/post/<id>/', methods=['GET', 'POST'])
def post(id):
    # 댓글 조회
    def comments_list(p_id):
        comments = Comment.query.filter_by(post_id=p_id).order_by(
            Comment.comment_created_at.desc()).all()
        return comments

    # 댓글 추가
    def comment_add(p_id, content, writer):
        new_comment = Comment(
            post_id=p_id, comment_content=content, comment_writer=writer)
        db.session.add(new_comment)
        db.session.commit()

    # 댓글 수정
    def comment_update(p_id, c_id, content):
        comment_data = Comment.query.filter_by(
            post_id=p_id, comment_id=c_id).first()
        comment_data.comment_content = content
        db.session.add(comment_data)
        db.session.commit()

    if request.method == "POST":
        comment_content = request.form.get('comment')
        comment_writer = "익명"  # 임시 작성자
        comment_add(id, comment_content, comment_writer)

    post = Post.query.filter_by(post_id=id).first()
    comments = comments_list(id)

    context = {
        "post": post,
        "comments": comments
    }

    return render_template('post.html', data=context)

# 댓글 삭제


@app.route('/post/<p_id>/<c_id>/delete', methods=['GET'])
def comment_delete(p_id, c_id):
    comment_data = Comment.query.filter_by(
        post_id=p_id, comment_id=c_id).first()
    db.session.delete(comment_data)
    db.session.commit()
    print('here')
    return redirect(url_for('post', id=p_id))


# 글 수정
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.post_title = request.form['title']
        post.post_content = request.form['content']
        post.post_author = request.form['author']  # 작성자 정보 업데이트
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


if __name__ == '__main__':
    app.run(debug=True)
