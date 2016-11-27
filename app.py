from flask import Flask, render_template, json, request, session, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:20092338@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'I love python!!!'
db = SQLAlchemy(app)

class User(db.Model):
	user_id = db.Column('user_id', db.Integer, primary_key=True, unique=True)
	user_name = db.Column('user_name', db.String(20))
	user_email = db.Column('user_email', db.String(100))
	user_password = db.Column('user_password', db.String(20))

	posts = db.relationship('Post', backref='owner', lazy='dynamic')

class Post(db.Model):
	post_id = db.Column('post_id', db.Integer, primary_key=True, unique=True)
	post_title = db.Column('post_title', db.String(100))
	post_content = db.Column('post_content', db.String(10000))
	post_user_id = db.Column('post_user_id', db.Integer, db.ForeignKey('user.user_id'))
	# post_date= db.Column('post_date', db.String)

@app.route('/')
@app.route('/showhome')
def index():
	return render_template('index.html')

@app.route('/showsignup')
def showsignup():
	return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
	try:
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']

		if _name and _email and _password:
			user = User(user_name=_name, user_email=_email, user_password=_password)
			db.session.add(user)
			db.session.commit()
			num = User.query.all()

			if len(num) != 0:
				return redirect('/showsignin')
				# return json.dumps({'message':'User created successfully !'})
			else:
				return json.dumps({'error':'User created failly !'})
		else:
			return json.dumps({'html':'<span>Enter the required fields</span>'})

	except Exception as e:
		return json.dumps({'error':str(e)})


@app.route('/showsignin')
def showsignin():
	return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin():
	try:
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
		num = User.query.all()
		if _email and _password:
			if (num) != 0:
				if num[0].user_email == _email and num[0].user_password == _password:
					session['user_id'] = num[0].user_id
					return redirect('/userhome')
				else:
					return render_template('error.html',error = 'Wrong Email address or Password.')
			else:
				return render_template('error.html',error = 'No user.')
		else:
			return render_template('error.html',error = 'Wrong input.')
	except Exception as e:
		return json.dumps({'error':str(e)})


@app.route('/userhome')
def userhome():
	return render_template('userhome.html')

@app.route('/logout')
def logout():
	session.pop('user_id',None)
	return redirect('/')

@app.route('/showpost')
def showpost():
	return render_template('addPost.html')

@app.route('/addPost',methods=['POST'])
def addPost():
	try:
		if session.get('user_id'):
			_title = request.form['inputTitle']
			_post = request.form['inputPost']
			_user_id = session.get('user_id')

			post = Post(post_title=_title, post_content=_post, post_user_id=_user_id)
			db.session.add(post)
			db.session.commit()

			num = Post.query.all()

			if len(num) != 0:
				return redirect('/userhome')
			else:
				return render_template('error.html',error="An error occurred!")
		else:
			return render_template('error.html',error="Unauthorized Access!")
	except Exception as e:
		return render_template('error.html',error=str(e))


@app.route('/getPost')
def getPost():
	try:
		if session.get('user_id'):
			_user_id = session.get('user_id')

			posts = Post.query.filter_by(post_user_id=_user_id).all()

			posts_dict = []
			for post in posts:
				post_dict = {
					'post_id':post.post_id,
					'post_title':post.post_title,
					'post_content':post.post_content
				}
				posts_dict.append(post_dict)
			return json.dumps(posts_dict)
		else:
			return render_template('error.html',error="Unauthorized Access!")
	except Exception as e:
		return render_template('error.html',error=str(e))


@app.route('/about')
def about():
	return render_template('about.html')



if __name__ == "__main__":
	app.run(debug=True)