from src.data_store import data_store
from datetime import timezone, datetime
from src.error import InputError, AccessError
from src.helpers import channel_is_valid, user_in_channel, dm_is_valid, user_in_dm
from src.helpers import user_is_channel_owner
from src.user import user_stats, users_stats
import src.notifications as notif
import threading

# A helper function to send the dm later
def dmhelper(auth_user_id, dm_id, message, message_number):
    # Get the time the function was called and convert it to unix utc
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    store = data_store.get()
    store['dms'][dm_id]['messages'].append({    'message_id': message_number,
                                                'u_id' : auth_user_id,
                                                'message': message,
                                                'time_created': time,
                                                'reacts': [],
                                                'is_pinned': False})

    # Check if message contains tag
    tagged_user = is_user_tagged(store['message_num'])
    if tagged_user != None:
        notif.notifications_send_v1('tag', auth_user_id, tagged_user, message_number)

    data_store.set(store)

# A helper function to send the message later
def channelhelper(auth_user_id, channel_id, message, message_number):
    # Get the time the function was called and convert it to unix utc
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    store = data_store.get()
    store['channels'][channel_id]['messages'].append({  'message_id': message_number,
                                                        'u_id' : auth_user_id,
                                                        'message': message,
                                                        'time_created': time,
                                                        'reacts': [],
                                                        'is_pinned': False})
    # Check if message contains tag
    tagged_user = is_user_tagged(store['message_num'])
    if tagged_user != None:
        notif.notifications_send_v1('tag', auth_user_id, tagged_user, message_number)

    data_store.set(store)

# A helper function that finds a message's location
def locate_message(store, message_id):

    channel_id = 0
    for channel in store['channels']:
        ch_msg_id = 0
        for messages in channel['messages']:
            if messages['message_id'] == message_id:
                return ('channels', channel_id, ch_msg_id)
            ch_msg_id += 1
        channel_id += 1

    dm_id = 0
    for dm in store['dms']:
        dm_msg_id = 0
        for messages in dm['messages']:
            if messages['message_id'] == message_id:
                return ('dms', dm_id, dm_msg_id)
            dm_msg_id += 1
        dm_id += 1

    return (None, None, None)

