from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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
                            default='Anonymous')

    # 댓글 수를 세는 메서드
    @property
    def comment_count(self):
        return Comment.query.filter_by(post_id=self.post_id).count()


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    comment_content = db.Column(db.Text, nullable=False)
    comment_writer = db.Column(db.String(50), nullable=False)
    comment_created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now())


class User(db.Model):
    user_id = db.Column(db.String(20), primary_key=True, nullable=False)
    user_pw = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)


# 테이블 생성
with app.app_context():
    db.create_all()

login_user_name = '익명'

# 게시판 글 조회


@app.route('/')
def index():
    posts = Post.query.order_by(Post.post_created_at.desc()).all()
    return render_template('index.html', data=posts)

# 글 작성


@app.route('/post', methods=['POST'])
def create_post():
    title = request.form['title']
    content = request.form['content']
    author = request.form.get('author', login_user_name)
    new_post = Post(post_title=title, post_content=content, post_author=author)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('index'))

# 글 작성 페이지로 이동


@app.route('/writing.html')
def write_post():
    return render_template('writing.html')


# 게시글
@app.route('/post/<int:id>/', methods=['GET', 'POST'])
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

    if request.method == "POST":
        comment_content = request.form.get('comment')
        comment_writer = login_user_name
        comment_add(id, comment_content, comment_writer)

    post = Post.query.filter_by(post_id=id).first()
    comments = comments_list(id)

    # 댓글 수 계산
    comment_count = len(comments)

    context = {
        "post": post,
        "comments": comments,
        "comment_count": comment_count,
        "login_user_name": login_user_name
    }

    return render_template('post.html', data=context)


# 댓글 수정


@app.route('/post/<p_id>/<c_id>/edit', methods=['GET', 'POST'])
def comment_update(p_id, c_id):
    if request.method == "POST":
        new_content = request.form.get('comment-edit-content')
        comment_data = Comment.query.filter_by(
            post_id=p_id, comment_id=c_id).first()
        comment_data.comment_content = new_content
        db.session.add(comment_data)
        db.session.commit()
        return redirect(url_for('post', id=p_id))

# 댓글 삭제


@app.route('/post/<p_id>/<c_id>/delete', methods=['GET', 'POST'])
def comment_delete(p_id, c_id):
    comment_data = Comment.query.filter_by(
        post_id=p_id, comment_id=c_id).first()
    db.session.delete(comment_data)
    db.session.commit()
    return redirect(url_for('post', id=p_id))


# 글 수정 페이지로 이동


@app.route('/edit/<int:id>', methods=['GET'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    return render_template('edit.html', post=post, is_edit=True)

# 글 수정


@app.route('/edit/<int:id>', methods=['POST'])
def edit_post_submit(id):
    post = Post.query.get_or_404(id)
    post.post_title = request.form['title']
    post.post_content = request.form['content']
    db.session.commit()
    return redirect(url_for('index'))

# 글 삭제


@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


# 로그인 페이지 렌더링
@app.route('/login.html')
def render_login():
    return render_template('login.html')

# 로그인 처리


@app.route('/login', methods=['POST'])
def login_post():
    id = request.form['id']  # 폼에서 ID를 받아옴
    password = request.form['password']

    # ID를 기반으로 사용자 조회
    user = User.query.filter_by(user_id=id).first()
    if user and user.user_pw == password:  # 비밀번호를 평문으로 비교
        # 사용자가 존재하고 비밀번호가 일치할 경우 로그인 성공
        # 로그인 성공 후 index 페이지로 리다이렉트하며 성공 메시지 전달
        global user_name
        user_name = user.user_name
        return redirect(url_for('index', success="로그인 성공!"))
    else:
        # 로그인 실패
        return render_template('login.html', error="ID 또는 비밀번호가 잘못되었습니다.")


# 회원가입 성공
@app.route('/register/success', methods=['POST'])
def register_user():
    if request.method == "POST":
        user_name = request.form.get('username')
        user_id = request.form.get('id')
        user_pw = request.form.get('password')
        new_user = User(
            user_name=user_name, user_id=user_id, user_pw=user_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))  # 회원가입 후 메인 게시판으로 리다이렉트


# 회원가입 페이지


@app.route('/register')
def register():
    user_data = User.query.all()
    return render_template('submit.html', data=user_data)

# ID중복체크


@app.route('/register/check/id', methods=['POST'])
def check_id():
    input_data = request.json['data']
    data = User.query.filter_by(user_id=input_data).first()
    print(data)
    exists = data is not None
    return jsonify({'exists': exists})

# 닉네임 중복체크


@app.route('/register/check/name', methods=['POST'])
def check_name():
    input_data = request.json['data']
    data = User.query.filter_by(user_name=input_data).first()
    exists = data is not None
    return jsonify({'exists': exists})


# 오래된 순으로 정렬
@app.route('/oldest')
def oldest():
    posts = Post.query.order_by(Post.post_created_at).all()
    return render_template('index.html', data=posts)

# 댓글 많은 순으로 정렬


@app.route('/most_comments')
def most_comments():
    posts = Post.query.all()
    posts.sort(key=lambda post: post.comment_count, reverse=True)
    return render_template('index.html', data=posts)

# 댓글 적은 순으로 정렬


@app.route('/least_comments')
def least_comments():
    posts = Post.query.all()
    posts.sort(key=lambda post: post.comment_count)
    return render_template('index.html', data=posts)


if __name__ == '__main__':
    app.run(debug=True)
