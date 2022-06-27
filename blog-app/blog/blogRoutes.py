from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Post, Like, User, Comment
from . import db
from datetime import datetime
from sqlalchemy import desc
import nltk
from nltk.corpus import stopwords
from collections import Counter

blogRoutes = Blueprint("blogRoutes", __name__)


@blogRoutes.route("/profile")
@login_required
def profile():
    top5posts = db.session.query(Post).filter(
        Post.userid == current_user.id).order_by(desc(Post.created_date)).limit(5).all()
    for row in top5posts:
        latest_date = row.modified_date if row.modified_date else row.created_date
        current_date = datetime.now()
        diff = current_date - latest_date
        row.num_of_days = diff.days

    top5comments = db.session.query(Comment).filter(
        Comment.userid == current_user.id).order_by(desc(Comment.created_date)).limit(5).all()
    for row in top5comments:
        latest_date = row.modified_date if row.modified_date else row.created_date
        current_date = datetime.now()
        diff = current_date - latest_date
        row.num_of_days = diff.days
    return render_template("profile.html", top5posts=top5posts, top5comments=top5comments)


@blogRoutes.route("/createPost", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("content")
        post_userid = current_user.id

        new_post = Post(userid=post_userid, title=title,
                        content=content)

        db.session.add(new_post)
        db.session.commit()
        flash('Post created!')

        return redirect(url_for('blogRoutes.profile'))

    return render_template("createPost.html")


@blogRoutes.route("/")
@blogRoutes.route("/allposts", methods=['GET', 'POST'])
def all_posts():
    posts = db.session.query(Post).all()
    for row in posts:
        latest_date = row.modified_date if row.modified_date else row.created_date
        current_date = datetime.now()
        diff = current_date - latest_date
        row.num_of_days = diff.days

    return render_template("allposts.html", posts=posts, page="All Posts")


@blogRoutes.route("/post/<id>", methods=['GET', 'POST'])
def post(id):
    post = db.session.query(Post).filter(Post.id == id).first()
    liked = None
    if current_user.is_authenticated:
        presence = db.session.query(Like).filter(
            Like.postid == id, Like.userid == current_user.id).first()
        if presence:
            liked = 1
    post.liked = liked
    text = post.content
    text = list(map(str.strip, text.strip().split()))
    sw = stopwords.words('english')
    text = [w for w in text if not w.lower() in sw]
    ids = []
    for word in text:
        searched_post = db.session.query(Post).filter(
            Post.title.like('%'+word+'%')).all()
        ids += [p.id for p in searched_post]
    postid_count = Counter(ids)
    postid_count = list(tuple(zip(postid_count.keys(), postid_count.values())))
    postid_count.sort(key=lambda x: -x[1])
    postid_count = [x[0] for x in postid_count]
    print("----->",postid_count)
    if int(id) in postid_count:
        postid_count.remove(int(id))
    searched_post = db.session.query(Post).filter(
        Post.id.in_(postid_count)).limit(5).all()

    return render_template("post.html", post=post, likecount=len(post.like), suggest=searched_post)


@blogRoutes.route("/like/<id>", methods=['GET'])
@login_required
def like(id):
    presence = db.session.query(Like).filter(
        Like.postid == id, Like.userid == current_user.id).first()
    if not presence:
        like = Like(userid=current_user.id, postid=id)
        db.session.add(like)
        db.session.commit()
        flash('Liked!')
    else:
        db.session.delete(presence)
        db.session.commit()
        flash('Disliked!')
    return redirect(url_for('blogRoutes.post', id=id))


@blogRoutes.route("/comment/<id>", methods=['POST'])
@login_required
def addcomment(id):
    comment = request.form.get("comment")
    newcomment = Comment(comment=comment, userid=current_user.id, postid=id)
    db.session.add(newcomment)
    db.session.commit()
    flash('Comment added!')
    return redirect(url_for('blogRoutes.post', id=id))


@blogRoutes.route("/comment/<id>/delete", methods=['POST'])
@login_required
def deletecomment(id):
    comment = db.session.query(Comment).filter(Comment.id == id).first()
    db.session.delete(comment)
    db.session.commit()
    flash('Comment Deleted!')
    return redirect(url_for('blogRoutes.post', id=comment.postid))


@blogRoutes.route("/post/<id>/delete", methods=['POST'])
@login_required
def deletepost(id):
    comment = db.session.query(Post).filter(Post.id == id).first()
    db.session.delete(comment)
    db.session.commit()
    flash('Post Deleted!')
    return redirect(url_for('blogRoutes.all_posts'))


@blogRoutes.route("/post/<id>/edit", methods=['GET', 'POST'])
@login_required
def editpost(id):
    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("content")
        post_userid = current_user.id

        db.session.query(Post).filter(Post.id == id).update(
            {'title': title, 'content': content})
        db.session.commit()
        flash('Post Edited!')
        return redirect(url_for('blogRoutes.post', id=id))

    post = db.session.query(Post).filter(Post.id == id).first()
    return render_template("editPost.html", post=post)


@blogRoutes.route("/post/search", methods=['GET', 'POST'])
def search():
    maintext = request.form.get("search")
    text = maintext
    if text is None or len(text) == 0:
        flash('Enter Search Text', category='error')
        return redirect(url_for('blogRoutes.all_posts'))
    text = list(map(str.strip, text.strip().split()))
    sw = stopwords.words('english')
    text = [w for w in text if not w.lower() in sw]
    ids = []
    for word in text:
        searched_post = db.session.query(Post).filter(
            Post.title.like('%'+word+'%')).all()
        ids += [p.id for p in searched_post]
    postid_count = Counter(ids)
    postid_count = list(tuple(zip(postid_count.keys(), postid_count.values())))
    postid_count.sort(key=lambda x: -x[1])
    postid_count = [x[0] for x in postid_count]
    searched_post = db.session.query(Post).filter(
        Post.id.in_(postid_count)).all()
    for row in searched_post:
        latest_date = row.modified_date if row.modified_date else row.created_date
        current_date = datetime.now()
        diff = current_date - latest_date
        row.num_of_days = diff.days

    return render_template("allposts.html", posts=searched_post, page="Search Results for '"+maintext+"'")


@blogRoutes.route("/about")
def about():
    return render_template("about.html")

@blogRoutes.route("/contact")
def contact():
    return render_template("contact.html")