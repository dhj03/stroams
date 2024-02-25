import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import user_is_valid, dm_is_valid, user_in_dm
from src.user import user_stats, users_stats
from src.notifications import notifications_send_v1

'''
<dm_create_v1>

Create a new DM between a user and a list of other users

Arguments:
    'auth_user_id' (int)    - ID of user creating the DM
    'u_ids' ([int])         - List of IDs of users to be added to the DM

Exceptions:
    InputError  - At least one of the provided IDs is invalid

Return Value:
    Returns {'dm_id'}
'''
def dm_create_v1(auth_user_id, u_ids):

    name_list = []
    members_list = []

    store = data_store.get()
    owner_handle = store['users'][auth_user_id]['handle_str']

    bad_u_id = False

    # Add the owner id and handle into the name_list and member_list
    for user in store['users']:

        if user['handle_str'] == owner_handle:
            name_list.append(owner_handle)
            members_list.append(auth_user_id)

        # Goes through the u_ids list
        for dm_user in u_ids:

            if not user_is_valid(store, dm_user):
                bad_u_id = True
            # Finds the users in the dm
            if dm_user == store['users'].index(user):
                name_list.append(user['handle_str'])
                members_list.append(dm_user)
                break

    if bad_u_id:
        raise InputError("Invalid user ID")

    new_dm_id = len(store['dms'])

    namestring = ', '.join(map(str,sorted(name_list)))

    store['dms'].append({   'name': namestring,
                            'members': members_list,
                            'owner': auth_user_id,
                            'messages': [] })

    data_store.set(store)
    
    # Send notification to recipient
    notifications_send_v1('invite_dm', auth_user_id, u_ids, new_dm_id)  

    #add to stats 
    user_stats('dms_joined', auth_user_id, 1)
    users_stats('dms_exist', auth_user_id, 1)

    return {'dm_id': new_dm_id}

'''
<dm_list_v1>

List all DMs that a user is part of

Arguments:
    'auth_user_id' (int)    - ID of user

Return Value:
    Returns {'dms'}
'''
def dm_list_v1(auth_user_id):

    dms_list = []
    store = data_store.get()

    dm_id = 0
    for dm in store['dms']:
        for member in dm['members']:
            if member == auth_user_id:
                dms_list.append({ 'dm_id': dm_id,
                                    'name': dm['name'] })
                break
        dm_id += 1

    return {'dms': dms_list}

'''
<dm_remove_v1>

Remove an existing DM, so all members are no longer in the DM
This can only be done by the original creator of the DM

Arguments:
    'auth_user_id' (int)    - ID of user removing the DM
    'dm_id' (int)           - ID of DM being removed

Exceptions:
    InputError  - At least one of the provided IDs is invalid

Return Value:
    Returns {}
'''
def dm_remove_v1(auth_user_id, dm_id):

    store = data_store.get()

    if not dm_is_valid(store, dm_id):
        raise InputError("Invalid DM")

    valid_owner = False

    for dm in store['dms']:
        if auth_user_id == dm['owner'] and dm_id == store['dms'].index(dm):
            valid_owner = True
            store['dms'].remove(dm)
            break

    if not valid_owner:
        raise AccessError("Unauthorised User")

    data_store.set(store)

    user_stats('dms_joined', auth_user_id, -1)
    users_stats('dms_exist', auth_user_id, -1)

    return {}

'''
<dm_details_v1>

Show basic details about a DM where the user is part of it

Arguments:
    'auth_user_id' (int)    - ID of user in DM
    'dm_id' (int)           - ID of DM

Exceptions:
    InputError  - Invalid DM ID
    AccessError - User is not a member of the DM

Return Value:
    Returns {'name', 'members'}
'''
def dm_details_v1(auth_user_id, dm_id):

    store = data_store.get()

    if not dm_is_valid(store, dm_id):
        raise InputError("Invalid DM")
    if not user_in_dm(store, dm_id, auth_user_id):
        raise AccessError("Unauthorised User")

    dm_list = []

    for member in store['dms'][dm_id]['members']:
        dm_list.append({
            'u_id': member,
            'email': store['users'][member]['email'],
            'name_first': store['users'][member]['name_first'],
            'name_last': store['users'][member]['name_last']
        })

    return {
        'name': store['dms'][dm_id]['name'],
        'members': dm_list
    }

'''
<dm_leave_v1>

Leave a DM, which will continue to exist with the same name even without owners or members

Arguments:
    'auth_user_id' (int)    - ID of user leaving the DM
    'dm_id' (int)           - ID of DM being left from

Exceptions:
    InputError  - Invalid ID of DM
    AccessError - User is not a member of the DM

Return Value:
    Returns {}
'''
def dm_leave_v1(auth_user_id, dm_id):

    store = data_store.get()

    if not dm_is_valid(store, dm_id):
        raise InputError("Invalid DM")
    valid_member = False
    for dm in store['dms']:
        for member in dm['members']:
            if member == auth_user_id and dm_id == store['dms'].index(dm):
                valid_member = True
                store['dms'][dm_id]['members'].remove(member)
                break

    if not valid_member:
        raise AccessError("Unauthorised User")

    data_store.set(store)
    
    #update the user statistics 
    user_stats('dms_joined', auth_user_id, -1)
    users_stats('dms_exist', auth_user_id, -1)

    return {}

'''
<dm_messages_v1>

Returns a list of maximum 50 messages (type dictionary) as well as the start and
end of the list. The start is determined by the user and if there are less than
50 messages before the start message, the function will return end = -1. Each
message dictionary contains information on the user id of the creator of the
message, the time the messasge is created and the message itself.

Arguments:
    'auth_user_id' (int)    - ID of user in the DM
    'dm_id' (int)           - ID of DM
    'start' (int)           - The number of most-recent messages to skip in retrieval

Exceptions:
    InputError  - Invalid ID of DM
                - The start number is larger than the total number of messages in the DM
    AccessError - User is not a member of the DM

Return Value:
    Returns {'messages', 'start', 'end'}
'''
def dm_messages_v1(auth_user_id, dm_id, start):

    store = data_store.get()

    # Initialize end
    end = 0

    # Check if dm_id is valid
    if not dm_is_valid(store, dm_id):
        raise InputError("Invalid DM")

    # Check if user is a member
    if not user_in_dm(store, dm_id, auth_user_id):
        raise AccessError("Unauthorised User")

    # Checking if end will be at 50 messages
    msg_count = len(store['dms'][dm_id]['messages'])
    if msg_count < start:
        raise InputError("Start is greater than the total number of messages in the channel")

    # The index of the oldest message to be listed, which must not be negative
    first = max(0, msg_count - start - 50)
    # If there are older messages to be displayed, show the end, or else show -1
    if first > 0:
        end = start + 50
    else:
        end = -1

    msg_list = store['dms'][dm_id]['messages'][first: first + 50]
    msg_list.reverse()

    return {'messages': msg_list, 'start': start, 'end': end}
