import os
from datetime import datetime

from flask_httpauth import HTTPTokenAuth
from flask import Flask, jsonify, make_response, request, abort, g, url_for
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

from models import (User, Bucketlist, Item, bucketlists_schema,
                    items_schema, db)


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Token')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
SECRET_KEY = os.environ["SECRET_KEY"]
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)
app.app_context().push()
db.create_all()  # create necessary tables




current_user = {
    'user_id': None
}


@auth.verify_token
def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        # The token is valid but has expired
        return None
    except BadSignature:
        # The token is invalid
        return None
    user_id = data['id']
    current_user['user_id'] = user_id
    return user_id


def verify_password(username, password):
    user = db.session.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return user


@app.route('/auth/register', methods=['POST'])
def new_user():
    '''To create a new user'''
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=str(username))
    user.hash_password(str(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({'Hello': user.username}), 201, {
        'Location': url_for('new_user', id=user.id, _external=True)}


@app.route('/auth/login', methods=['POST'])
def get_auth_token():
    '''Method to create a token for a user'''
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=str(username)).first()
    if not user or not user.verify_password(password):
        return jsonify({'Error': 'Register To Use Service!'}), 401
    else:
        g.user = user
        token = g.user.generate_auth_token(SECRET_KEY=app.config['SECRET_KEY'])
        return jsonify(
            {'Greetings': username, 'token': 'Token ' + token.decode('ascii')})


@app.route('/auth/dashboard')
@auth.login_required
def get_resource():
    '''Silly me testing whether authentication is working'''
    return jsonify({'Greetings': 'Hello, %s!' % g.user.username})


@app.route('/bucketlists/', methods=['POST'])
@auth.login_required
def create_bucketlist():
    '''A method to create a new bucketlist'''
    if not request.json or not 'name' in request.json:
                abort(400)
    bucketlist_name = request.json.get('name')
    if not bucketlist_name:
        abort(400)
    user_id = current_user['user_id']
    date_created = datetime.utcnow()
    date_modified = datetime.utcnow()
    bucketlist = Bucketlist(name=bucketlist_name,
                            date_created=date_created,
                            date_modified=date_modified, user_id=user_id)
    db.session.add(bucketlist)
    db.session.commit()
    return jsonify({'bucketlist': bucketlist.name}), 201, {
        'Location': url_for(
            'get_bucketlist', bucketlist_id=bucketlist.id, _external=True)}


@app.route('/bucketlists/', methods=['GET'])
@auth.login_required
def get_bucketlists():
    '''A Method to get all bucket lists'''
    user_id = current_user['user_id']
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        return jsonify({'message': 'Invalid Page Value'})
    try:
        limit = int(request.args.get('limit', 20))
    except Exception:
        return jsonify({'message': 'Invalid Limit Value'})
    search = request.args.get('q', '')

    if db.session.query(Bucketlist).filter_by(user_id=user_id).count() == 0:
        return jsonify({'message': 'no bucketlist found'})

    bucketlist_rows = Bucketlist.query.filter(
        Bucketlist.user_id == user_id,
        Bucketlist.name.like('%' + search + '%')).paginate(page, limit, False)

    all_pages = bucketlist_rows.pages
    next_page = bucketlist_rows.has_next
    previous_page = bucketlist_rows.has_prev

    if next_page:
        next_page_url = str(request.url_root) + 'bucketlists?' + \
            'limit=' + str(limit) + '&page=' + str(page + 1)
    else:
        next_page_url = None

    if previous_page:
        previous_page_url = str(request.url_root) + 'bucketlists?' + \
            'limit=' + str(limit) + '&page=' + str(page - 1)
    else:
        previous_page_url = None

    bucketlists = []
    for bucketlist in bucketlist_rows.items:
        bucketlistitems = []
        bucketlistitem_rows = Item.query.filter(
            Item.bucketlist_id == bucketlist.id).all()
        for bucketlistitem in bucketlistitem_rows:
            bucketlistitems.append({
                'id': bucketlistitem.id,
                'name': bucketlistitem.name,
                'date_created': bucketlistitem.date_created,
                'date_modified': bucketlistitem.date_modified,
                'done': bucketlistitem.done
            })
        bucketlists.append({
            'id': bucketlist.id,
            'name': bucketlist.name,
            'date_created': bucketlist.date_created,
            'date_modified': bucketlist.date_modified,
            'created_by': bucketlist.created_by.username,
            'items': bucketlistitems,
            'total_pages': all_pages,
            'next_page': next_page_url,
            'previous_page': previous_page_url
        })

    return jsonify({'bucketlists': bucketlists})


@app.route('/bucketlists/<int:bucketlist_id>', methods=['GET'])
@auth.login_required
def get_bucketlist(bucketlist_id):
    '''A method to get one bucket list
        args:
        bucketlist_id The id of the bucketlist to get.
    '''
    bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    result = bucketlists_schema.dump(bucketlist)
    if len(result[0]) == 0:
                abort(404)
    return jsonify({'bucketlist': result.data})


@app.route('/bucketlists/<int:bucketlist_id>', methods=['PUT'])
@auth.login_required
def update_bucketlist(bucketlist_id):
    '''A method to update bucketlist details
        args:
            bucketlist_id The id of the bucketlist to update.
    '''

    user_id = current_user['user_id']
    bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=user_id)
    result = bucketlists_schema.dump(bucketlist)
    if len(result[0]) == 0:
        abort(404)  # Abort incase bucketlist does not exist.
    if not request.json:
        abort(400)  # If a user sends anything other than Json

    name = request.json.get('name', None)
    if not name:
        abort(400)  # Abort incase user does not send a new name for bucket.
    date_modified = datetime.utcnow()
    bucketlistnew = {"name": str(name), "date_modified": date_modified}
    bucketlist.update(bucketlistnew)
    db.session.commit()

    updated_bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=user_id)  # Get the updated bucketlist
    new_result = bucketlists_schema.dump(updated_bucketlist)

    return jsonify({'bucketlist': new_result.data})


