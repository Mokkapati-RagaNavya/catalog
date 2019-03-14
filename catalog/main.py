from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup import Base, LapyUser, Laptop, Types
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///laptop.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Laptops"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
camera = session.query(Laptop).all()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    camera = session.query(Laptop).all()
    youcam = session.query(Types).all()
    return render_template('login.html',
                           STATE=state, camera=camera, youcam=youcam)
    # return render_template('myhome.html', STATE=state
    # camera=camera,youcam=youcam)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = LapyUser(name=login_session['username'], email=login_session[
                   'email'])
    session.add(User1)
    session.commit()
    user = session.query(LapyUser).filter_by(
                                            email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(LapyUser).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(LapyUser).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home


@app.route('/')
@app.route('/home')
def home():
    camera = session.query(Laptop).all()
    return render_template('myhome.html', camera=camera)

#####
# Laptop Category for admins


@app.route('/LapStore')
def LapStore():
    try:
        if login_session['username']:
            name = login_session['username']
            camera = session.query(Laptop).all()
            b612 = session.query(Laptop).all()
            youcam = session.query(Types).all()
            return render_template('myhome.html', camera=camera,
                                   b612=b612, youcam=youcam, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing laptops based on laptop category


@app.route('/LapStore/<int:hiphopid>/AllBrands')
def showLaptop(hiphopid):
    camera = session.query(Laptop).all()
    b612 = session.query(Laptop).filter_by(id=hiphopid).one()
    youcam = session.query(Types).filter_by(laptopid=hiphopid).all()
    try:
        if login_session['username']:
            return render_template('showLaptop.html', camera=camera,
                                   b612=b612, youcam=youcam,
                                   uname=login_session['username'])
    except:
        return render_template('showLaptop.html',
                               camera=camera, b612=b612, youcam=youcam)

#####
# Add New Laptop


@app.route('/LapStore/addLaptop', methods=['POST', 'GET'])
def addLaptop():
    if request.method == 'POST':
        brand = Laptop(name=request.form['name'],
                       user_id=login_session['user_id'])
        session.add(brand)
        session.commit()
        return redirect(url_for('LapStore'))
    else:
        return render_template('addLaptop.html', camera=camera)

########
# Edit Laptop Category


@app.route('/LapStore/<int:hiphopid>/edit', methods=['POST', 'GET'])
def editLaptopCategory(hiphopid):
    editLap = session.query(Laptop).filter_by(id=hiphopid).one()
    creator = getUserInfo(editLap.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Laptop Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('LapStore'))
    if request.method == "POST":
        if request.form['name']:
            editLap.name = request.form['name']
        session.add(editLap)
        session.commit()
        flash("Laptop Category Edited Successfully")
        return redirect(url_for('LapStore'))
    else:
        # camera is global variable we can them in entire application
        return render_template('editLaptopCategory.html',
                               hiphop=editLap, camera=camera)

######
# Delete Laptop Category


@app.route('/LapStore/<int:hiphopid>/delete', methods=['POST', 'GET'])
def deleteLaptopCategory(hiphopid):
    hiphop = session.query(Laptop).filter_by(id=hiphopid).one()
    creator = getUserInfo(hiphop.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Laptop Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('LapStore'))
    if request.method == "POST":
        session.delete(hiphop)
        session.commit()
        flash("Laptop Category Deleted Successfully")
        return redirect(url_for('LapStore'))
    else:
        return render_template('deleteLaptopCategory.html',
                               hiphop=hiphop, camera=camera)

######
# Add New Laptop Name Details


@app.route('/LapStore/addLap/addLapDetails/<string:hiphopname>/add',
           methods=['GET', 'POST'])
def addLapDetails(hiphopname):
    b612 = session.query(Laptop).filter_by(name=hiphopname).one()
    # See if the logged in user is not the owner of laptop
    creator = getUserInfo(b612.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Laptop edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showLaptop', hiphopid=b612.id))
    if request.method == 'POST':
        lapyname = request.form['lapyname']
        speciality = request.form['speciality']
        ram = request.form['ram']
        storage = request.form['storage']
        price = request.form['price']
        warrenty = request.form['warrenty']
        rating = request.form['rating']
        lapdetails = Types(lapyname=lapyname, speciality=speciality,
                           ram=ram, storage=storage,
                           price=price,
                           warrenty=warrenty,
                           rating=rating,
                           date=datetime.datetime.now(),
                           laptopid=b612.id,
                           lapyuser_id=login_session['user_id'])
        session.add(lapdetails)
        session.commit()
        return redirect(url_for('showLaptop', hiphopid=b612.id))
    else:
        return render_template('addLapDetails.html',
                               hiphopname=b612.name, camera=camera)

######
# Edit Laptop details


@app.route('/LapStore/<int:hiphopid>/<string:camelname>/edit',
           methods=['GET', 'POST'])
def editLaptop(hiphopid, camelname):
    hiphop = session.query(Laptop).filter_by(id=hiphopid).one()
    lapdetails = session.query(Types).filter_by(lapyname=camelname).one()
    # See if the logged in user is not the owner of laptop
    creator = getUserInfo(hiphop.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this Laptop name"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showLaptop', hiphopid=hiphop.id))
    # POST methods
    if request.method == 'POST':
        lapdetails.lapyname = request.form['lapyname']
        lapdetails.speciality = request.form['speciality']
        lapdetails.ram = request.form['ram']
        lapdetails.storage = request.form['storage']
        lapdetails.price = request.form['price']
        lapdetails.warrenty = request.form['warrenty']
        lapdetails.rating = request.form['rating']
        lapdetails.date = datetime.datetime.now()
        session.add(lapdetails)
        session.commit()
        flash("Laptop Edited Successfully")
        return redirect(url_for('showLaptop', hiphopid=hiphopid))
    else:
        return render_template('editLaptop.html',
                               hiphopid=hiphopid, lapdetails=lapdetails,
                               camera=camera)

#####
# Delte Laptop Edit


@app.route('/LapStore/<int:hiphopid>/<string:camelname>/delete',
           methods=['GET', 'POST'])
def deleteLaptop(hiphopid, camelname):
    hiphop = session.query(Laptop).filter_by(id=hiphopid).one()
    lapdetails = session.query(Types).filter_by(lapyname=camelname).one()
    # See if the logged in user is not the owner of laptop
    creator = getUserInfo(hiphop.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this Laptop"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showLaptop', hiphopid=hiphop.id))
    if request.method == "POST":
        session.delete(lapdetails)
        session.commit()
        flash("Deleted Laptop Successfully")
        return redirect(url_for('showLaptop', hiphopid=hiphopid))
    else:
        return render_template('deleteLaptop.html',
                               hiphopid=hiphopid, lapdetails=lapdetails,
                               camera=camera)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
                                'Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('home'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/LapStore/JSON')
def allLaptopJSON():
    laptopcategories = session.query(Laptop).all()
    category_dict = [c.serialize for c in laptopcategories]
    for c in range(len(category_dict)):
        Laptops = [i.serialize for i in session.query(
                 Types).filter_by(laptopid=category_dict[c]["id"]).all()]
        if Laptops:
            category_dict[c]["Laptops"] = Laptops
    return jsonify(Laptop=category_dict)

####


@app.route('/LapStore/LapCategories/JSON')
def categoriesJSON():
    Laptops = session.query(Laptops).all()
    return jsonify(LapCategories=[c.serialize for c in Laptops])

####


@app.route('/LapStore/Laptops/JSON')
def itemsJSON():
    items = session.query(Types).all()
    return jsonify(laptops=[i.serialize for i in items])

#####


@app.route('/LapStore/<path:Laptop_name>/Laptops/JSON')
def categoryItemsJSON(laptop_name):
    laptopCategory = session.query(Laptop).filter_by(name=laptop_name).one()
    laptops = session.query(Types).filter_by(laptopname=laptopCategory).all()
    return jsonify(lapEdtion=[i.serialize for i in aptops])

#####


@app.route('/LapStore/<path:Laptop_name>/<path:edition_name>/JSON')
def ItemJSON(Laptop_name, edition_name):
    laptopCategory = session.query(Laptop).filter_by(name=laptop_name).one()
    lapEdition = session.query(Types).filter_by(
           name=edition_name, laptopname=laptopCategory).one()
    return jsonify(lapEdition=[lapEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=2222)
