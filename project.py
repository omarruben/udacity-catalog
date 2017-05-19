from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import datetime
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
database = DBSession()

# decorator for login


def login_required(func):
    @wraps(func)  # this requires an import
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return wrapper

# custome renderer,  check if the user is logged in


def myrender(template, **params):
    params['loggedin'] = ('username' in login_session)
    return render_template(template, **params)

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return myrender('login.html', STATE=state)

# get token from facebooks , convert to long duration and save info on session


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # start change of temporal token for larger time token
    # get secret from file json on the folder
    app_id = json.loads(
        open('fb_client_secrets.json', 'r')
        .read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r')
                            .read())['web']['app_secret']

    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s&'
           'fb_exchange_token=%s' % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    fullresult = json.loads(result)

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"

    # strip expire tag from access token
    longterm_token = fullresult["access_token"]

    url = ('https://graph.facebook.com/v2.4/me?access_token=%s&'
           'fields=name,id,email' % longterm_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals
    # sign in our token

    login_session['access_token'] = longterm_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.4/me/picture?access_token=%s&'
           'redirect=0&height=200&width=200' % longterm_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists, if not save it on the database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # prepare the string OUTPUT to return to the ajax call
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;'
               'border-radius: 150px;-webkit-border-radius: 150px;'
               '-moz-border-radius: 150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output

# helper function to see the session information, used only on the debug state


@app.route('/sessioninfo')
def sessioninfo():
    output = ""
    output += '<br> username: ' + login_session['username'] + ','
    output += '<br> state: ' + login_session['state'] + ','
    output += '<br> token: ' + login_session['access_token'] + ','
    return output

# logout from facebook and teh catalog en general


@app.route('/logout')
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']

    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?'
           'access_token=%s' % (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    flash("You have successfully been logged out.")

    return redirect('/')

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   username=login_session['username'],
                   password="xxx",
                   email=login_session['email'],
                   picture=login_session['picture']
                   )
    database.add(newUser)
    database.commit()
    user = database.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = database.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = database.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Show catalog

@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = database.query(Category).order_by(asc(Category.name))
    lastitems = database.query(Item, Category).join(Category) \
        .filter(Item.category_id == Category.id) \
        .order_by(asc(Item.date)).limit(5).all()

    return myrender('front.html', title='My catalog',
                    categories=categories,
                    lastitems=lastitems)

# Show specific catalog


@app.route('/catalog/<string:catname>/')
def showCatalogx(catname):
    # get category fields (id,name,etc) , need it to get other items
    try:
        cat = database.query(Category).filter_by(name=catname).one()

        # get list of items and categories
        items = database.query(Item).filter_by(category_id=cat.id).all()
        categories = database.query(Category).order_by(asc(Category.name))

        #  DO NOT DELETE example of query for joined tables DO NOT DELETE
        #  test= database.query(Item,Category).join(Category)
        #  .filter(Item.category_id==Category.id).all()
        count = len(items)

        return myrender('catalog.html', title='My catalog',
                        categories=categories, category_name=catname,
                        category_count=count, items=items)
    except:
        return myrender('404.html', title='Error - My catalog')

# Show specific item


@app.route('/item/<string:catname>/<string:itemname>/')
def showCatalogItemx(catname, itemname):

    try:
        # get category fields (id,name,etc) , need it to get other items
        cat = database.query(Category).filter_by(name=catname).one()

        # get the item
        item = database.query(Item).filter_by(name=itemname).one()

        return myrender('item.html', title='Item Details', item=item)
    except:
        return myrender('404.html', title='Error - My catalog')

# CRUD Create a new category


@app.route('/newcategory/', methods=['GET', 'POST'])
@login_required
def newCategory():

    if request.method == 'POST':
        newCategory = Category(name=request.form['categoryName'],
                               user_id=login_session['user_id'])
        database.add(newCategory)
        flash('New category created')
        database.commit()
        return redirect('/')
    else:
        print "\n trying \n"
        return myrender('newCategory.html', title='New Category')

# CRUD Edit category


@app.route('/editcategory/<int:idx>', methods=['GET', 'POST'])
@login_required
def editCategory(idx):
    try:
        # get the field to edit
        editedCategory = database.query(Category).filter_by(id=idx).one()

        # check if the current user is the owner
        if editedCategory.user_id != login_session['user_id']:
            flash('ERROR: You are not authorized to edit this category.')
            return redirect(request.referrer)

        # if POST (update data)
        if request.method == 'POST':
            editedCategory.name = request.form['categoryName']
            flash('Category Updated')
            return redirect('/')
        else:
            categoryToEdit = database.query(Category).filter_by(id=idx).one()
            return myrender('editCategory.html', title='Edit Category',
                            currentName=categoryToEdit.name)
    except:
        return myrender('404.html', title='Error - My catalog')

# CRUD delete category


@app.route('/deletecategory/<int:idx>')
@login_required
def deleteCategory(idx):
    # check if the user is logged in
    try:
        # get the element to delete
        categoryToDelete = database.query(Category).filter_by(id=idx).one()

        # check the owner
        if categoryToDelete.user_id != login_session['user_id']:
            flash('ERROR: You are not authorized to delete this category.')
            return redirect(request.referrer)

        # everything checks out , so delete the element
        database.delete(categoryToDelete)
        flash('Successfully Deleted')
        database.commit()
        return redirect('/')
    except:
        return myrender('404.html', title='Error - My catalog')

# CRUD new item


@app.route('/newitem/', methods=['GET', 'POST'])
@login_required
def newItem():
    # if POST (save data od database and redirect to front)
    if request.method == 'POST':
        newItem = Item(
            name=request.form['itemName'],
            description=request.form['itemDescription'],
            category_id=request.form['category'],
            user_id=login_session['user_id'],
            date=datetime.datetime.now()
        )
        database.add(newItem)
        flash('New item created')
        database.commit()
        return redirect('/')
    else:
        categories = database.query(Category).order_by(asc(Category.name))
        return myrender('newItem.html',
                        title='New Item',
                        categories=categories)

# CRUD delete item


@app.route('/deleteitem/<int:idx>')
@login_required
def deleteItem(idx):
    try:
        # get the element to delete
        itemToDelete = database.query(Item).filter_by(id=idx).one()

        # check the owner
        if itemToDelete.user_id != login_session['user_id']:
            flash('ERROR: You are not authorized to delete this item.')
            return redirect(request.referrer)

        # everything checks out , so delete the element
        database.delete(itemToDelete)
        flash('Item Successfully Deleted')
        database.commit()
        return redirect('/')
    except:
        return myrender('404.html', title='Error - My catalog')
# CRUD edit item


@app.route('/edititem/<int:idx>', methods=['GET', 'POST'])
@login_required
def editItem(idx):
    try:
        # get the field to edit
        editedItem = database.query(Item).filter_by(id=idx).one()

        # check if the current user is the owner
        if editedItem.user_id != login_session['user_id']:
            flash('ERROR: You are not authorized to edit this item.')
            return redirect(request.referrer)

        # if POST (update data)
        if request.method == 'POST':
            editedItem.name = request.form['itemName']
            editedItem.description = request.form['itemDescription']
            editedItem.category_id = request.form['category']
            flash('Item Updated')
            return redirect('/')
        else:
            itemToEdit = database.query(Item).filter_by(id=idx).one()
            categories = database.query(Category).order_by(asc(Category.name))
            return myrender('editItem.html', title='Edit Item',
                            item=itemToEdit, categories=categories)
    except:
        return myrender('404.html', title='Error - My catalog')

#  generate a serialized information of the full catalog


@app.route('/catalog/JSON')
def catalogJSON():
    catalog = []
    categories = database.query(Category).all()
    for cat in categories:
        catalog.append(cat.serialize)
        item = []
        items = database.query(Item).filter_by(category_id=cat.id).all()
        for it in items:
            item.append(it.serialize)
        catalog.append(item)

    return jsonify(catalog=catalog)

#  generate a serialized information of one specific category


@app.route('/catalog/<string:idx>/JSON')
def catalogJSON(idx):
    catalog = []
    categories = database.query(Category).filter_by(name=idx).all()
    for cat in categories:
        catalog.append(cat.serialize)
        item = []
        items = database.query(Item).filter_by(category_id=cat.id).all()
        for it in items:
            item.append(it.serialize)
        catalog.append(item)

    return jsonify(catalog=catalog)

#  generate a serialized information for one specific item


@app.route('/item/<string:idx>/JSON')
def catalogJSON(idx):
    try:
        items = database.query(Item).filter_by(name=idx).all()
        return jsonify(item=[r.serialize for r in items])
    except:
        return myrender('404.html', title='Error - My catalog')

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('/catalog/'))
    else:
        flash("You were not logged in")
        return redirect(url_for('/catalog/'))


if __name__ == '__main__':
    app.secret_key = 'my_super_secret'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
