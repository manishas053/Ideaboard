from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #records the time of the signing and can be used to expire signatures
from flask import current_app
from ideaboard import db, login_manager, app
from flask_login import UserMixin

''' for reloading the user from the user id stored in the session, for extension to work(from extensions website) '''
@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))


''' Database structure for a user '''

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)   # primary key - unique id for our user
    username = db.Column(db.String(20), unique=True, nullable=False)  #cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)  #has relationship with Post model, backref is similar to adding
                                                                  #a column in Post model
    #comment = db.relationship('Comment', backref='article_1', lazy=True)
    likes = db.relationship('PostLike', foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')
    dislikes = db.relationship('PostDislike', foreign_keys='PostDislike.user_id',
                            backref='user3', lazy='dynamic')
    approves = db.relationship('PostApprove', foreign_keys='PostApprove.user_id',
                            backref='user1', lazy='dynamic')
    rejects = db.relationship('PostReject', foreign_keys='PostReject.user_id',
                               backref='user2', lazy='dynamic')

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id, PostLike.post_id == post.id).count() > 0


    def dislike_post(self, post):
        if not self.has_disliked_post(post):
            dislike = PostDislike(user_id=self.id, post_id=post.id)
            db.session.add(dislike)

    def undislike_post(self, post):
        if self.has_disliked_post(post):
            PostDislike.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_disliked_post(self, post):
        return PostDislike.query.filter(PostDislike.user_id == self.id, PostDislike.post_id == post.id).count() > 0


    def approve_post(self, post):
        if not self.has_approved_post(post):
            approve = PostApprove(user_id=self.id, post_id=post.id)
            db.session.add(approve)

    def has_approved_post(self, post):
        return PostApprove.query.filter(PostApprove.user_id == self.id, PostApprove.post_id == post.id).count() > 0

    def reject_post(self, post):
        if not self.has_rejected_post(post):
            reject = PostReject(user_id=self.id, post_id=post.id)
            db.session.add(reject)

    def has_rejected_post(self, post):
        return PostReject.query.filter(PostReject.user_id == self.id, PostReject.post_id == post.id).count() > 0


    def get_reset_token(self, expires_sec=1800):                #Login expires after 30 mins
        #s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        #s = Serializer(current_app.config['SECRET_KEY'])
        s = Serializer(app.config['SECRET_KEY'])
        '''
            we could get exception when we try to load this token,
            token could be invalid or time could have expired,
            so put in try except
        '''
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"  #how our user object is printed whenever we print it out


''' Database structure for a post/idea '''
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    effort_required = db.Column(db.Text, nullable=False)
    business_value = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.relationship('Comment', backref='article', lazy=True)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    dislikes = db.relationship('PostDislike', backref='post3', lazy='dynamic')
    approves = db.relationship('PostApprove', backref='post1', lazy='dynamic')
    rejects = db.relationship('PostReject', backref='post2', lazy='dynamic')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


''' Database structure for a comment '''
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.comment}', '{self.username}', '{self.date_posted}')"


''' Database structure for like '''
class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


''' Database structure for dislike '''
class PostDislike(db.Model):
    __tablename__ = 'post_dislike'
    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


''' Database for Approve '''
class PostApprove(db.Model):
    __tablename__ = 'post_approve'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

''' Database for Approve '''
class PostReject(db.Model):
    __tablename__ = 'post_reject'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

'''
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        #return '<Post %r>' % (self.body)
        return f"Post('{self.body}', '{self.date_posted}')"
'''
'''class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    author = db.Column(db.String(32))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)'''