@app.route('/bucketlists/<int:bucketlist_id>', methods=['DELETE'])
@auth.login_required
def delete_bucketlist(bucketlist_id):
    '''Delete a bucketlist
        args:
            bucketlist_id The id of the bucketlist to delete.
    '''
    bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    result = bucketlists_schema.dump(bucketlist)
    if len(result[0]) == 0:
                abort(404)  # Abort incase bucketlist does not exist.
    bucketlist.delete()
    db.session.commit()
    return jsonify({'Success!': 'Bucketlist Deleted'})


@app.route('/bucketlists/<int:bucketlist_id>/items/', methods=['POST'])
@auth.login_required
def create_bucketlist_item(bucketlist_id):
    '''A method to create a new bucketlist item
        args:
            bucketlist_id The id of the bucketlist you want to add an item to.
    '''

    if not request.json or not 'name' in request.json:
                abort(400)  # No name provided in the request

    bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    result = bucketlists_schema.dump(bucketlist)
    if len(result[0]) == 0:
                abort(404)  # For a non existent bucketlist

    item_name = request.json.get('name')
    if not item_name:
        abort(400)
    bucketlist_id = bucketlist_id
    date_created = datetime.utcnow()
    date_modified = datetime.utcnow()
    item = Item(
        name=item_name, date_created=date_created, date_modified=date_modified,
        bucketlist_id=bucketlist_id, done=False)
    db.session.add(item)
    db.session.commit()

    updated_bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    result = bucketlists_schema.dump(updated_bucketlist)
    if len(result[0]) == 0:
                abort(404)  # Non-existent bucketlist
    return jsonify({'bucketlist': result.data}), 201


@app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['PUT'])
@auth.login_required
def update_bucketlist_item(bucketlist_id, item_id):
    '''A method to update bucketlist items
        args:
            bucketlist_id The bucketlist containing the item to edit.
            item_id The item to update in the bucketlist
    '''
    bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    result = bucketlists_schema.dump(bucketlist)
    if len(result[0]) == 0:
                abort(404)

    item = Item.query.filter_by(
        id=item_id, bucketlist_id=bucketlist_id)
    result = items_schema.dump(item)
    if len(result[0]) == 0:
                abort(404)  # Abort incase bucketlist does not exist.
    if not request.json:
        abort(400)  # If a user sends anything other than Json
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)  # Abort incase user does not send a valid bolean for done

    name = request.json.get('name', None)
    if not name:
        abort(400)  # Abort incase user does not send a new name for item.
    done = request.json.get('done')
    date_modified = datetime.utcnow()
    updateditem = {
        "name": str(name), "date_modified": date_modified, "done": done}
    item.update(updateditem)
    db.session.commit()

    updated_bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    new_result = bucketlists_schema.dump(updated_bucketlist)
    return jsonify({'bucketlist': new_result.data}), 201


@app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['DELETE'])
@auth.login_required
def delete_bucketlist_item(bucketlist_id, item_id):
    '''A method to delete a bucketlist item
        args:
            bucketlist_id The id of bucketlist containing item to delete.
            item_id The id of the item to delete.
    '''
    bucketlist = Bucketlist.query.filter_by(
        id=bucketlist_id, user_id=current_user['user_id'])
    result = bucketlists_schema.dump(bucketlist)
    if len(result[0]) == 0:
                abort(404)

    item = Item.query.filter_by(
        id=item_id, bucketlist_id=bucketlist_id)
    result = items_schema.dump(item)
    if len(result[0]) == 0:
                abort(404)  # Abort incase bucketlist does not exist.
    item.delete()
    db.session.commit()

    return jsonify({'Success!': 'Item deleted'})


@app.errorhandler(404)
def not_found(error):
    '''Return Error as a Json File'''
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(401)
def token_expired_or_invalid(error):
    '''Error as json'''
    return make_response(jsonify({'message': 'Token Expired/Invalid'}), 401)


if __name__ == '__main__':
        app.run(debug=True)
