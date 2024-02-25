from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import user_is_valid
from src.user import user_stats, users_stats

'''
<channels_list_v1>

Provide a list of all channels, that the authorised user is part of (and their associated details)

Arguments:
    'auth_user_id' (dict)   - User ID needed to access the command

Return Value:
    Returns {'channels'}
'''
def channels_list_v1(auth_user_id):

    channels_list = []
    store = data_store.get()

#    if not user_is_valid(store, auth_user_id):
#        raise AccessError("User ID is not registered")

    channel_id = 0
    for channel in store['channels']:
        for member in channel['all_members']:
            if member == auth_user_id:
                channels_list.append({  'channel_id': channel_id,
                                        'name': channel['name'] })
                break
        channel_id += 1

    return {'channels': channels_list}

'''
<channels_listall_v1>

Provide a list of all channels, including private channels, (and their associated details)

Arguments:
    'auth_user_id' (dict)   - User ID needed to access the command

Return Value:
    Returns {'channels'}
'''
def channels_listall_v1(auth_user_id):

    channels_listall = []
    store = data_store.get()

#    if not user_is_valid(store, auth_user_id):
#        raise AccessError("User ID is not registered")

    channel_id = 0
    for channel in store['channels']:
        channels_listall.append({   'channel_id': channel_id,
                                    'name': channel['name'] })
        channel_id += 1

    return {'channels': channels_listall}

'''
<channels_create_v1>

User creates a channel and are designated the creator of that channel. The
channel's name is determined by the creator and whether it is public or private.
The creator is automatically added to that channel.

Arguments:
    'auth_user_id' (dict)   - User ID needed to create the channel
    'name' (string) - The name of the created channel
    'is_public' (string)    - Determines if the created channel with be public
                             or private

Exceptions:
    InputError - Occurs when the arguments do not meet expected formating (name
                 size error, duplicate channel or invalid privacy input)

Return Value:
    Returns {'new_channels_id'} on creation of channel
'''
def channels_create_v1(auth_user_id, name, is_public):

    store = data_store.get()

#    if not user_is_valid(store, auth_user_id):
#        raise AccessError("User ID is not registered")

    for channel in store['channels']:
        if name == channel['name']:
            raise InputError("Duplicate channel name")

    if len(name) == 0 or len(name) > 20:
        raise InputError("Name must be between 1 and 20 characters inclusive")

    new_channel_id = len(store['channels'])

    if not type(is_public) is bool:
        raise InputError("Invalid privacy type")



    # If everything is correct, create channel in data_store
    store['channels'].append({  'name': name,
                                'is_public': is_public,
                                'owner_members': [auth_user_id],
                                'all_members': [auth_user_id],
                                'messages': [],
                                'standup': {
                                    'time_finish': None,
                                    'messages': []
                                }
                            })

    data_store.set(store)

    #Add the data for the stats
    user_stats('channels_joined', auth_user_id, 1) 
    users_stats('channels_exist', auth_user_id, 1)
    
    return {'channel_id': new_channel_id}
