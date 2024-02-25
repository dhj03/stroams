from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import locate_message

'''
<notifications_send_v1>

Helper fucntion
Processes and stores notification in user data store.

List of dictionaries, where each dictionary contains types { channel_id, dm_id, notification_message } 
where channel_id is the id of the channel that the event happened in, and is -1 if it is being sent to a DM. 
dm_id is the DM that the event happened in, and is -1 if it is being sent to a channel. 
Notification_message is a string of the following format for each trigger action:
      
        - tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
        - reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
        - added to a channel/DM: "{User’s handle} added you to {channel/DM name}"

Arguments:
    'function_type' (str)    - Function identifier string
    'sender'        (dict)   - Dictionary of user sender
    'recipient'     (dict)   - Dictionary of user recipient
    'chosen_id'     (int)    - Depending on function type, acts as message_id, channel_id or dm_id

Exceptions:
    N/A

Return Value:
    Null
'''
def notifications_send_v1(function_type, sender, recipient, chosen_id):
    store = data_store.get()

    # tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
    if function_type is 'tag':
        message_id = chosen_id
        (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
        if loc_type is 'dms':
            dm_id = 1
            channel_id = -1
        elif loc_type is 'channels':
            dm_id = -1
            channel_id = 1

        user_handle = store['users'][sender]['handle_str']  
        name = store[loc_type][loc_id]['name']
        message = store[loc_type][loc_id]['messages'][loc_msg_id]['message']
        notification_message = f"{user_handle} tagged you in {name}: {message[0:19]}"

        store['users'][recipient]['notifications'].append({ 'channel_id':channel_id,
                                                            'dm_id':dm_id,
                                                            'notification_message': notification_message})
    
    # reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
    elif function_type is 'react':
        message_id = chosen_id
        (loc_type, loc_id, loc_msg_id) = locate_message(store, message_id)
        if loc_type is 'dms':
            dm_id = 1
            channel_id = -1
        elif loc_type is 'channels':
            dm_id = -1
            channel_id = 1

        user_handle = store['users'][sender]['handle_str']  
        name = store[loc_type][loc_id]['name']
        notification_message = f"{user_handle} reacted to your message in {name}"

        store['users'][recipient]['notifications'].append({ 'channel_id':channel_id,
                                                            'dm_id':dm_id,
                                                            'notification_message': notification_message})

    # added to a channel/DM: "{User’s handle} added you to {channel/DM name}"
    elif function_type is 'invite_dm':
        loc_id = chosen_id
        loc_type = 'dms'
        dm_id = 1
        channel_id = -1
        
        user_handle = store['users'][sender]['handle_str']       
        name = store[loc_type][loc_id]['name']
        notification_message = f"{user_handle} added you to {name}"

        for user in recipient:
            store['users'][user]['notifications'].append({ 'channel_id':channel_id,
                                                                'dm_id':dm_id,
                                                                'notification_message': notification_message})
    elif function_type is 'invite_channel':
        loc_id = chosen_id
        loc_type = 'channels'
        dm_id = -1
        channel_id = 1

        user_handle = store['users'][sender]['handle_str']  
        name = store[loc_type][loc_id]['name']
        notification_message = f"{user_handle} added you to {name}"

        store['users'][recipient]['notifications'].append({ 'channel_id':channel_id,
                                                            'dm_id':dm_id,
                                                            'notification_message': notification_message})

    else:
        print(function_type[0:6])
        raise InputError("Invalid function type")
    data_store.set(store)


'''
<notifications_get_v1>

Return the user's most recent 20 notifications, ordered from most recent to least recent.

Arguments:
    'auth_user_id' (int)    - ID of authorised user

Exceptions:
    N/A

Return Value:
    Return {'notifications'}

    Return example: 
    [
        {
            channel_id: -1,
            dm_id: 1,
            notification_message:(string format above in send)
        },
        {
            channel_id: 1,
            dm_id: -1,
            notification_message:(string format above in send)
        }
    ]
'''

def notifications_get_v1(auth_user_id):
    
    store = data_store.get()
    user_notifications = store['users'][auth_user_id]['notifications'][0:19]
    user_notifications.reverse()
    data_store.set(store)

    return {'notifications': user_notifications}
