from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from data import Beers
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)

#Beers = Beers()

# Home page
@app.route('/')
def index():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# The List of beers
@app.route('/beers')
def beers():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get beers
    result = cur.execute("SELECT * FROM beerlist_main")

    beers = cur.fetchall()

    if result > 0:
        return render_template('beers.html', beers=beers)
    else:
        msg = 'No Beers Found'
        return render_template('beers.html')

    # Close connection
    cur.close()

    return render_template('beers.html', beers=Beers)

# Single Beer
@app.route('/beer/<string:id>/')
def beer(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get beers
    result = cur.execute("SELECT * FROM beerlist_main WHERE id=%s", [id])

    beer = cur.fetchone()
    return render_template('beer.html', beer=beer)

class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#user Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s,%s,%s,%s)", (name, email, username, password))
        # commit to DB
        mysql.connection.commit()
        # close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are  now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard to edit the list of beers
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get beers
    result = cur.execute("SELECT * FROM beerlist_main")

    beers = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', beers=beers)
    else:
        msg = 'No Beers Found'
        return render_template('dashboard.html')

    # Close connection
    cur.close()

# Article Form Class
class ArticleForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    style = StringField('Style', [validators.Length(min=1, max=50)])
    abv = StringField('Abv', [validators.Length(max=5)])
    ibu = StringField('Ibu', [validators.Length(max=5)])
    brewery = StringField('Brewery', [validators.Length(min=5, max=100)])
    location = StringField('Location', [validators.Length(max=255)])
    website = StringField('Website', [validators.Length(max=255)])
    description = TextAreaField('Description', [validators.Length(min=0)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        style = form.style.data
        abv = form.abv.data
        ibu = form.ibu.data
        brewery = form.brewery.data
        location = form.location.data
        website = form.website.data
        description = form.description.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO beerlist_main(name, style, abv, ibu, brewery, location, website, description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(name, style, abv, ibu, brewery, location, website, description))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Beer added to list.', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)

# Edit Article
@app.route('/edit_beer/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get beer by id
    result = cur.execute("SELECT * FROM beerlist_main WHERE id = %s", [id])

    beer = cur.fetchone()

    # Get form
    form = ArticleForm(request.form)

    # Populate beer from fields
    form.name.data = beer['name']
    form.style.data = beer['style']
    form.abv.data = beer['abv']
    form.ibu.data = beer['ibu']
    form.brewery.data = beer['brewery']
    form.location.data = beer['location']
    form.website.data = beer['website']
    form.description.data = beer['description']


    if request.method == 'POST' and form.validate():
        name = request.form['name']
        style = request.form['style']
        abv = request.form['abv']
        ibu = request.form['ibu']
        brewery = request.form['brewery']
        location = request.form['location']
        website = request.form['website']
        description = request.form['description']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("UPDATE beerlist_main SET name=%s, style=%s, abv=%s, ibu=%s, brewery=%s, location=%s, website=%s, description=%s WHERE id=%s", (name, style, abv, ibu, brewery, location, website, description, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Beer updated.', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_beer.html', form=form)

# Delete beer
@app.route('/delete_beer/<string:id>', methods=['POST'])
@is_logged_in
def delete_beer(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM beerlist_main WHERE id=%s", [id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('Beer Deleted', 'success')

    return redirect(url_for('dashboard'))

if __name__== '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
