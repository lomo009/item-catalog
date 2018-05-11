from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem
import random
import string
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
import httplib2
import json
from flask import make_response
import requests

# Client Secret from Google Developer
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_user(login_session):
    nUser = User(
        name=login_session['username'],
        email=login_session['id'],
        picture=login_session['picture'])
    session.add(nUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['id']).one()
    return user.id


def get_userInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_userId(id):
    try:
        user = session.query(User).filter_by(email=id).one()
        return user.id
    except:
        return None

# Create state token for authorization
# Store for later use from user


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Route for Google Connect


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Auth code
    code = request.data
    try:
        # Turn auth code into credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check access token is valid
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Stop if error in access token
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is for app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID doesn't match app's"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Save token for later use
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # Check that user exists
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info from Google
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    print(data)
    # Save user info with welcome message
    login_session['username'] = data['name']
    login_session['id'] = data['id']
    login_session['picture'] = data['picture']
    print(login_session)
    user_id = get_userId(data["id"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1 style="color: white">Hello, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px; -mox-border-radius: 150px;"> '
    flash("You're now logged in as %s" % login_session['username'])
    return output

# Route for Google Disconnect


@app.route('/gdisconnect/')
def gdisconnect():
    if 'username' not in login_session:
        return redirect('/login/')
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = (
        'https://accounts.google.com/o/oauth2/revoke?token=%s'
        % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    # Delete user info
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['id']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected. Refresh the page to Log in again.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Home Routes


@app.route('/')
@app.route('/home/')
def home():
    catalog = session.query(Category).all()
    items = session.query(CategoryItem).all()
    return render_template('home.html', catalog=catalog, items=items)

# Category Route


@app.route('/catalog/<int:category_id>/category/')
def viewCategory(category_id):
    catalog = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category.id)
    if 'username' not in login_session:
        return render_template(
            'category.html', catalog=catalog, category=category, items=items)
    else:
        return render_template(
            'userCategory.html',
            catalog=catalog,
            category=category,
            items=items)

# Create New Item Route


@app.route('/catalog/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newCategoryItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = CategoryItem(
            user_id=login_session['user_id'],
            name=request.form['name'],
            subcategory=request.form['subcategory'],
            description=request.form['description'],
            price=request.form['price'],
            category_id=category_id)
        session.add(newItem)
        session.commit()
        flash('New Item Created!')
        return redirect(url_for('viewCategory', category_id=category_id))
    else:
        return render_template(
            'newItem.html', category=category, category_id=category_id)

# View Item Routes


@app.route(
    '/catalog/<int:category_id>/<int:ItemID>/view/', methods=['GET', 'POST'])
def viewCategoryItem(category_id, ItemID):
    itemToView = session.query(CategoryItem).filter_by(id=ItemID).one()
    if 'username' not in login_session:
        return render_template(
            'viewItem.html',
            category_id=category_id,
            ItemID=ItemID,
            item=itemToView)
    if request.method == 'POST':
        return redirect(url_for('viewCategory', category_id=category_id))
    else:
        return render_template(
            'userViewItem.html',
            category_id=category_id,
            ItemID=ItemID,
            item=itemToView)
# Edit Item Route


@app.route(
    '/catalog/<int:category_id>/<int:ItemID>/edit/', methods=['GET', 'POST'])
def editCategoryItem(category_id, ItemID):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToEdit = session.query(CategoryItem).filter_by(id=ItemID).one()
    if itemToEdit.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['subcategory']:
            itemToEdit.subcategory = request.form['subcategory']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        if request.form['price']:
            itemToEdit.price = request.form['price']
        session.add(itemToEdit)
        session.commit()
        flash("Catalog Item has been edited!")
        return redirect(
            url_for(
                'viewCategoryItem',
                category_id=category.id,
                ItemID=ItemID,
                item=itemToEdit))
    else:
        return render_template(
            'editItem.html',
            category_id=category_id,
            ItemID=ItemID,
            item=itemToEdit)

# Delete Item Route


@app.route(
    '/catalog/<int:category_id>/<int:item_id>/delete/', methods=['GET', 'POST']
    )
def deleteCategoryItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Category Item has been removed!")
        return redirect(url_for('viewCategory', category_id=category_id))
    else:
        return render_template(
            'deleteConfirm.html', category=category, item=itemToDelete)

# API Route


@app.route('/api/catalog.json')
def catalog_api():
    catalog = session.query(Category).all()
    return jsonify(
        catalog=[c.serialize for c in catalog])


@app.route('/api/catalog/<int:category_id>.json')
@app.route('/api/catalog/<int:category_id>/items.json')
def category_api(category_id):
    categoryItems = session.query(
        CategoryItem).filter_by(category_id=category_id).all()
    return jsonify(categoryItems=[ci.serialize for ci in categoryItems])


@app.route('/api/catalog/<int:category_id>/<int:item_id>.json')
@app.route('/api/catalog/<int:category_id>/<int:item_id>/data.json')
def category_item_api(category_id, item_id):
    categoryItem = session.query(CategoryItem).filter_by(id=item_id).first()
    return jsonify(categoryItem=categoryItem.serialize)

# Secret key from Class


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
