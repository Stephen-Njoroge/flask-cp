#!flask/bin/python
from flask import Flask, jsonify, make_response, request,  abort, g, url_for
from flask_httpauth import HTTPBasicAuth
from models import db, User

# initialization
app = Flask(__name__)
db.create_all()  # create necessary tables

# extensions
auth = HTTPBasicAuth()


@app.route('/auth/register', methods=['POST'])
def new_user():
    '''To create a new user'''
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201, {
        'Location': url_for('new_user', id=user.id, _external=True)}


@app.route('/auth/login', methods=['POST'])
def get_auth_token():
    '''Method to create a token for a user'''
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return jsonify({'Stop': 'Register To Use Service!'})
    else:
        g.user = user
        token = g.user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})


@auth.verify_password
def verify_password(username_or_token, password):
    '''To verify a user is registered'''
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/auth/dashboard')
@auth.login_required
def get_resource():
    return jsonify({'Greetings': 'Hello, %s!' % g.user.username})


bucketlists = [{
    'id': 1,
    'name': "BucketList1",
    'items': [{
        'id': 1,
        'name': "I need to do X",
        'date_created': "2015-08-12 11:57:23",
        'date_modified': "2015-08-12 11:57:23",
        'done': False
    }],
    'date_created': "2015-08-12 11:57:23",
    'date_modified': "2015-08-12 11:57:23",
    'created_by': "1113456"
},
    {
    'id': 2,
    'name': "BucketList2",
    'items': [{
        'id': 1,
        'name': "I need to do pee",
        'date_created': "2015-08-12 11:57:23",
        'date_modified': "2015-08-12 11:57:23",
        'done': False
    }],
    'date_created': "2015-08-12 11:57:23",
    'date_modified': "2015-08-12 11:57:23",
    'created_by': "1113456"
}]


@app.route('/bucketlists/', methods=['POST'])
def create_bucketlist():
    '''A method to create a new bucketlist'''
    if not request.json or not 'name' in request.json:
                abort(400)
    bucketlist = {
        'id': bucketlists[-1]['id'] + 1,
        'name': request.json['name'],
        'items': request.json.get('items', [{
            'id': 1,
            'name': request.json.get('item_name', ""),
            'date_created': request.json.get('item_date_created', ""),
            'date_modified': request.json.get('item_date_modified', ""),
            'done': False
        }]),
        'date_created': request.json.get('date_created', ""),
        'date_modified': request.json.get('date_modified', ""),
        'created_by': request.json.get('created_by', "")
    }
    bucketlists.append(bucketlist)
    return jsonify({'bucketlist': bucketlist}), 201


@app.route('/bucketlists/', methods=['GET'])
def get_bucketlists():
    '''A Method to get all bucket lists'''
    return jsonify({'bucketlists': bucketlists})


@app.route('/bucketlists/<int:bucketlist_id>', methods=['GET'])
def get_bucketlist(bucketlist_id):
    '''A method to get one bucket list
        args:
        bucketlist_id The id of the bucketlist to get.
    '''
    bucketlist = [
        bucketlist for bucketlist in bucketlists if
        bucketlist['id'] == bucketlist_id]
    if len(bucketlist) == 0:
                abort(404)
    return jsonify({'bucketlist': bucketlist[0]})


