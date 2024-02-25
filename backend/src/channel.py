from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import channel_is_valid, user_is_valid, user_in_channel, user_is_channel_owner
from src.user import user_stats, users_stats
from src.notifications import notifications_send_v1

# channel_details helper function
def user_details(store, u_id):
    user = store['users'][u_id]
    return {
        'u_id': u_id,
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
    }

'''
<channel_details_v1>

Given a channel with ID channel_id that the authorised user is a member of,
provide basic details about the channel.

Arguments:
    'auth_user_id' (int)   - ID of user in channel
    'channel_id' (int)  - ID of channel

Exceptions:
    InputError  - Channel of 'channel_id' doesn't exist
    AccessError - Channel exists but the authorised user is not a member of it

Return Value:
    Returns {'name', 'is_public', 'owner_members', 'all_members'}
'''
def channel_details_v1(auth_user_id, channel_id):
    # Init
    owner_details_list = []
    member_details_list = []

    store = data_store.get()

    # Test validity of user and channel
    if not channel_is_valid(store, channel_id):
        raise InputError("Channel ID does not refer to a valid channel")
    if not user_in_channel(store, channel_id, auth_user_id):
        raise AccessError("The authorised user is not a member of the channel")

    # Channel name
    channel_name = store['channels'][channel_id]['name']

    # Channel public status
    channel_public_status = store['channels'][channel_id]['is_public']

    # Add details of owner_members to owner list
    for member in store['channels'][channel_id]['owner_members']:
        user_info_dict = user_details(store, member)
        owner_details_list.append(user_info_dict)

    # Add details of all_members to member list
    for member in store['channels'][channel_id]['all_members']:
        user_info_dict = user_details(store, member)
        member_details_list.append(user_info_dict)

    return {
        'name': channel_name,
        'is_public': channel_public_status,
        'owner_members': owner_details_list,
        'all_members': member_details_list
    }

'''
<channel_messages_v1>

Returns a list of maximum 50 messages (type dictionary) as well as the start and
end of the list. The start is determined by the user and if there are less than
50 messages before the start message, the function will return end = -1. Each
message dictionary contains information on the user id of the creator of the
message, the time the messasge is created and the message itself.

Arguments:
    'auth_user_id' (dict)   - Function checks for any message created by user
    'channel_id' (int)  - Function checks for any messages the the user has
                           send in the given channel
    'start' (int)   - Determines range of messages the function will return.
                        0 will be the most recent message

Exceptions:
    AccessError - Occurs when the user attempts to access a channel they are
                   not authorised in
    InputError  - Occurs when the arguments do not meet expected formating
                 (Invalid channel id, invalid start value)

Return Value:
    Returns {'messages', 'start, 'end'}
'''
def channel_messages_v1(auth_user_id, channel_id, start):

    store = data_store.get()

    # Initialise end
    end = 0

    if not channel_is_valid(store, channel_id):
        raise InputError("Invalid channel ID")
    if not user_in_channel(store, channel_id, auth_user_id):
        raise AccessError("User is not authorised in this channel")

    # Checking if end will be at 50 messages
    msg_count = len(store['channels'][channel_id]['messages'])
    if msg_count < start:
        raise InputError("Start is greater than the total number of messages in the channel")

    # The index of the oldest message to be listed, which must not be negative
    first = max(0, msg_count - start - 50)
    # If there are older messages to be displayed, show the end, or else show -1
    if first > 0:
        end = start + 50
    else:
        end = -1

    msg_list = store['channels'][channel_id]['messages'][first: first + 50]
    msg_list.reverse()

    return {'messages': msg_list, 'start': start, 'end': end}

'''
<channel_invite_v1>

Allow an authorised user (channel member) to invite another user into a channel.

Arguments:
    'auth_user_id' (int)   - ID of user in channel
    'channel_id' (int)  - ID of channel the user is being invited to
    'u_id' (int)    - ID of user being invited to channel

Exceptions:
    InputError  - Channel of 'channel_id' doesn't exist
                - User of 'u_id' doesn't exist
                - User of 'u_id' is already in channel
    AccessError - Channel exists but the authorised user is not a member of it

Return Value:
    Returns {}
'''
def channel_invite_v1(auth_user_id, channel_id, u_id):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Invalid channel ID")
    if not user_is_valid(store, u_id):
        raise InputError("Invalid user ID")

    if not user_in_channel(store, channel_id, auth_user_id):
        raise AccessError("User is not authorised in this channel")
    if user_in_channel(store, channel_id, u_id):
        raise InputError("User is already a member of this channel")

    store['channels'][channel_id]['all_members'].append(u_id)

    # Add the data for the stats
    user_stats('channels_joined', auth_user_id, 1) 
    users_stats('channels_exist', auth_user_id, 1)
    
    # Send notification to recipient
    notifications_send_v1('invite_channel', auth_user_id, u_id, channel_id)

    data_store.set(store)

    return {}

