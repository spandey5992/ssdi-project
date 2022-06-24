from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)

    email = db.Column(db.String(45), unique=False, nullable=False)

    firstname = db.Column(db.String(45), unique=False, nullable=True)
    lastname = db.Column(db.String(45), unique=False, nullable=True)

    bio = db.Column(db.String(300), unique=False, nullable=True)

    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_date = db.Column(db.DateTime(timezone=True), nullable=True)

    password = db.Column(db.String(150))


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    postid = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint(
        'userid', 'postid', name='postlikeuc'),)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    postid = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    comment = db.Column(db.String(300), unique=False, nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_date = db.Column(db.DateTime(timezone=True), nullable=True)

    user = relationship(User, load_on_pending=True)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), unique=False, nullable=False)
    content = db.Column(db.Text, unique=False, nullable=False)

    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_date = db.Column(db.DateTime(timezone=True), nullable=True)
    user = relationship(User, load_on_pending=True)
    like = relationship(Like, backref="post", cascade="delete")
    comment = relationship(Comment, backref="post",
                           order_by='Comment.created_date.desc()', cascade="delete")
