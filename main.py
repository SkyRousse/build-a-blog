from flask import Flask, render_template, session, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogging@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "aj56kghj9gi4ypn6c5"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, body, category, owner, pub_date=None):
        self.title = title
        self.body = body
        self.category = category
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Post %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.all()
    return render_template('index.html', title='PyBlog', posts=posts)

@app.before_request
def require_login():
    login_routes = ['add_post']
    if request.endpoint in login_routes and 'email' not in session:
        return redirect('/login')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash("sucess, thanks for registering", "success")
            return redirect('/')
        else:
            flash("oops, user already exists. Login below", "warning")
            return redirect('/login')

    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged in successfully', 'success')
            return redirect('/')
        else:
            flash('Login info incorrect, please try again', 'error')
            return render_template('login.html')
    else:
        return render_template('login.html')

    
@app.route('/logout')
def logout():
    del session['email']
    flash('you have been logged out', 'warning')
    return redirect('/')

@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form['post-title']
        body = request.form['post-body']
        post_category = request.form['post-category']
        category = Category.query.filter_by(name=post_category).first()
        user = User.query.filter_by(email=session['email']).first()
        new_post = Post(title, body, category, user)
        db.session.add(new_post)
        db.session.commit()
        flash('new post successfully created', 'success')
        return redirect('/')
    else:
        return render_template('add_post.html', categories=categories)

if __name__ == '__main__':
    app.run()