'''
<channel_join_v1>

Allow a user to join a channel if it is public.

Arguments:
    'auth_user_id' (int)   - ID of user
    'channel_id' (int)  - ID of channel

Exceptions:
    InputError  - Channel of 'channel_id' doesn't exist
                - User of 'user_id' is already in channel
    AccessError - Channel exists but is private, and the user isn't already a member
                  or a global owner

Return Value:
    Returns {}
'''
def channel_join_v1(auth_user_id, channel_id):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Invalid channel ID")
    if user_in_channel(store, channel_id, auth_user_id):
        raise InputError("User is already a member of this channel")

    if (not store['channels'][channel_id]['is_public']) and (
            store['users'][auth_user_id]['permission_id'] != 1):
        raise AccessError("Channel is private and user is not a global owner")

    store['channels'][channel_id]['all_members'].append(auth_user_id)

    # Add the data for the stats
    user_stats('channels_joined', auth_user_id, 1) 
    users_stats('channels_exist', auth_user_id, 1)

    data_store.set(store)

    return {}

'''
<channel_leave_v1>

Remove a user from a channel

Arguments:
    'auth_user_id' (int)    - ID of user leaving channel
    'channel_id' (int)      - ID of channel being left from
    'permission_id' (int)   - ID of new permissions being applied

Exceptions:
    InputError  - Channel ID is invalid
                - User is not a member of the channel

Return Value:
    Returns {}
'''
def channel_leave_v1(auth_user_id, channel_id):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Invalid channel ID")
    try:
        store['channels'][channel_id]['all_members'].remove(auth_user_id)
    except Exception as e:
        raise AccessError("User is not a member of this channel") from e
    try:
        store['channels'][channel_id]['owner_members'].remove(auth_user_id)
    except:
        pass
    data_store.set(store)

    user_stats('channels_joined', auth_user_id, -1) 
    users_stats('channels_exist', auth_user_id, -1)

    return {}

'''
<channel_addowner_v1>

Add a user as an owner to a channel

Arguments:
    'auth_user_id' (int)    - ID of authorised user adding the new owner
    'channel_id' (int)      - ID of channel with added owner
    'u_id' (int)            - ID of added owner

Exceptions:
    AccessError - Authorised user is not an owner of the channel
    InputError  - Channel ID is invalid
                - User ID is invalid
                - User is not a member of the channel
                - User is already an owner of the channel

Return Value:
    Returns {}
'''
def channel_addowner_v1(auth_user_id, channel_id, u_id):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Invalid channel ID")
    if not user_is_valid(store, u_id):
        raise InputError("Invalid user ID")

    if not user_is_channel_owner(store, channel_id, auth_user_id):
        raise AccessError("User is not authorised in this channel")
    if not user_in_channel(store, channel_id, u_id):
        raise InputError("User is not a member of this channel")
    if user_is_channel_owner(store, channel_id, u_id):
        raise InputError("User is already an owner of this channel")

    store['channels'][channel_id]['owner_members'].append(u_id)
    data_store.set(store)

    return {}

'''
<channel_removeowner_v1>

Remove a user as an owner from a channel

Arguments:
    'auth_user_id' (int)    - ID of authorised user removing the owner
    'channel_id' (int)      - ID of channel with removed owner
    'u_id' (int)            - ID of removed owner

Exceptions:
    AccessError - Authorised user is not an owner of the channel
    InputError  - Channel ID is invalid
                - User ID is invalid
                - User is not an owner of the channel
                - User is the only owner of the channel

Return Value:
    Returns {}
'''
def channel_removeowner_v1(auth_user_id, channel_id, u_id):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Invalid channel ID")
    if not user_is_valid(store, u_id):
        raise InputError("Invalid user ID")

    if not user_is_channel_owner(store, channel_id, auth_user_id):
        raise AccessError("User is not authorised in this channel")
    if not user_is_channel_owner(store, channel_id, u_id):
        raise InputError("User is not an owner of this channel")
    if len(store['channels'][channel_id]['owner_members']) == 1:
        raise InputError("User is the only owner of this channel")

    store['channels'][channel_id]['owner_members'].remove(u_id)
    data_store.set(store)

    return {}
