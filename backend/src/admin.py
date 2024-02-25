from src.data_store import data_store
from src.helpers import user_is_valid
from src.error import InputError, AccessError

# Helper functions
def num_global_owners(store):
    num = 0
    for user in store['users']:
        if user['permission_id'] == 1:
            num += 1
    return num

def remove_from_channels_and_dms(store, u_id):

    for channel in store['channels']:
        try:
            channel['all_members'].remove(u_id)
        except:
            pass
        else:
            try:
                channel['owner_members'].remove(u_id)
            except:
                pass

            for message in channel['messages']:
                if message['u_id'] == u_id:
                    message['message'] = "Removed user"

    for dm in store['dms']:
        try:
            dm['members'].remove(u_id)
        except:
            pass
        else:
            for message in dm['messages']:
                if message['u_id'] == u_id:
                    message['message'] = "Removed user"

'''
<admin_user_remove_v1>

Remove a user from all channels and DMs, setting their messages to "Removed user"
Clear their details, and set their name to "Removed user"

Arguments:
    'auth_user_id' (int)    - ID of authorised user performing the user removal
    'u_id' (int)            - ID of user being removed

Exceptions:
    AccessError - Authorised user is not a global owner
    InputError  - User ID is invalid
                - User being removed is the only global owner

Return Value:
    Returns {}
'''
def admin_user_remove_v1(auth_user_id, u_id):

    store = data_store.get()

    if store['users'][auth_user_id]['permission_id'] == 2:
        raise AccessError("Authorised user is not a global owner")
    if not user_is_valid(store, u_id):
        raise InputError("User ID is invalid")
    # The last global owner cannot be removed
    if store['users'][u_id]['permission_id'] == 1 and num_global_owners(store) <= 1:
        raise InputError("User is the only global owner")

    remove_from_channels_and_dms(store, u_id)

    store['users'][u_id] = {
        'email': None,
        'name_first': 'Removed',
        'name_last': 'user',
        'handle_str': None,
        'permission_id': None,
        'sessions': []
    }

    data_store.set(store)

    return {}

'''
<admin_userpermission_change_v1>

Change a user's permissions

Arguments:
    'auth_user_id' (int)    - ID of authorised user changing permissions
    'u_id' (int)            - ID of user having their permissions changed
    'permission_id' (int)   - ID of new permissions being applied

Exceptions:
    AccessError - Authorised user is not a global owner
    InputError  - User ID is invalid
                - User being demoted is the only global owner

Return Value:
    Returns {}
'''
def admin_userpermission_change_v1(auth_user_id, u_id, permission_id):

    store = data_store.get()

    if store['users'][auth_user_id]['permission_id'] == 2:
        raise AccessError("Authorised user is not a global owner")
    if not user_is_valid(store, u_id):
        raise InputError("User ID is invalid")
    # The last global owner cannot be demoted
    if (permission_id == 2 and store['users'][u_id]['permission_id'] == 1
        and num_global_owners(store) <= 1):
        raise InputError("User is the only global owner")
    if not (permission_id == 1 or permission_id == 2):
        raise InputError("Permission ID is invalid")

    store['users'][u_id]['permission_id'] = permission_id
    data_store.set(store)

    return {}
