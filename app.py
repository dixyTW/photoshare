#export PATH=${PATH}:/usr/local/mysql/bin
#mysql -u root -h 127.0.0.1 -p
#cd /Users/kangtungho/Desktop/pa1_tunghokang
#export FLASK_APP=app.py
#flask run
#source /Users/kangtungho/desktop/pa1_tunghokang/schema.sql
#DROP DATABASE pa1;
#SELECT * FROM City
#SELECT AUTO_INCREMENT FROM information_schema.tables WHERE table_name = 'Photos' and table_schema = database();
#LOAD DATA LOCAL INFILE '/Users/kangtungho/Desktop/PA2/partsupp.data' INTO TABLE partsupp FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
#source /Users/kangtungho/desktop/PA2/table.sql

# THINGS TO DO 
# LIMIT PHOTOSIZE
# If logged in remove the login or become a new member option
# give error if registering user does not complete all fields 
# error occurs when trying to use same email?
# email has to be unique 
# how to store friends (bi directional or just store once?)
# preventing adding self as friend
# Browse other users's profile??
#change photos, albums user_id into email 
#non-existing profile picture

#print(flask_login.current_user.is_authenticated)
#SELECT AUTO_INCREMENT FROM information_schema.tables WHERE table_name = 'Users' and table_schema = database(); 
#gets next autoincrement value 

import flask
import datetime #for getting the current time/date
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
#import flask.ext.login as LoginManager
import flask_login
#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
now = datetime.datetime.now()

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'pa1' 
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			uid = getUserIdFromEmail(email)
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file
			#render_template('profile.html', name=flask_login.current_user.id, message="Here's your profile", photos=getUsersPhotos(uid))

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

