# coding=utf-8
"""Views to handle url requests. Flask main entry point is also defined here.
:copyright: (c) 2013 by Tim Sutton
:license: GPLv3, see LICENSE for more details.
"""
import json

from flask import render_template, Response, request
from werkzeug.exceptions import default_exceptions

# App declared directly in __init__ as per
# http://flask.pocoo.org/docs/patterns/packages/#larger-applications
from . import APP
from users.utilities.helpers import make_json_error
from users.utilities.validator import (
    is_email_address_valid,
    is_required_valid,
    is_boolean)
from users.user import add_user, get_user, get_all_users


@APP.route('/')
def map_view():
    """Default view - shows a map with users."""
    context = dict(
        current_tag_name='None',
        error='None',
    )
    #pylint: disable=W0142
    return render_template('base.html', **context)


@APP.route('/users.json', methods=['POST'])
def users_view():
    """Return a json document of users who have registered themselves."""
    # Get data:
    user_type = int(request.form['user_type'])

    # Create model User
    if user_type == 0:
        all_users = get_all_users()
    elif user_type == 1:
        all_users = get_all_users(role=1)
    elif user_type == 2:
        all_users = get_all_users(role=2)

    json_users = render_template('users.json', users=all_users)

    users_json = (
        '{'
        ' "users": %s'
        '}' % json_users
    )
    # Return Response
    return Response(users_json, mimetype='application/json')


@APP.route('/add_user', methods=['POST'])
def add_user_view():
    """View to add a user.

    Handle post request via ajax and add the user to the user.db

    :returns: A new json response as in users.json.
    :rtype: HttpResponse

    .. note:: JavaScript on client must update the map on ajax completion
        callback.
    """
    # return any errors as json - see http://flask.pocoo.org/snippets/83/
    for code in default_exceptions.iterkeys():
        APP.error_handler_spec[None][code] = make_json_error

    # Get data from form
    name = str(request.form['name']).strip()
    email = str(request.form['email']).strip()
    role = int(request.form['role'])
    email_updates = str(request.form['email_updates'])
    latitude = str(request.form['latitude'])
    longitude = str(request.form['longitude'])

    # Validate the data:
    message = {}
    if not is_required_valid(name):
        message['name'] = 'Name is required'
    if not is_email_address_valid(email):
        message['email'] = 'Email address is not valid'
    if not is_required_valid(email):
        message['email'] = 'Email is required'
    if role not in [0, 1, 2]:
        message['role'] = 'Role must be checked'
    elif not is_boolean(email_updates):
        message['email_updates'] = 'Notification must be checked'

    # Modify the data:
    if email_updates == 'true':
        email_updates = True
    else:
        email_updates = False

    # Process data
    if len(message) != 0:
        message['type'] = 'Error'
        return Response(json.dumps(message), mimetype='application/json')
    else:
        # Create model for user and add user
        guid = add_user(
            name=name,
            email=email,
            role=int(role),
            email_updates=bool(email_updates),
            latitude=float(latitude),
            longitude=float(longitude))

    # Prepare json for added user
    user = get_user(guid)
    added_user = render_template('users.json', users=[user])
    # Return Response
    return Response(added_user, mimetype='application/json')
