import re
from src.error import InputError, AccessError
from src.data_store import data_store
from src.helpers import user_is_valid
from src.token import token_generate, decode_jwt, generate_jwt, generate_new_session_id, hasher

'''
<auth_login_v1>

Given a registered user's email and password, return their `auth_user_id` value.

Arguments:
    'email' (str)   - Email used to login
    'password' (str)    - Password used to login

Exceptions:
    InputError  - Email entered does not belong to a user
                - Password is incorrect

Return Value:
    Returns {'auth_user_id'}
'''
def auth_login_v1(email, password):

    store = data_store.get()

    found = False
    u_id = 0
    for user in store['users']:
        if user['email'] == email:
            found = True
            break
        u_id += 1

    # Return false if email not found
    if not found:
        raise InputError("Email is not registered with an account")

    # Test if the password matches the email
    if store['users'][u_id]['password'] != hasher(password):
        raise InputError("Incorrect password")

    token = token_generate(u_id)

    data_store.set(store)

    return {    'token': token,
                'auth_user_id': u_id}

'''
<new_handle_id> - Helper function for auth_register_v1

Generate a new handle ID based off first and last names.

Arguments:
    'name' (str)   - Takes both first and last name

Return Value:
    Returns handle_str
'''
def new_handle_id(name_first,name_last):
    # Initiating handle by adding first and last names together
    handle_str = name_first + name_last

    # Making handle all lower case
    handle_str = handle_str.lower()

    # Check and remove non-alphanumeric characters
    handle_str = ''.join(ch for ch in handle_str if ch.isalnum())

    # Checking for its length
    if len(handle_str) > 20:
        handle_str = handle_str[0:20]

    # Check if handle_str is pre-existing in data_store
    store = data_store.get()

    # Appends to the end of handle_str if duplicate is found, n increments after loop
    n = 0
    for user in store['users']:
        if user['handle_str'] == handle_str:
            # If there is an existing number in the string
            handle_str = re.sub(r'[0-9]', '', handle_str)
            handle_str = handle_str + str(n)
            n += 1

    return handle_str

'''
<auth_register_v1>

Given a user's first and last name, email address,
and password, create a new account for them and return a new `auth_user_id`.

Arguments:
    'email' (str)  - Email used to login
    'name' (str)   - Takes both first and last name
    'password' (str)   - Password used to login

Exceptions:
    InputError  - Invalid email
                - Already used email
                - Password is less than 6 characters
                - Name (First and Last) are not between 1 to 50 characters

Return Value:
    Returns {'auth_user_id'}
'''
def auth_register_v1(email, password, name_first, name_last):

    store = data_store.get()

    # Checks if invalid email
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    if not re.fullmatch(regex, email):
        raise InputError("Invalid email")

    # This checks if there is a duplicate
    for user in store['users']:
        if user['email'] == email:
            raise InputError("Email duplicate")

    # Check the password size is not less that 6 charciters
    if len(password) < 6:
        raise InputError("Password must be at least 6 characters long")

    # Check first name is not empty and is less than 50
    if len(name_first) == 0 or len(name_first) > 50:
        raise InputError("Invalid first name")

    # Check last name is not empty and is less than 50
    if len(name_last) == 0 or len(name_last) > 50:
        raise InputError("Invalid last name")

    # Create new handle ID
    handle_str = new_handle_id(name_first, name_last)

    # Set up user stats
    stats = {
        'channels_joined': [{'num_channels_joined': 0, 'time_stamp': 0}],
        'dms_joined': [{'num_dms_joined': 0, 'time_stamp': 0 }],
        'messages_sent': [{'num_messages_sent': 0, 'time_stamp': 0}],
        'involvement_rate': 0
    }

    u_id = len(store['users'])
    # Create and store the new user
    store['users'].append({ 'email': email,
                            'password': hasher(password),
                            'name_first': name_first,
                            'name_last': name_last,
                            'handle_str': handle_str,
                            'permission_id': 2,
                            'sessions': [],
                            'reset_code': '',
                            'stats': stats,
                            'image_url' : 'empty',
                            'notifications':[]})

    # Sets the first user as a global owner
    if u_id == 0:
        store['users'][0]['permission_id'] = 1

    # Add workplace statistics
    if len(store['workspace_stats']) == 0:
        store['workspace_stats'] = {
            'channels_exist': [{'num_channels_exist': 0, 'time_stamp': 0}],
            'dms_exist': [{'num_dms_exist': 0, 'time_stamp': 0 }],
            'messages_exist': [{'num_messages_exist': 0, 'time_stamp': 0}],
            'utilization_rate': 0
        }

    token = token_generate(u_id)

    data_store.set(store)

    return {'token': token, 'auth_user_id': len(store['users']) - 1}

"""
<auth_logout_v1>

Given a token, invalidate it

Arguments:
    'token'

Exceptions:
    AccessError - Invalid token

Return Value:
    Returns {}
"""
def auth_logout_v1(token):

    session = decode_jwt(token)
    store = data_store.get()

    if not user_is_valid(store, session['u_id']):
        raise AccessError("Invalid token")

    try:
        store['users'][session['u_id']]['sessions'].remove(session['session_id'])
        data_store.set(store)
    except Exception as e:
        raise AccessError("Invalid token") from e

    return {}

"""
<auth_passwordreset_request_v1>

Given a email, sent a reset code to that email

Arguments:
    'email'

Exceptions:
    None

Return Value:
    Returns {}
"""
import smtplib, ssl
import string
import random

def reset_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def auth_passwordreset_request_v1(email):

    store = data_store.get()
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "fixfork@gmail.com"  # Enter your address
    receiver_email = email  # Enter receiver address
    password = 'fixfork123'
    reset_code = reset_generator()

    u_id = 0
    for users in store['users']:
        if users['email'] == email:
            users['reset_code'] = hasher(reset_code)
            break
        u_id += 1

    message = """\
    Subject: Stroams Reset Code

    Ignore this message if you have not requested a reset
    Reset code: {}"""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.format(reset_code))

    # Logout the user on all sessions
    store['users'][u_id]['sessions'].clear()
    data_store.set(store)

    return {}

"""
<auth_passwordreset_reset_v1>

Take a reset code and new password and sets the new password as current

Arguments:
    'reset_code'
    'new_password'
Exceptions:
    InputError - Invalid reset_code
    InputError - Password too short

Return Value:
    Returns {}
"""
def code_valid(store, resetcode):
    for users in store['users']:
        if users['reset_code'] == hasher(resetcode):
                return True
    return False

def auth_passwordreset_reset_v1(reset_code, new_password):
    store = data_store.get()
    if not code_valid(store, reset_code):
        raise InputError("Invalid reset code")

    # Check the password size is not less that 6 char
    if len(new_password) < 6:
        raise InputError("Password must be at least 6 characters long")

    for user in store['users']:
        # If reset code matches, change the password
        if user['reset_code'] == hasher(reset_code):
            user['password'] = hasher(new_password)
            # Reset the code back to empty string
            user['reset_code'] = ''
    data_store.set(store)
    return {}
    