@app.route('/profile')
@flask_login.login_required
def UserProfile():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('profile.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid), friends=getAllFriends(uid), tags=getUsersTag(uid), pics = getUserProfilePic(uid), bio=getUserBio(uid))

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
	return render_template('improved_register.html', supress='True')  

@app.route("/register/", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		birthday=request.form.get('birthday')
		firstName=request.form.get('firstName')
		lastName=request.form.get('lastName')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		uid = getNextID("user_id","Users")
		print cursor.execute("INSERT INTO Users (user_id,email,password,birthday,firstName,lastName,hometown,gender) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')".format(uid,email,password,birthday,firstName,lastName,hometown,gender)) #why do you need to print
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!', photos=getAllPhotos(), albums=getAllAlbums(),likes=getAllPhotoLike())
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

# <-------------------------------Users-------------------------------------->

def getUserProfilePic(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT pPic FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getUserBio(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT bio FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getTopContributor():
	#first number in the list is user id of 1 
	numUser = getNextID('user_id', 'Users')
	a = [] # has total score of each user
	for x in range(1,numUser):
		uid = getEmailFromId(x)
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM CommentInPhoto NATURAL JOIN (SELECT comment_id FROM Comments WHERE name = '{0}') as temp".format(uid))
		comment = cursor.fetchone()
		if comment:
			comment = comment[0]
		else:
			comment = 0 
		cursor.execute("SELECT COUNT(*) FROM Photos WHERE user_id = '{0}'".format(x))
		photo = cursor.fetchone()
		if photo:
			photo = photo[0]
		else:
			photo = 0

		total = comment + photo
		a.append(total)
	return sorted(range(len(a)), key=lambda i: a[i])[-3:] #sorts the ranking while keeping the order of users

def getAllFriends(uid):
	#to list all friends when viewing profile
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users INNER JOIN (SELECT friend_id FROM Friends WHERE user_id = '{0}') as test ON Users.user_id = test.friend_id;".format(uid))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserIdFromAlbumID(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Albums WHERE album_id = '{0}'".format(aid))
	return cursor.fetchone()[0]

def getUserIdFromPhoto(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Photos WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchone()[0]

def getEmailFromId(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

# <-------------------------------albums-------------------------------------->

def deleteAlbum(aid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE album_id = '{0}'".format(aid))
	return 

def getAlbumID(uid, album_name):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}' and album_name = '{1}'".format(uid, album_name))
	return cursor.fetchone()[0]

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumName(uid,aid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Albums WHERE user_id = '{0}' and album_id = '{1}'".format(uid,aid))
	return cursor.fetchone()[0]

def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT album_name, user_id, album_id FROM Albums")
	return cursor.fetchall()

	# <------------------------------photo-------------------------------------->

def deletePhoto(pid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE picture_id = '{0}'".format(pid))
	return 

def getAllPhotos():
	#used for exploring all photos on Photoshare
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Photos")
	return cursor.fetchall()

def getTagPhoto(tag_name):
	#for everyone
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption,tag_name FROM Photos NATURAL JOIN ((SELECT tag_id, tag_name FROM Tags WHERE tag_name = '{0}') as temp NATURAL JOIN TagInPhoto)".format(tag_name))
	return cursor.fetchall()

def getPopTagPhoto(tag_name):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM (SELECT tag_id FROM Tags WHERE Tags.tag_name = '{0}') as temp NATURAL JOIN TagInPhoto NATURAL JOIN Photos".format(tag_name))
	result = cursor.fetchall()
	return result

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumPhotos(uid, aid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Photos WHERE user_id = '{0}' and album_id = '{1}'".format(uid, aid))
	return cursor.fetchall()

# <-------------------------------tags-------------------------------------->

def popularTags(num):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name, tag_id, tag_count FROM Tags ORDER BY tag_count DESC LIMIT {0};".format(num))
	return cursor.fetchall()

def tagExist(tag_name):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name FROM Tags WHERE tag_name = '{0}'".format(tag_name))
	return cursor.fetchone()

def getUsersTag(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name FROM Tags NATURAL JOIN (TagInPhoto INNER JOIN (SELECT * FROM Photos WHERE user_id = '{0}') as temp ON TagInPhoto.picture_id = temp.picture_id)".format(uid))
	return cursor.fetchall() 

def getAllTags():
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name FROM Tags")
	return cursor.fetchall()

def getPhotoTags(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name FROM Tags NATURAL JOIN ((SELECT tag_id FROM TagInPhoto WHERE picture_id = '{0}') AS temp ON Tags.tag_id = temp.tag_id))".format(pid))
	return cursor.fetchall()

def getTagID(tag_name):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = '{0}'".format(tag_name))
	return cursor.fetchone()[0]

def tagCount(tag_id):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_count FROM Tags WHERE tag_id = '{0}'".format(tag_id))
	return cursor.fetchone()[0]

def removeTag(tag_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tags WHERE tag_id = '{0}'".format(tag_id))
	conn.commit()
	return 

def getAllTagInPhoto(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name FROM Tags NATURAL JOIN TagInPhoto WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchall()

def UpdateTagCount(tag_id,val):
	cursor = conn.cursor()
	cursor.execute("UPDATE Tags SET tag_count = tag_count+'{0}' WHERE tag_id = '{1}'".format(val,tag_id))
	conn.commit()
	return

# <--------------------------------Likes---------------------------------------->

def insertLike(pid,uid):
	cursor = conn.cursor()
	cursor.execute("INSERT INTO LikeInPhoto (picture_id,user_id) VALUES ('{0}','{1}')".format(pid,uid))
	conn.commit()
	return

def getPhotoLike(pid):
	pass

def getAllPhotoLike():
	#returns list of tuple with 1 attribute (num likes) in each tuple 
	picNum = getNextID('picture_id','Photos')
	rlist = []
	if picNum == 1:
		return rlist
	for x in range(1,picNum):
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM (SELECT * FROM LikeInPhoto WHERE picture_id = '{0}') as temp".format(x))
		result = cursor.fetchall()
		rlist.append(result)
	return rlist

# <-------------------------------Comments-------------------------------------->

def insertComment(uid,pid,comment):
	cursor = conn.cursor()
	date = now.strftime("%Y-%m-%d %H:%M")
	cid = getNextID('comment_id','Comments')
	cursor.execute("INSERT INTO Comments (comment_id, name, commentDate, commentData) VALUES ('{0}','{1}','{2}','{3}')".format(cid,uid,date,comment))
	cursor.execute("INSERT INTO CommentInPhoto (picture_id, comment_id) VALUES ('{0}','{1}')".format(pid,cid))
	conn.commit()
	return

def getPhotoComment(pid):
	pass

def getAllPhotoComment():
	picNum = getNextID('picture_id','Photos')
	rlist = []
	if picNum == 1:
		return rlist
	for x in range(1,picNum):
		cursor = conn.cursor()
		#SELECT picture_id 
		cursor.execute("SELECT name, commentData FROM (SELECT * FROM CommentInPhoto WHERE picture_id = '{0}') as temp NATURAL JOIN Comments".format(x))
		result = cursor.fetchall()
		rlist.append(result)
	return rlist

# <-------------------------------Utility/Check Functions-------------------------------------->

def interpret(lst):
	numUser = getNextID('user_id', 'Users')
	userlst = []
	newlst = []
	for x in range(1,numUser):
		cursor = conn.cursor()
		cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(x))
		usr = cursor.fetchone()[0]
		userlst.append(usr)
	for y in range(len(lst)):
		newlst.append(userlst[lst[2-y]])
	print(newlst)
	return newlst

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def getNextID(table_id,table):
	cursor = conn.cursor()
	cursor.execute("SELECT MAX({0}) FROM {1}".format(table_id,table))
	result = cursor.fetchone()[0]
	if result is None:
		return 1
	else:
		return result + 1


#end login code

@app.route('/explore')
def explore():
	return render_template('explore.html', photos=getAllPhotos())

@app.route('/hello')
@flask_login.login_required
def protected():
	return render_template('hello.html', pops=popularTags(5),name=flask_login.current_user.id, message="Here's your profile",albums=getAllAlbums(), photos=getAllPhotos(),tags=getAllTags(),comments=getAllPhotoComment(),likes=getAllPhotoLike())

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album_name = request.form.get('album_name')
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		aid = getAlbumID(uid, album_name)
		pid = getNextID('picture_id', 'Photos')
		cursor.execute("INSERT INTO Photos (picture_id,imgdata, album_id, user_id, caption) VALUES ('{0}' ,'{1}', '{2}', '{3}', '{4}' )".format(pid,photo_data, aid, uid, caption))
		conn.commit()
		return render_template('inter.html', pid=pid)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		if not getUsersAlbums(uid):
			return render_template('newAlbum.html', message='Please Create an Album Before Uploading Photos')
		else: 
			return render_template('upload.html')
#end photo uploading code 

@app.route('/changeBio', methods=['GET', 'POST'])
@flask_login.login_required
def change_bio():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		bio = request.form.get('bio')
		cursor = conn.cursor()
		cursor.execute("UPDATE Users SET bio = '{0}' WHERE user_id = '{1}'".format(bio,uid))
		conn.commit()
		return render_template('profile.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid), friends=getAllFriends(uid), tags=getUsersTag(uid), pics = getUserProfilePic(uid), bio=getUserBio(uid))
	else:
		return render_template('changeBio.html')

@app.route('/profilePic', methods=['GET', 'POST'])
@flask_login.login_required
def profile_pic():
	if request.method == 'POST':
		imgfile = request.files['photo']
		profilePic = base64.standard_b64encode(imgfile.read())
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("UPDATE Users SET pPic = '{0}' WHERE user_id = '{1}'".format(profilePic,uid))
		conn.commit()
		return flask.redirect(flask.url_for('UserProfile'))
	else:
		return render_template('profilePic.html')





@app.route('/addTags/<pid>', methods=['GET', 'POST'])
@flask_login.login_required
def add_tag(pid):
	if request.method == 'POST':
		print("IM HERE")
		leng = len(pid)
		picture_id = pid[1:leng-1]
		tag_name = request.form.get('tag')
		cursor = conn.cursor()
		
		if not tagExist(tag_name):
			#insert new tag
			tag_id = getNextID("tag_id","Tags")
			cursor.execute("INSERT INTO Tags (tag_id, tag_name,tag_count) VALUES ('{0}','{1}','{2}')".format(tag_id,tag_name,1))
			cursor.execute("INSERT INTO TagInPhoto (picture_id,tag_id) VALUES ('{0}', '{1}')".format(picture_id,tag_id))
		else:
			#tag already exist, incremnt tag value
			tag_id = getTagID(tag_name) 
			UpdateTagCount(tag_id,1)
			cursor.execute("INSERT INTO TagInPhoto (picture_id,tag_id) VALUES ('{0}', '{1}')".format(picture_id,tag_id))
		conn.commit()
		return render_template('inter.html', pid=picture_id)
	else:
		leng = len(pid)
		picture_id = pid[1:leng-1]
		return render_template('addTags.html', pid=picture_id) #don't know what to put here yet

@app.route('/removeTags/<pid>', methods=['GET', 'POST'])
@flask_login.login_required
def remove_tag(pid):
	if request.method == 'POST':
		cursor = conn.cursor()
		leng = len(pid)
		picture_id = pid[1:leng-1]
		tag_name = request.form.get('tag')
		tag_id = getTagID(tag_name)
		cursor.execute("DELETE FROM TagInPhoto WHERE tag_id = '{0}' and picture_id = '{1}'".format(tag_id,picture_id))
		conn.commit()
		UpdateTagCount(tag_id,-1)
		if tagCount(tag_id) == 0:
			removeTag(tag_id)
		msg = "Tag " + tag_name + " is removed from your Photo"
		return render_template('profile.html',message=msg)
	else:
		leng = len(pid)
		picture_id = pid[1:leng-1]
		return render_template('removeTags.html', pid=picture_id, tags=getAllTagInPhoto(picture_id))

@app.route('/searchPhoto',methods=['GET', 'POST'])
def searchPhoto():
	if request.method == 'POST':
		Input = request.form.get('search')
		keylist = Input.split(" ")
		rlist = []
		for x in range(len(keylist)):
			tup = getTagPhoto(keylist[x])
			for y in range(len(tup)):
				if tup[y] == None:
					pass
				else:
					rlist.append(tup[y])
		return render_template('tagSearch.html', photos=rlist)
	else:
		return render_template('searchPhoto.html')



@app.route('/newAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def make_album():
	if request.method =='POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('album_name')
		date = now.strftime("%Y-%m-%d %H:%M")
		cursor = conn.cursor()
		aid = getNextID("album_id", "Albums")
		cursor.execute("INSERT INTO Albums (album_id, album_name, user_id, creationDate) VALUES ('{0}','{1}', '{2}', '{3}' )".format(aid,album_name,uid, date))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Album Created!')
	else:
		return render_template('newAlbum.html')


@app.route('/deleteAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def delete_album():
	if request.method == 'POST':
		album_name = request.form.get('album_name')
		uid = getUserIdFromEmail(flask_login.current_user.id)
		aid = getAlbumID(uid,album_name)
		deleteAlbum(aid)
		return flask.redirect(flask.url_for('UserProfile'))
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('deleteAlbum.html', albums=getUsersAlbums(uid))

@app.route('/deletePhoto', methods=['GET', 'POST'])
@flask_login.login_required
def delete_photo():
	if request.method == 'POST':
		pid = request.form.get('pid')
		deletePhoto(pid)
		return flask.redirect(flask.url_for('UserProfile'))
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('deletePhoto.html', photos=getUsersPhotos(uid))



@app.route('/tag_photo/<tag_name>')
def viewTagPhoto(tag_name):
	leng = len(tag_name)
	name = tag_name[1:leng-1]
	return render_template('tag_photo.html', photos=getTagPhoto(name), tag=name)

@app.route('/pop_Tag/<tag_name>')
def popTag(tag_name):
	leng = len(tag_name)
	name = tag_name[1:leng-1]
	return render_template('popTag.html', photos=getPopTagPhoto(name),tag=name)

@app.route('/like/<picture_id>',methods=['POST'])
@flask_login.login_required
def like(picture_id):
	leng = len(picture_id)
	pid = picture_id[1:leng-1]
	uid = getUserIdFromEmail(flask_login.current_user.id) #email
	insertLike(pid,uid)
	return flask.redirect(flask.url_for('hello'))


@app.route('/comment/<picture_id>',methods=['POST'])
def comment(picture_id):
	leng = len(picture_id)
	pid = picture_id[1:leng-1]
	if flask_login.current_user.is_authenticated:
		uid = flask_login.current_user.id
	else:
		uid = "GUEST"
	email = getEmailFromId(getUserIdFromPhoto(pid))
	comment = request.form.get('comment')
	if email == uid:
		error("Cannot comment on your own photos")
	else:
		insertComment(uid,pid,comment)
	return flask.redirect(flask.url_for('hello'))

@app.route('/viewAlbum/<album_id>')
@flask_login.login_required
def view_album(album_id):
	leng = len(album_id)
	aid = album_id[1:leng-1]
	uid = getUserIdFromAlbumID(aid)
	album_name = getAlbumName(uid,aid)
	msg = "Photos in ", album_name
	return render_template('viewAlbum.html', name=flask_login.current_user.id, photos=getAlbumPhotos(uid,aid), message=msg)



@app.route('/addFriends', methods=['GET', 'POST'])
@flask_login.login_required
def add_friends():
	#bidirectional adding 
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		f_email = request.form.get('friend_id')
		fid = getUserIdFromEmail(f_email)
		if uid != fid:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES ('{0}', '{1}')".format(uid,fid))
			cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES ('{0}', '{1}')".format(fid,uid))
			conn.commit()
			return render_template('hello.html',name=flask_login.current_user.id, message='Friend Added!',likes=getAllPhotoLike())
		elif uid == fid:
			return error("Cannot add yourself as a Friend")
		else:
			return error("You are already friends with this user")
	else:
		return render_template('addFriends.html')

@app.route('/error')
def error(msg):
	return render_template('error.html', message=msg)
#default page  

@app.route("/", methods=['GET'])
def hello():
	result = getTopContributor()
	final = interpret(result)
	return render_template('hello.html', message='Welcome to Photoshare',pops=popularTags(5), albums=getAllAlbums(), photos=getAllPhotos(), tags=getAllTags(),comments=getAllPhotoComment(), likes=getAllPhotoLike(), tops=final)


if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
