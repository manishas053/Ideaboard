from flask import render_template, url_for, flash, redirect, request, abort
from ideaboard import app, db, bcrypt, mail
from ideaboard.forms import (RegistrationForm, LoginForm,
                             PostForm, AddCommentForm)
from ideaboard.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


'''In home page, displays posts in order 5 per page'''
@app.route("/")                      # route function is a decorator, used to bind URL to a function, / -> root page
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)        # .get() is a method of the dict class, by default shows page 1
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) # shows 5 posts per page in desc ord
    #p.likes.count()
    return render_template('home.html', posts=posts)   # search for home.html in templates folder and renders


'''About page, go to templates folder and renders about.html '''
@app.route("/about")
def about():
    home = url_for('static', filename='pics/' + 'home.png')
    submit_idea = url_for('static', filename='pics/' + 'submit_idea.png') #url_for finds the exact location of route for us
    idea = url_for('static', filename='pics/' + 'idea.png')
    submitted_idea = url_for('static', filename='pics/'+'idea_created.png')
    update = url_for('static', filename='pics/'+'update.png')
    return render_template('about.html', title='About', home=home, submit_idea=submit_idea, idea=idea, submitted_idea=submitted_idea, update=update)


''' Registers a new user, renders the html file and takes the inputs from user and store them in db '''
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:      # If user already registered and logged in, goes to home page
        return redirect(url_for('home'))
    form = RegistrationForm()  # creates instance of Registration form
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # to get string instead of byte
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)          # stores new user to database
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


''' Login page for registered users '''
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


''' Logout option, redirects to home page '''
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


''' Account info page, renders account.html '''
@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


''' Displays posts created by a particular user, render template user_posts.html '''
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


''' Route for creating new post/ submitting new idea, renders create_post.html '''
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def submit_idea():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, description=form.description.data, effort_required=form.effort_required.data,
                    business_value=form.business_value.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your idea has been created!', 'success')
        #user = User.query.filter_by(email=current_user.email).first_or_404()
        #send_email(user)
        #flash('An email has been sent to you','info')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Submit Idea',
                           form=form, legend='Submit Idea')


''' On double clicking a post, it will show all the details of that post/idea, renders post.html '''
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    #user = Comment.query.get_or_404(user_id)
    #user = Comment.query.filter_by(user_id=user.id).first_or_404()
    comments = Comment.query.filter_by(post_id=post.id).all()
    form = AddCommentForm()
    #form1 = ApproveForm()
    if form.validate_on_submit():
        #comment = Comment(comment=form.comment.data, article=post, article_1=user)
        #comment = Comment(comment=form.comment.data, username=form.username.data, article=post)
        comment = Comment(comment=form.comment.data, username=current_user.username, article=post)
        #if comment.username == current_user:
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been added to the post", "success")
        #else:
         #   flash("Please enter your registered username", "failed")

        return redirect(url_for("post", post_id=post.id))
    #return render_template('post.html', title=post.title, post=post, comments=comments, user=user, form=form)
    return render_template('post.html', title=post.title, post=post, comments=comments, form=form)


''' For updating a post/idea, renders same template for creating idea (create_post.html) '''
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:     # Only the author of the post can update his post, else error page
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        post.effort_required = form.effort_required.data
        post.business_value = form.business_value.data
        db.session.commit()
        flash('Your idea has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.effort_required.data = post.effort_required
        form.business_value.data = post.business_value
    return render_template('create_post.html', title='Update Idea',
                           form=form, legend='Update Post')


''' For deleting a post '''
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)            # Error page if someone else tries to delete a post
    try:
        db.session.delete(post)   # Deleting form database
        db.session.commit()
        flash('Your idea has been deleted!', 'success')
    except:
        return render_template('delete_error.html')
        #flash('Oops. You cannot delete the post', 'info')

        #return redirect(url_for("post", post_id=post.id))
    return redirect(url_for('home'))


''' For liking a post '''

@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    post.likes.count()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(url_for('home'))


''' For disliking a post '''

@app.route('/dislike/<int:post_id>/<action>')
@login_required
def dislike_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    post.dislikes.count()
    if action == 'dislike':
        current_user.dislike_post(post)
        db.session.commit()
    if action == 'undislike':
        current_user.undislike_post(post)
        db.session.commit()
    return redirect(url_for('home'))


''' For approving a post '''
@app.route('/approve/<int:post_id>/<action>')
@login_required
def approve_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    post.approves.count()
    if action == 'approve':
        current_user.approve_post(post)
        db.session.commit()
    #return redirect(url_for('home'))
    return redirect(url_for('post', post_id=post.id))

''' For rejecting a post '''
@app.route('/reject/<int:post_id>/<action>')
@login_required
def reject_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    post.rejects.count()
    if action == 'reject':
        current_user.reject_post(post)
        db.session.commit()
    #return redirect(url_for('home'))
    return redirect(url_for('post', post_id=post.id))

''' For sending emails '''
#def send_email(user):
 #   msg = Message('A New Post has been Created',
  #                sender='usert3244@gmail.com',
   #               recipients=['maneesjnm@gmail.com'])
    #msg.body = f'''To see the post, visit the following link:
#{url_for('home', _external=True)}
    
#If you do not wish to see the post, then simply ignore this email.
#'''
 #   mail.send(msg)

''' Error handlers for 404, 403 and 500
    404 - Not found
    403 - No permission
    500 - Server Error
 '''
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def permission_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()   # Discard the changes
    return render_template('500.html'), 500
