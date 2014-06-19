# coding=utf-8
"""User CRUD routines."""

import uuid

# Use jinja directly as we dont have guarantee of app context
# see http://stackoverflow.com/questions/17206728/
# attributeerror-nonetype-object-has-no-attribute-app
from jinja2 import Environment, PackageLoader
from users.utilities.db import get_conn, query_db
from users import APP


def add_user(
        name,
        email,
        website,
        latitude,
        longitude,
        email_updates=False):
    """Add a user to the database.

    :param name: Name of user.
    :type name: str

    :param email: Email of user.
    :type email: str

    :param website: Website of user.
    :type website: str

    :param latitude: latitude of this user
    :type latitude: float

    :param longitude: longitude of this uer
    :type longitude: float

    :param email_updates: True if user wants email updates about project
        related activities. False if not.
    :type email_updates: bool

    :returns: Globally unique identifier for the added user.
    :rtype: str
    """
    conn = get_conn(APP.config['DATABASE'])
    guid = uuid.uuid4()

    if email_updates:
        email_updates = 1
    else:
        email_updates = 0

    env = Environment(
        loader=PackageLoader('users', 'templates'))
    template = env.get_template('sql/add_user.sql')
    sql = template.render(
        guid=guid,
        name=name,
        email=email,
        website=website,
        email_updates=email_updates,
        longitude=longitude,
        latitude=latitude
    )
    conn.execute(sql)
    conn.commit()
    conn.close()
    return guid


def edit_user(
        guid,
        name,
        email,
        website,
        latitude,
        longitude,
        email_updates):
    """Edit a user with given guid with all new attribute value.

    :param guid: Guid of user.
    :type guid: str

    :param name: The new name of user.
    :type name: str

    :param email: The new email of user.
    :type email: str

    :param website: The new website of user.
    :type website: str

    :param latitude: The new latitude of this user
    :type latitude: float

    :param longitude: The new longitude of this uer
    :type longitude: float

    :param email_updates: The new email updates status of user. True if user
        wants email updates about project related activities. False if not.
    :type email_updates: bool

    :returns: Globally unique identifier for the added user.
    :rtype: str
    """
    conn = get_conn(APP.config['DATABASE'])

    if email_updates:
        email_updates = 1
    else:
        email_updates = 0

    env = Environment(
        loader=PackageLoader('users', 'templates'))
    template = env.get_template('sql/update_user.sql')
    sql = template.render(
        guid=guid,
        name=name,
        email=email,
        website=website,
        email_updates=email_updates,
        longitude=longitude,
        latitude=latitude
    )
    conn.execute(sql)
    conn.commit()
    conn.close()
    return guid


def delete_user(guid):
    """Delete a user with given guid

    :param guid: Guid of user.
    :type guid: str
    """
    conn = get_conn(APP.config['DATABASE'])
    env = Environment(
        loader=PackageLoader('users', 'templates'))
    template = env.get_template('sql/delete_user.sql')
    sql = template.render(guid=guid)
    conn.execute(sql)
    conn.commit()
    conn.close()


def get_user(guid):
    """Get a user given their GUID.

    :param guid: Globally unique identifier for the requested user.
    :type guid: str

    :returns: A user expressed as a dictionary of key value pairs or None if
        the given GUID does not exist.
    :rtype: dict
    """
    conn = get_conn(APP.config['DATABASE'])
    sql = 'SELECT * FROM user WHERE guid="%s"' % guid
    users = query_db(conn, sql)
    if len(users) == 0:
        return None
    else:
        return users[0]


def get_user_by_email(email):
    """Get one user by email.

    :param email: Email address for the requested user.
    :type email: str

    :returns: A user expressed as a dictionary of key value pairs or None if
        the given email address does not exist.
    :rtype: dict
    """
    conn = get_conn(APP.config['DATABASE'])
    sql = 'SELECT * FROM user WHERE email="%s"' % email
    users = query_db(conn, sql)
    if len(users) == 0:
        return None
    else:
        return users[0]


def get_all_users():
    """Get all users from database.

    :returns: A list of user objects.
    :rtype: list
    """
    conn = get_conn(APP.config['DATABASE'])

    sql = 'SELECT * FROM user'

    all_users = query_db(conn, sql)
    return all_users