def is_user_tagged(message_id):
    store = data_store.get()

    # Locate the message, if message is not located then message_id is invalid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type is None:
        raise InputError("Message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    u_id = 0
    for user in store['users']:
        if user['handle_str'] in store[loc_type][loc_id]['messages'][loc_msg_id]['message']:

            # if loc_type is 'dms':
            #     # Check if user is in the dm
            #     if not user_in_dm(store, loc_id, user):
            #         raise AccessError("dm_id is valid and the authorised user is not a member of the dm TAGGED")

            # if loc_type is 'channels':
            #     # Check if user is in the channel
            #     if not user_in_channel(store, loc_id, user):
            #         raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

            data_store.set(store)
            return u_id

        u_id += 1

    data_store.set(store)
    return None

'''
<message_send_v1>

Send a message from the authorised user to the channel specified by channel_id.
Note: Each message should have its own unique ID,
i.e. no messages should share an ID with another message,
even if that other message is in a different channel.

Arguments:
    'auth_user_id' (int)    - ID of authorised user
    'channel_id' (int)      - ID of channel
    'message' (str)         - Message to be sent

Exceptions:
    AccessError - Channel_id is valid and the authorised user is not a member of the channel
    InputError  - Channel_id does not refer to a valid channel
                - Length of message is less than 1 or over 1000 characters

Return Value:
    Returns {'message_id'}
'''
def message_send_v1(auth_user_id, channel_id, message):

    store = data_store.get()

    # Check if channel is a valid channel
    if not channel_is_valid(store, channel_id):
        raise InputError("Channel ID does not refer to a valid channel")

    # Check if user is authorised in that channel
    if not user_in_channel(store, channel_id, auth_user_id):
        raise AccessError("Channel_id is valid and the authorised user is not a member of the channel")

    # Check the length of the message
    if not 1 <= len(message) <= 1000:
        raise InputError("Length of message is less than 1 or over 1000 characters")

    # Get the time the function was called and convert it to unix utc
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    # If everything is correct, append the message to the data_store
    store['message_num'] += 1
    store['channels'][channel_id]['messages'].append({  'message_id': store['message_num'],
                                                        'u_id' : auth_user_id,
                                                        'message': message,
                                                        'time_created': time,
                                                        'reacts': [],
                                                        'is_pinned': False})
    data_store.set(store)

    # Check if message contains tag
    tagged_user = is_user_tagged(store['message_num'])
    if tagged_user != None:
        notif.notifications_send_v1('tag', auth_user_id, tagged_user, store['message_num'])

    # Add to stats
    user_stats('messages_sent', auth_user_id, 1)
    users_stats('messages_exist', auth_user_id, 1)

    return {'message_id': store['message_num']}

'''
<message_edit_v1>

Given a message, update its text with new text.
If the new message is an empty string, the message is deleted.

Arguments:
    'auth_user_id' (int)    - ID of authorised user
    'message_id' (int)      - ID of message on channel
    'message' (str)         - Message to edit and replace current message

Exceptions:
    AccessError - When message_id refers to a valid message in a joined channel/DM and none
                  of the following are true:
                    - The message was sent by the authorised user making this request
                    - The authorised user has owner permissions in the channel/DM

    InputError  - Message_id does not refer to a valid message within a channel/DM that the
                  authorised user has joined
                - Length of message is less than 1 or over 1000 characters

Return Value:
    Returns {}
'''
def message_edit_v1(auth_user_id, message_id, message):

    store = data_store.get()

    # Locate the message, if message is not located then message_id is invalid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type is None:
        raise InputError("Message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    # Check for permission to edit
    sent_check = False
    authorised_check = False

    if store[loc_type][loc_id]['messages'][loc_msg_id]['u_id'] == auth_user_id:
        sent_check = True

    if ((loc_type == 'dms' and store['dms'][loc_id]['owner'] == auth_user_id)
    or (loc_type == 'channels' and user_is_channel_owner(store, loc_id, auth_user_id))):
        authorised_check = True

    if not (sent_check or authorised_check):
        raise AccessError("User is neither authorised nor message owner")

    # Check the length of the message
    length = len(message)

    if length > 100:
        raise InputError("Length of message is less than 1 or over 1000 characters")
    elif length <= 0:
        store[loc_type][loc_id]['messages'].pop(loc_msg_id)
    else:
        store[loc_type][loc_id]['messages'][loc_msg_id]['message'] = message

    data_store.set(store)

    # Check if message contains tag
    tagged_user = is_user_tagged(message_id)
    if tagged_user != None:
        notif.notifications_send_v1('tag', auth_user_id, tagged_user, message_id)

    return {}

'''
<message_remove_v1>

Given a message_id for a message, this message is removed from the channel/DM

Arguments:
    'auth_user_id' (int)    - ID of authorised user
    'message_id' (int)      - ID of message on channel

Exceptions:
    AccessError - When message_id refers to a valid message in a joined channel/DM and none
                  of the following are true:
                    - The message was sent by the authorised user making this request
                    - The authorised user has owner permissions in the channel/DM

    InputError  - Message_id does not refer to a valid message within a channel/DM that the
                  authorised user has joined

Return Value:
    Returns {}
'''
def message_remove_v1(auth_user_id, message_id):

    store = data_store.get()

    # Locate the message, if message is not located then message_id is invalid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type is None:
        raise InputError("Message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    # Checking for if the user is allowed to edit the message
    sent_check = False
    authorised_check = False

    # Check if the user is the user that sent the message
    if store[loc_type][loc_id]['messages'][loc_msg_id]['u_id'] == auth_user_id:
        sent_check = True

    # Check if the user is admin or global owner
    if ((loc_type == 'dms' and store['dms'][loc_id]['owner'] == auth_user_id)
    or (loc_type == 'channels' and user_is_channel_owner(store, loc_id, auth_user_id))):
        authorised_check = True

    if not (sent_check or authorised_check):
        raise AccessError("User is neither authorised nor message owner")
    else:
        store[loc_type][loc_id]['messages'].pop(loc_msg_id)

    data_store.set(store)

    users_stats('messages_exist', auth_user_id, -1)

    return {}

'''
<message_senddm_v1>

Send a message from authorised_user to the DM specified by dm_id.
Note: Each message should have it's own unique ID,
i.e. no messages should share an ID with another message,
even if that other message is in a different channel or DM.

Arguments:
    'auth_user_id' (int)    - ID of authorised user
    'dm_id' (int)           - ID of dm
    'message' (str)         - Message to be sent

Exceptions:
    AccessError - When dm_id is valid and the authorised user is not a member of the DM

    InputError  - When dm_id does not refer to a valid DM
                - Length of message is less than 1 or over 1000 characters

Return Value:
    Returns {'message_id'}
'''
def message_senddm_v1(auth_user_id, dm_id, message):

    store = data_store.get()

    # Check if dm_id is valid
    if not dm_is_valid(store, dm_id):
        raise InputError("dm_id does not refer to a valid DM")

    # Check if user is in the dm
    if not user_in_dm(store, dm_id, auth_user_id):
        raise AccessError("dm_id is valid and the authorised user is not a member of the DM")

    # Check the length of the message
    if not 1 <= len(message) <= 1000:
        raise InputError("Length of message is less than 1 or over 1000 characters")

    # Get the time the function was called and convert it to unix utc
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    # If everything is correct, send the message
    store['message_num'] += 1
    store['dms'][dm_id]['messages'].append({'message_id': store['message_num'],
                                            'u_id' : auth_user_id,
                                            'message': message,
                                            'time_created': time,
                                            'reacts': [],
                                            'is_pinned': False})
    data_store.set(store)

    # Check if message contains tag
    tagged_user = is_user_tagged(store['message_num'])
    if tagged_user != None:
        notif.notifications_send_v1('tag', auth_user_id, tagged_user, store['message_num'])

    # Add to stats
    user_stats('messages_sent', auth_user_id, 1)
    users_stats('messages_exist', auth_user_id, 1)

    return {'message_id': store['message_num']}

'''
<message_share_v1>

The og_message_id is the ID of the original message. channel_id is the channel that the message is being shared to,
and is -1 if it is being sent to a DM. dm_id is the DM that the message is being shared to,
and is -1 if it is being sent to a channel. message is the optional message in addition to the shared message,
and will be an empty string '' if no message is given.

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'og_message_id' (int)   - ID of original message
    'message'       (str)   - Optional message in addition to the shared message
    'channel_id'    (int)   - ID of channel
    'dm_id'         (int)   - ID of channel

Exceptions:
    AccessError - The pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and
                  the authorised user has not joined the channel or DM they are trying to share the message to.

    InputError  - Both channel_id and dm_id are invalid.
                - Neither channel_id nor dm_id are -1.
                - The og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined.
                - Length of message is more than 1000 characters.

Return Value:
    Returns {'shared_message_id'}
'''
def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):

    store = data_store.get()

    # Check if id's are either both -1 or both not -1
    if channel_id != -1 and dm_id != -1:
        raise InputError("channel_id and dm_id are both not -1")

    # Check if id's are both -1
    if channel_id == -1 and dm_id == -1:
        raise InputError("channel_id and dm_id are both -1")

    # If inputs are correct, check if id's are valid
    if channel_id is -1:
        # Check if dm_id is valid
        if not dm_is_valid(store, dm_id):
            raise InputError("dm_id does not refer to a valid dm")
        # Check if user is in the dm
        if not user_in_dm(store, dm_id, auth_user_id):
            raise AccessError("dm_id is valid and the authorised user is not a member of the dm SHARE")
    if dm_id is -1:
        # Check if channel_id is valid
        if not channel_is_valid(store, channel_id):
            raise InputError("channel_id does not refer to a valid channel")
        # Check if user is in the channel
        if not user_in_channel(store, channel_id, auth_user_id):
            raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

    # Check the length of the message
    if not len(message) <= 1000:
        raise InputError("Length of message is more than 1000 characters.")

    # Check the og message is valid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, og_message_id)
    if loc_type == None:
        raise InputError("The og_message_id does not refer to a valid message")

    # Check if user is in the dm/channel that the original message is in
    check = False
    if loc_type == 'dms':
        for member in store[loc_type][loc_id]['members']:
            if member == auth_user_id:
                check = True
    if loc_type == 'channels':
        for member in store[loc_type][loc_id]['all_members']:
            if member == auth_user_id:
                check = True
    if check == False:
        raise AccessError("User does not have access to that message")

    og_message = store[loc_type][loc_id]['messages'][loc_msg_id]['message']

    shared_message = f"{og_message} {message}"

    # Check whether being shared to a dm or channel
    if dm_id is not -1:
        message_senddm_v1(auth_user_id, dm_id, shared_message)
    if channel_id is not -1:
        message_send_v1(auth_user_id, channel_id, shared_message)

    data_store.set(store)

    # # Check if message contains tag
    # tagged_user = is_user_tagged(store['message_num'])
    # if tagged_user != None:
    #     notif.notifications_send_v1('tag', auth_user_id, tagged_user, store['message_num'])


    return {'shared_message_id': store['message_num']}

'''
<message_react_v1>

Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.

NOTE: "The only React ID currently associated with the frontend is React ID 1, which is a thumbs up.
       You are welcome to add more (this will require some frontend work)."

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'message_id'    (int)   - ID of message
    'react_id'      (int)   - ID of reaction

Exceptions:
    InputError  - Message_id is not a valid message within a channel or DM that the authorised user has joined
                - React_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
                - The message already contains a react with ID react_id from the authorised user

Return Value:
    Returns {}
'''
def message_react_v1(auth_user_id, message_id, react_id):

    store = data_store.get()

    # Locate the message, if message is not located then message_id is invalid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type is None:
        raise InputError("Message ID does not refer to a valid message")

    if loc_type is 'dms':
        dm_id = loc_id
        # Check if user is in the dm
        if not user_in_dm(store, dm_id, auth_user_id):
            raise AccessError("dm_id is valid and the authorised user is not a member of the dm REACT")
    else:
        channel_id = loc_id
        # Check if user is in the channel
        if not user_in_channel(store, channel_id, auth_user_id):
            raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

    # Check react_id is valid, (equal to one, as only reaction available right now)
    if not react_id == 1:
        raise InputError("React_id is not a valid react ID")

    dir_react = store[loc_type][loc_id]['messages'][loc_msg_id]['reacts']

    # Check if the message is already reacted by user
    for user in dir_react:
        for key in user:
            if key == auth_user_id:
                raise InputError("The message already contains a react with ID react_id from the authorised user")

    dir_react.append({auth_user_id: 1})
    
    data_store.set(store)
    
    # Send notification to user of reacted message
    recipient = store[loc_type][loc_id]['messages'][loc_msg_id]['u_id']
    notif.notifications_send_v1('react', auth_user_id, recipient, message_id)

    

    return {}
'''
<message_unreact_v1>

Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'message_id'    (int)   - ID of message
    'react_id'      (int)   - ID of reaction

Exceptions:
    InputError  - Message_id is not a valid message within a channel or DM that the authorised user has joined
                - React_id is not a valid react ID
                - The message does not contain a react with ID react_id from the authorised user

Return Value:
    Returns {}
'''
def message_unreact_v1(auth_user_id, message_id, react_id):

    store = data_store.get()

    # Locate the message, if message is not located then message_id is invalid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type is None:
        raise InputError("Message ID does not refer to a valid message")

    if loc_type is 'dms':
        dm_id = loc_id
        # Check if user is in the dm
        if not user_in_dm(store, dm_id, auth_user_id):
            raise AccessError("dm_id is valid and the authorised user is not a member of the dm UNREACT")
    else:
        channel_id = loc_id
        # Check if user is in the channel
        if not user_in_channel(store, channel_id, auth_user_id):
            raise AccessError("channel_id is valid and the authorised user is not a member of the channel")


    # Check react_id is valid, (equal to one, as only reaction available right now)
    if not react_id == 1:
        raise InputError("React_id is not a valid react ID")


    dir_react = store[loc_type][loc_id]['messages'][loc_msg_id]['reacts']

    # Check if the message is already reacted by user
    flag = 0

    counter = 0
    for user in dir_react:
        for key in user:
            if key == auth_user_id:
                flag = 1
                del dir_react[counter]
                break
            else:
                counter += 1

    if flag == 0:
        raise InputError("The message does not contain a react with ID react_id from the authorised user")



    data_store.set(store)

    return {}

'''
<message_pin_v1>

Given a message within a channel or DM, mark it as "pinned".

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'message_id'    (int)   - ID of message

Exceptions:
    AccessError - Message_id refers to a valid message in a joined channel/DM and
                  the authorised user does not have owner permissions in the channel/DM

    InputError  - Message_id is not a valid message within a channel or DM that the authorised user has joined
                - The message is already pinned

Return Value:
    Returns {}
'''
def message_pin_v1(auth_user_id, message_id):

    store = data_store.get()

    # Check if message_id is valid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type == None:
        raise InputError("The message_id does not refer to a valid message")

    # Check if the user is admin or global owner
    authorised_check = False
    if ((loc_type == 'dms' and store['dms'][loc_id]['owner'] == auth_user_id)
    or (loc_type == 'channels' and user_is_channel_owner(store, loc_id, auth_user_id))):
        authorised_check = True
    if authorised_check == False:
        raise AccessError("The user is not an authorised user")

    # Check if the message is already pined
    if store[loc_type][loc_id]['messages'][loc_msg_id]['is_pinned'] == True:
        raise InputError("Message is already pinned")

    store[loc_type][loc_id]['messages'][loc_msg_id]['is_pinned'] = True

    data_store.set(store)

    return {}

'''
<message_unpin_v1>

Given a message within a channel or DM, remove its mark as pinned.

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'message_id'    (int)   - ID of message

Exceptions:
    AccessError - Message_id refers to a valid message in a joined channel/DM and
                  the authorised user does not have owner permissions in the channel/DM

    InputError  - Message_id is not a valid message within a channel or DM that the authorised user has joined
                - The message is not already pinned

Return Value:
    Returns {}
'''
def message_unpin_v1(auth_user_id, message_id):

    store = data_store.get()

    # Check if message_id is valid
    (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
    if loc_type == None:
        raise InputError("The message_id does not refer to a valid message")

    # Check if the user is admin or global owner
    authorised_check = False
    if ((loc_type == 'dms' and store['dms'][loc_id]['owner'] == auth_user_id)
    or (loc_type == 'channels' and user_is_channel_owner(store, loc_id, auth_user_id))):
        authorised_check = True
    if authorised_check == False:
        raise AccessError("The user is not an authorised user")

    # Check if the message is already pined
    if store[loc_type][loc_id]['messages'][loc_msg_id]['is_pinned'] == False:
        raise InputError("Message is already pinned")

    store[loc_type][loc_id]['messages'][loc_msg_id]['is_pinned'] = False

    data_store.set(store)

    return {}


'''
<message_sendlater_v1>

Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future.

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'channel_id'    (int)   - ID of channel
    'message'       (str)   - Message to be sent
    'time_sent'     (str)   - Time message was sent

Exceptions:
    AccessError - Channel_id is valid and the authorised user is not a member of the channel they are trying to post to

    InputError  - Channel_id does not refer to a valid channel
                - Length of message is not over 1000 characters
                - Time_sent is a time in the past

Return Value:
    Returns {'message_id'}
'''
def message_sendlater_v1(auth_user_id, channel_id, message, time_sent):

    store = data_store.get()

    # Check the length of the message
    if not len(message) <= 1000:
        raise InputError("Length of message is over 1000 characters")

    # Check if channel is a valid channel
    if not channel_is_valid(store, channel_id):
        raise InputError("Channel_id does not refer to a valid channel")

    # Check if user is authorised in that channel
    if not user_in_channel(store, channel_id, auth_user_id):
        raise AccessError("Channel_id is valid but the user is not an authorised member")

    # Get the time
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    # Check if time_sent is a time in the past
    if time_sent < time:
        raise InputError("time_sent is a time in the past")

    # If no error has have been raised, send the message at designated time
    time_diff = float(time_sent - time)
    store['message_num'] += 1
    sendlater = threading.Timer(time_diff, channelhelper, [auth_user_id, channel_id, message, store['message_num']])
    sendlater.start()

    data_store.set(store)

    user_stats('messages_sent', auth_user_id, 1)
    users_stats('messages_exist', auth_user_id, 1)

    return {'message_id': store['message_num']}
'''
<message_sendlaterdm_v1>

Send a message from the authorised user to the DM specified by dm_id automatically at a specified time in the future.

Arguments:
    'auth_user_id'  (int)   - ID of authorised user
    'dm_id'         (int)   - ID of dm
    'message'       (str)   - Message to be sent
    'time_sent'     (str)   - Time message was sent

Exceptions:
    AccessError - Channel_id is valid and the authorised user is not a member of the channel they are trying to post to

    InputError  - Channel_id does not refer to a valid channel
                - Length of message is less than 1 or over 1000 characters
                - Time_sent is a time in the past

Return Value:
    Returns {'message_id'}
'''
def message_sendlaterdm_v1(auth_user_id, dm_id, message, time_sent):

    store = data_store.get()

    # Check the length of the message
    if not len(message) <= 1000:
        raise InputError("Length of message is over 1000 characters")

    # Check if dm is a valid dm
    if not dm_is_valid(store, dm_id):
        raise InputError("Dm_id does not refer to a valid dm")

    # Check if user is authorised in that dm
    if not user_in_dm(store, dm_id, auth_user_id):
        raise AccessError("Dm_id is valid but the user is not an authorised member")

    # Get the time
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    # Check if time_sent is a time in the past
    if time_sent < time:
        raise InputError("time_sent is a time in the past")

    # If no error has have been raised, send the message at designated time
    time_diff = float(time_sent - time)
    store['message_num'] += 1
    sendlater = threading.Timer(time_diff, dmhelper, [auth_user_id, dm_id, message, store['message_num']])
    sendlater.start()
    data_store.set(store)

    return {'message_id': store['message_num']}
