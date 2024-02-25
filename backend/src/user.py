import re
import pytest
from src.data_store import data_store
from src.error import InputError
from datetime import timezone, datetime
import urllib.request
from PIL import Image
import requests
from tests.helpers import BASE_URL




'''
<users_all_v1>

Returns a list of all users and their associated details.

Arguments:
    N/A

Exceptions:
    N/A

Return Value:
    Returns {'users'}
'''
def users_all_v1():

    user_list = []
    store = data_store.get()

    u_id = 0
    for user in store['users']:
        if user['permission_id'] is not None:
            user_list.append({  'u_id': u_id,
                                'email': user['email'],
                                'name_first': user['name_first'],
                                'name_last': user['name_last'],
                                'handle_str': user['handle_str']
                            })
        u_id += 1

    return {'users': user_list}

'''
<user_profile_v1>

For a valid user, returns information about their u_id, email, first name, last name, and handle

Arguments:
    'u_id' (int)    - ID of user

Exceptions:
    InputError  - u_id does not refer to a valid user

Return Value:
    Returns {'user'}
'''
def user_profile_v1(u_id):

    store = data_store.get()
    # The user_is_valid() helper isn't used because removed users can still have profiles
    if u_id < 0 or len(store['users']) <= u_id:
        raise InputError("User ID is not registered with a user")

    profile = {
        'u_id': u_id,
        'email': store['users'][u_id]['email'],
        'name_first': store['users'][u_id]['name_first'],
        'name_last': store['users'][u_id]['name_last'],
        'handle_str': store['users'][u_id]['handle_str']
    }

    return {'user': profile}

'''
<user_profile_setname_v1>

For a valid user, returns information about their u_id, email, first name, last name, and handle

Arguments:
    'u_id' (int)    - ID of user
    'name_first'    - First name of user
    'name_last'     - Last name of user

Exceptions:
    InputError  - Length of name_first is not between 1 and 50 characters inclusive
                - Length of name_last is not between 1 and 50 characters inclusive

Return Value:
    Returns {}
'''
def user_profile_setname_v1(u_id, name_first, name_last):

    store = data_store.get()

    # Check first name is not empty and is less than 50
    if len(name_first) == 0 or len(name_first) > 50:
        raise InputError("Invalid first name")

    # Check last name is not empty and is less than 50
    if len(name_last) == 0 or len(name_last) > 50:
        raise InputError("Invalid last name")

    # Set the first and last name to the new values
    store['users'][u_id]['name_first'] = name_first
    store['users'][u_id]['names_last'] = name_last

    data_store.set(store)

    return {}

'''
<user/profile/setemail/v1>

Update the authorised user's email address

Arguments:
    'u_id' (int)    - ID of user
    'email' (str)   - Updated Email of user

Exceptions:
    InputError  - Email entered is not a valid email (more in section 6.4)
                - Email address is already being used by another user

Return Value:
    Returns {}
'''
def user_profile_setemail_v1(u_id, email):

    store = data_store.get()

    # Check for invalid email
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    if not re.fullmatch(regex, email):
        raise InputError("Invalid email")

    # This checks if there is a duplicate
    for user in store['users']:
        if user['email'] == email:
            raise InputError("Email duplicate")

    # Set the email to the new value
    store['users'][u_id]['email'] = email

    data_store.set(store)

    return {}

'''
<user_profile_sethandle_v1>

Update the authorised user's handle (i.e. display name)

Arguments:
    'u_id' (int)    - ID of user
    'email' (str)   - Updated email of user

Exceptions:
    InputError  - Length of handle_str is not between 3 and 20 characters inclusive
                - Handle_str contains characters that are not alphanumeric
                - The handle is already used by another user

Return Value:
    Returns {}
'''
def user_profile_sethandle_v1(u_id, handle_str):

    store = data_store.get()

    # Check if lenght is between 3 and 20 inclusive
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("Length of handle_str is not between 3 and 20 characters inclusive")

    # Check it is alpha numeric
    if handle_str.isalnum() == False:
        raise InputError("Handle contains characters that are not alphanumeric")


    # Check handle is not a duplicate
    for user in store['users']:
        if user['handle_str'] == handle_str:
            raise InputError("The handle is already used by another user")

    # Set handle str to new value
    store['users'][u_id]['handle_str'] = handle_str

    data_store.set(store)

    return {}