@app.route('/bucketlists/<int:bucketlist_id>', methods=['PUT'])
def update_bucketlist(bucketlist_id):
    '''A method to update bucketlist details
        args:
            bucketlist_id The id of the bucketlist to update.
    '''
    bucketlist = [
        bucketlist for bucketlist in bucketlists if
        bucketlist['id'] == bucketlist_id]
    if len(bucketlist) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'items' in request.json and type(request.json['items']) is not str:
        abort(400)
    if 'date_created' in request.json and type(
            request.json['date_created']) is not str:
        abort(400)
    if 'date_modified' in request.json and type(
            request.json['date_modified']) is not str:
        abort(400)
    if 'created_by' in request.json and type(
            request.json['created_by']) is not str:
        abort(400)
    bucketlist[0]['name'] = request.json.get('name', bucketlist[0]['name'])
    bucketlist[0]['items'] = request.json.get('items', bucketlist[0]['items'])
    bucketlist[0]['date_created'] = request.json.get(
        'date_created', bucketlist[0]['date_created'])
    bucketlist[0]['date_modified'] = request.json.get(
        'date_modified', bucketlist[0]['date_modified'])
    bucketlist[0]['created_by'] = request.json.get(
        'created_by', bucketlist[0]['created_by'])

    return jsonify({'bucketlist': bucketlist[0]})


@app.route('/bucketlists/<int:bucketlist_id>', methods=['DELETE'])
def delete_bucketlist(bucketlist_id):
    '''Delete a bucketlist
        args:
            bucketlist_id The id of the bucketlist to delete.
    '''
    bucketlist = [
        bucketlist for bucketlist in bucketlists if
        bucketlist['id'] == bucketlist_id]
    if len(bucketlist) == 0:
        abort(404)
    bucketlist.remove(bucketlist[0])
    return jsonify({'result': True})


@app.route('/bucketlists/<int:bucketlist_id>/items/', methods=['POST'])
def create_bucketlist_item(bucketlist_id):
    '''A method to create a new bucketlist
        args:
            bucketlist_id The id of the bucketlist you want to add an item.
    '''
    bucketlist = [
        bucketlist for bucketlist in bucketlists if
        bucketlist['id'] == bucketlist_id]
    bucketlist_items = bucketlist[0]['items']
    if not request.json or not 'item_name' in request.json:
                abort(400)
    item = {
        'id': bucketlist_items[-1]['id'] + 1,
        'name': request.json.get('item_name', ""),
        'date_created': request.json.get('item_date_created', ""),
        'date_modified': request.json.get('item_date_modified', ""),
        'done': request.json.get('done', False)}
    bucketlist_items.append(item)
    return jsonify({'bucketlist': bucketlist}), 201


@app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['PUT'])
def update_bucketlist_item(bucketlist_id, item_id):
    '''A method to update bucketlist items
        args:
            bucketlist_id The bucketlist containing the item to edit. 
            item_id The item to update in the bucketlist
    '''
    bucketlist = [
        bucketlist for bucketlist in bucketlists if
        bucketlist['id'] == bucketlist_id]
    bucketlist_item = bucketlist[0]['items'][item_id-1]
    if len(bucketlist_item) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    if 'date_created' in request.json and type(request.json['date_created']) is not str:
        abort(400)
    if 'date_modified' in request.json and type(request.json['date_modified']) is not str:
        abort(400)
    bucketlist_item['name'] = request.json.get('name', bucketlist_item['name'])
    bucketlist_item['date_created'] = request.json.get(
        'date_created', bucketlist_item['date_created'])
    bucketlist_item['date_modified'] = request.json.get(
        'date_modified', bucketlist_item['date_modified'])
    bucketlist_item['done'] = request.json.get(
        'done', bucketlist_item['done'])

    return jsonify({'bucketlist': bucketlist[0]})


@app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['DELETE'])
def delete_bucketlist_item(bucketlist_id, item_id):
    '''A method to delete a bucketlist item
        args:
            bucketlist_id The id of bucketlist containing item to delete.
            item_id The id of the item to delete.
    '''
    bucketlist = [
        bucketlist for bucketlist in bucketlists if
        bucketlist['id'] == bucketlist_id]
    bucketlist_items = bucketlist[0]['items']
    bucketlist_item = bucketlist[0]['items'][item_id-1]
    if len(bucketlist_item) == 0:
        abort(404)
    bucketlist_items.remove(bucketlist_item)
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    '''Return Error as a Json File'''
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
        app.run(debug=True)
