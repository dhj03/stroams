import threading
from src.data_store import data_store
from datetime import timezone, datetime
from src.error import InputError, AccessError
from src.helpers import channel_is_valid, user_in_channel, dm_is_valid, user_in_dm
from src.helpers import user_is_channel_owner
from src.user import user_stats, users_stats

'''
<standup_start_v1>

Start a standup period in a given channel for a given number of seconds.
Once the period is over, all messages in the standup buffer are flushed into the channel.

Arguments:
    'u_id' (int)        - ID of user
    'channel_id' (int)  - ID of channel
    'length' (int)      - Length of standup period in seconds

Exceptions:
    InputError  - Channel ID does not refer to a valid channel
                - Length is a negative integer
                - An active standup is currently running in the channel
    AccessError - User is not a member of the channel

Return Value:
    {'time_finish'}
'''
def standup_start_v1(u_id, channel_id, length):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Channel ID does not refer to a valid channel")
    if u_id not in store['channels'][channel_id]['all_members']:
        raise AccessError("User is not a member of the channel")
    if length < 0:
        raise InputError("Length is a negative integer")

    standup = store['channels'][channel_id]['standup']
    if standup['time_finish'] is not None:
        raise InputError("An active standup is currently running in the channel")

    time = int(datetime.now(timezone.utc).timestamp())
    standup['time_finish'] = time + length

    # End the standup
    thread = threading.Timer(length, standup_end, [u_id, channel_id])
    thread.start()

    data_store.set(store)

    return {'time_finish': standup['time_finish']}

'''
<standup_active_v1>

Return whether or not a standup is active in a given channel, and if so when it finishes.
If no standup is active in said channel, 'time_finish' returns None.

Arguments:
    'u_id' (int)        - ID of user
    'channel_id' (int)  - ID of channel

Exceptions:
    InputError  - Channel ID does not refer to a valid channel
    AccessError - User is not a member of the channel

Return Value:
    {'is_active', 'time_finish'}
'''
def standup_active_v1(u_id, channel_id):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Channel ID does not refer to a valid channel")
    if u_id not in store['channels'][channel_id]['all_members']:
        raise AccessError("User is not a member of the channel")

    time_finish = store['channels'][channel_id]['standup']['time_finish']
    if time_finish is not None:
        is_active = True
    else:
        is_active = False

    return {'is_active': is_active, 'time_finish': time_finish}

'''
<standup_send_v1>

Send a message to be buffered in the standup queue, if one is currently active

Arguments:
    'u_id' (int)        - ID of user
    'channel_id' (int)  - ID of channel
    'message' (str)     - String of message

Exceptions:
    InputError  - Channel ID does not refer to a valid channel
                - Length of message is over 1000 characters
                - An active standup is not currently running in the channel
    AccessError - User is not a member of the channel

Return Value:
    {}
'''
def standup_send_v1(u_id, channel_id, message):

    store = data_store.get()

    if not channel_is_valid(store, channel_id):
        raise InputError("Channel ID does not refer to a valid channel")
    if u_id not in store['channels'][channel_id]['all_members']:
        raise AccessError("User is not a member of the channel")
    if len(message) > 1000:
        raise InputError("Length of message is over 1000 characters")
    if store['channels'][channel_id]['standup']['time_finish'] is None:
        raise InputError("An active standup is not currently running in the channel")

    store['channels'][channel_id]['standup']['messages'].append(
        f"{store['users'][u_id]['handle_str']}: {message}"
    )

    data_store.set(store)

    return {}

def standup_end(u_id, channel_id):

    store = data_store.get()
    channel = store['channels'][channel_id]

    standup_message = ""
    for message in channel['standup']['messages']:
        standup_message += message + '\n'
    standup_message = standup_message[:-1]

    store['message_num'] += 1
    time = int(datetime.now(timezone.utc).timestamp())

    channel['messages'].append({'message_id': store['message_num'],
                                'u_id' : u_id,
                                'message': standup_message,
                                'time_created': time})

    user_stats('messages_sent', u_id, 1)
    users_stats('messages_exist', u_id, 1)

    channel['standup']['time_finish'] = None
    channel['standup']['messages'].clear()

    data_store.set(store)
