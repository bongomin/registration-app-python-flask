from flask import Flask,render_template,jsonify,flash,session,redirect,logging,request,url_for
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from MySQLdb.cursors import DictCursor 
from functools import wraps



app=Flask(__name__)

# config mysql
app.config['MY SQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'danny'
app.config['MYSQL_PASSWORD'] ="P@55w0rd55"
app.config['MYSQL_DB']='myapp'

# initializing msql
mysql=MySQL(app)


articles =Articles





@app.route('/')
def index():
   return render_template('home.html')
   
@app.route('/about')
def about_page():
    return render_template('about.html')
    
@app.route('/contact')
def contact_page():
    return render_template('contact.html')
    
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')
    

    
class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min =1 ,max=50)])
    username = StringField('username',[validators.Length(min=4, max=25)])
    email =  StringField('email',[validators.Length(min =1 ,max=50)])
    password = PasswordField('password',[
          validators.DataRequired(),
          validators.EqualTo('confirm',message='password do not match')
          ])
    confirm = PasswordField('confirm password')

    
    
@app.route('/register',methods=['GET','POST'])
def register():    
    form = RegisterForm(request.form)
    if request.method ==  'POST' and form.validate():
       name = form.name.data
       email = form.email.data
       username = form.username.data
       password = sha256_crypt.encrypt(str(form.password.data))

      #  creating the cursor
       cur = mysql.connection.cursor()
       cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)", (name,email,username,password))
       mysql.connection.commit()
       cur.close()
       
       flash('you are now registered and you can login to the system','success')
       
       redirect(url_for('login')) 
    return render_template('register.html', form=form)
    
#user login   
@app.route('/login',methods=['GET','POST'])
def login():
  if request.method == 'POST':
    #get form fileds
    email = request.form['email']
    password_candidate =request.form['password'] 

    #create cusor
    cur = mysql.connection.cursor(DictCursor)

    #get user by email
    result = cur.execute("SELECT * FROM users WHERE email = %s",[email])

    if result > 0:
       data = cur.fetchone()
       password = data['password']

       #compare passwords
       if sha256_crypt.verify(password_candidate,password):
           session['logged_in'] = True
           session['email'] = email


           flash('you are logged in ','success')
           return redirect(url_for('dashboard'))
       else:
           error ='invalid login'
           return render_template('login.html',error = error)
    else:
        error ='email not found'
        return render_template('login.html',error = error )

    cur.close()

  return render_template('login.html') 

#   # check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if'logged_in' in session:
           return f(*args,**kwargs)
        else:
          flash('unauthorised please login first','danger')
          return redirect(url_for('login'))

    return wrap      

# # logout
@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  flash('you are logged out of the system','success')
  return redirect(url_for('login'))
  
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')







if __name__=='__main__':
    app.secret_key="P@%^jfhgksn"
    app.run(debug=True)