def user_stats(call, u_id, value):

    store = data_store.get()

    if call == 'print':
        return {'user_stats': store['users'][u_id]['stats']}

    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    num_call = 'num_' + call
    last_element = store['users'][u_id]['stats'][call][-1]
    store['users'][u_id]['stats'][call].append({
        num_call: (last_element[num_call] + value),
        'time_stamp': time
    })

    data_store.set(store)

    update_involvement(u_id)

def users_stats(call, u_id, value):

    store = data_store.get()

    if call == 'print':
        return {'workspace_stats': store['workspace_stats']}

    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    num_call = 'num_' + call
    workspace_stats = store['workspace_stats']
    store['workspace_stats'][call].append({
        num_call: (workspace_stats[call][-1][num_call] + value),
        'time_stamp': time
    })

    data_store.set(store)

    update_utilization()

def update_involvement(u_id):

    store = data_store.get()

    num_channels = len(store['channels'])
    num_dms = len(store['dms'])

    # Find the amount of messages
    num_messages = 0
    for channel in store['channels']:
        num_messages += len(channel['messages'])
    for dm in store['dms']:
        num_messages += len(dm['messages'])

    total_count = (num_channels + num_dms + num_messages)

    # Update the user stats
    channels_joined = store['users'][u_id]['stats']['channels_joined']\
                    [-1]['num_channels_joined']
    messages_sent = store['users'][u_id]['stats']['messages_sent'][-1]['num_messages_sent']
    dms_joined = store['users'][u_id]['stats']['dms_joined'][-1]['num_dms_joined']

    stats_num = (channels_joined + messages_sent + dms_joined)

    # Update the involvement rate
    # total_count >= 1 if this function is called, so no need to account for division by zero
    involvement_rate = stats_num/total_count
    if involvement_rate >= 1:
        store['users'][u_id]['stats']['involvement_rate'] = 1
    else:
        store['users'][u_id]['stats']['involvement_rate'] = involvement_rate

    data_store.set(store)

def update_utilization():

    store = data_store.get()
    invloved_users = []

    # Add all the users part of a channel
    for channel in store['channels']:
        for member in channel['all_members']:
            if member not in invloved_users:
                invloved_users.append(member)


    # Add all the users part of a dm
    for dm in store['dms']:
        for member in dm['members']:
            if member not in invloved_users:
                invloved_users.append(member)

    workspace_stats = store['workspace_stats']

    workspace_stats['utilization_rate'] = (len(invloved_users) / len(store['users']))

    data_store.set(store)

def user_uploadphoto(u_id, img_url, x_start, y_start, x_end, y_end):

    store = data_store.get()

    #check if the x values are valid
    if x_start > x_end:
        raise InputError("Please enter valid dimentions")

    # check if the y values are valid 
    if y_start > y_end:
        raise InputError("Please enter valid dimentions")

    urllib.request.urlretrieve(img_url, f"image{u_id}.jpg")

    imageObject = Image.open(f"image{u_id}.jpg")

    width, height = imageObject.size

    if x_start > width or x_end > width:
        raise InputError("Please enter valid dimentions")

    # check if the y values are valid 
    if y_start > height or y_end > height:
        raise InputError("Please enter valid dimentions")

    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(f"image{u_id}.jpg")

    #save the url to the data store 
    store['users'][u_id]['image_url'] = f'/profilephoto/src/image{u_id}.jpg'

    requests.get(f'{BASE_URL}/profilephoto/src/image{u_id}.jpg')

    data_store.set(store)

