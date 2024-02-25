import hashlib
import jwt
import re
from src.error import AccessError
from src.data_store import data_store
from src.helpers import user_is_valid

SECRET = 'UVKAukOA3VK3ngJdIS5gLqCvpQPPi8'
# Probably change this

"""Generates a new sequential session ID

Returns:
    number: The next session ID
"""
def generate_new_session_id():

    store = data_store.get()
    store['session_num'] += 1
    data_store.set(store)
    return store['session_num']


def hasher(input_string):
    """
    Hashes the input string with sha256

    Args:
        input_string ([string]): The input string to hash

    Returns:
        string: The hexidigest of the encoded string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


"""Generates a JWT using the global SECRET

Args:
    username ([string]): The username
    session_id ([string], optional): The session id, if none is provided will
                                        generate a new one. Defaults to None.

Returns:
    string: A JWT encoded string
"""
def generate_jwt(u_id, session_id):

    return jwt.encode({'u_id': u_id, 'session_id': session_id},
                        SECRET, algorithm='HS256')

"""Decodes a JWT string into an object of the data

Args:
    encoded_jwt ([string]): The encoded JWT as a string

Returns:
    Object: An object storing the body of the JWT encoded string
"""
def decode_jwt(encoded_jwt):

    try:
        return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    except Exception as e:
        raise AccessError("Invalid token") from e


"""Takes in a hanle string and returns a token with handle string and session_id
    also updates the token to the users session_id list

Args:
    handlestring ([string]): The username

Returns:
    string: A JWT encoded string
"""
def token_generate(u_id):

    # Generates a new session id
    session_id = generate_new_session_id()
    # session_id = 1
    # Append the session id to the users session id string
    store = data_store.get()

    store['users'][u_id]['sessions'].append(session_id)

    data_store.set(store)

    # Uses the session id to create a new token
    return generate_jwt(u_id, session_id)

"""Takes in a token and returns true or not based on whether it's valid

Args:
    encoded_jwt

Returns:
    true or false
"""
def valid_session(session):

    store = data_store.get()

    # Not applicable to tests that don't break abstraction

    # if (session['u_id'] is None or session['session_id'] is None
    #     or not user_is_valid(store, session['u_id'])):
    #     return False

    for session_id in store['users'][session['u_id']]['sessions']:
        if session_id == session['session_id']:
            return True
    return False

"""
def test_if_token_type(token):

    Probably not that useful

    regex = "^[A-Za-z0-9\\-_=]+\\.[A-Za-z0-9\\-_=]+(\\.[A-Za-z0-9\\-_.+/=]+)?$"

    if not re.fullmatch(regex, token):
        return False

    return True
"""
