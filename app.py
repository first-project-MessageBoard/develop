from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'comment.db')

db = SQLAlchemy(app)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    # post_id = db.Column(db.Integer, ForeignKey('<여기에 post_id>'))
    comment_content = db.Column(db.String, nullable=False)
    comment_writer = db.Column(db.String, nullable=False)
    comment_write_date = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()

# 현재시간
def write_date():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


# 댓글 추가
def comment_add(p_id, content, writer):
    new_comment = Comment(post_id = p_id, comment_content=content, comment_writer=writer, comment_write_date=write_date)
    db.session.add(new_comment)
    db.session.commit()


# 댓글 수정
def comment_update(p_id, c_id, content):
    comment_data = Comment.query.filter_by(
        post_id=p_id, comment_id=c_id).first()
    comment_data.comment_content = content
    comment_data.comment_write_date = write_date
    db.session.add(comment_data)
    db.session.commit()


# 댓글 삭제
def comment_delete(p_id, c_id):
    comment_data = Comment.query.filter_by(
        post_id=p_id, comment_id=c_id).first()
    db.session.delete(comment_data)
    db.session.commit()

