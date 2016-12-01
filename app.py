from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from flask import Flask, jsonify, make_response, request, abort, g, url_for
from flask_httpauth import HTTPTokenAuth
from datetime import datetime
from models import (User, Bucketlist, Item, bucketlists_schema,
                    items_schema, db)

db.create_all()  # create necessary tables
app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Token')
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'


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


@app.errorhandler(404)
def ivalid_url(error):
    return jsonify({'message': 'You entered an invalid URL'})


@app.errorhandler(401)
def token_expired_or_invalid(error):
    return jsonify({'message': 'Token Expired/Invalid'})


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
    return jsonify({'username': user.username}), 201, {
        'Location': url_for('new_user', id=user.id, _external=True)}


@app.route('/auth/login', methods=['POST'])
def get_auth_token():
    '''Method to create a token for a user'''
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=str(username)).first()
    if not user or not user.verify_password(password):
        return jsonify({'Stop': 'Register To Use Service!'}), 401
    else:
        g.user = user
        token = g.user.generate_auth_token()
        return jsonify({'token': 'Token ' + token.decode('ascii')})


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
    # user_id = g.user.id
    bucketlists = Bucketlist.query.filter_by(user_id=user_id)
    result = bucketlists_schema.dump(bucketlists)
    if len(result[0]) == 0:
                abort(404)
    return jsonify({'bucketlists': result.data})


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
    return jsonify({'bucketlist': result.data})


@app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['PUT'])
@auth.login_required
def update_bucketlist_item(bucketlist_id, item_id):
    '''A method to update bucketlist items
        args:
            bucketlist_id The bucketlist containing the item to edit.
            item_id The item to update in the bucketlist
    '''
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
    return jsonify({'bucketlist': new_result.data})


@app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['DELETE'])
@auth.login_required
def delete_bucketlist_item(bucketlist_id, item_id):
    '''A method to delete a bucketlist item
        args:
            bucketlist_id The id of bucketlist containing item to delete.
            item_id The id of the item to delete.
    '''
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


if __name__ == '__main__':
        app.run(debug=True)
