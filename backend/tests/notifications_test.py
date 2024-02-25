import requests
from tests.helpers import *

'''
<notifications/get/v1>
'''
def test_notification_get_valid(message_setup):
    user1 = message_setup[0].json()
    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user1['token']}).json()
    assert data['notifications'] == []

'''
<notifications/send/v1>
'''
def test_notification_send_invite_channel_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    # invite user2
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})

    channel = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']}).json()
    name = channel['channels'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} added you to {name}"
    

def test_notification_send_invite_dm_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    # Create two DMs for coverage
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()

    dm =  requests.get(f"{BASE_URL}/dm/list/v1", params = {'token': user2['token']}).json()                                                                                                                 
    name = dm['dms'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} added you to {name}"


def test_notification_send_tag_send_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']

    channel = create_channel(token = user1['token']).json()

    # invite user1
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})

    msg = f'Wow cool channel {handle2}'
    # send msg
    message_send(user1['token'], channel['channel_id'], msg)

    channel = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']}).json()
    name = channel['channels'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {msg[0:19]}"


def test_notification_send_tag_senddm_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']

    # Create two DMs for coverage
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()

    msg = f"Am I talking to myself {handle2}"
    response = message_senddm(user1['token'], dm['dm_id'], msg).json()
    assert response['message_id'] == 1

    dm =  requests.get(f"{BASE_URL}/dm/list/v1", params = {'token': user2['token']}).json()                                                                                                                 
    name = dm['dms'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {msg[0:19]}"


def test_notification_send_tag_share_ch_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']
    
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']

    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()

    # invite user2
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel2['channel_id'],
                                                            'u_id': user2['auth_user_id']})

    msg1 = 'I want to share this message to channel 2.'
    message_send(user1['token'], channel1['channel_id'], msg1).json()
    msg2 = f'I have shared the message.{handle2}'
    requests.post(f"{BASE_URL}/message/share/v1", json = {  'token': user1['token'],
                                                            'og_message_id': 1,
                                                            'message': msg2,
                                                            'channel_id': channel2['channel_id'],
                                                            'dm_id': -1}).json()

    channel = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']}).json()
    name = channel['channels'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {f'{msg1} {msg2}'[0:19]}"


def test_notification_send_tag_msg_share_ch_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']
    
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']

    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()

    # invite user2
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel2['channel_id'],
                                                            'u_id': user2['auth_user_id']})

    msg1 = f'I want to share this message to channel 2. {handle2}'
    message1 = message_send(user1['token'], channel1['channel_id'], msg1).json()

    msg2 = 'I have shared the message.'
    requests.post(f"{BASE_URL}/message/share/v1", json = {  'token': user1['token'],
                                                            'og_message_id': message1['message_id'],
                                                            'message': msg2,
                                                            'channel_id': channel2['channel_id'],
                                                            'dm_id': -1}).json()

    channel = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']}).json()
    name = channel['channels'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {f'{msg1} {msg2}'[0:19]}"

def test_notification_send_tag_share_dm_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']

    dm1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    dm2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user3['auth_user_id']]}).json()


    msg1 =  "I will share this to dm1."
    msg2 = f'I have sent the message to {handle2}'
    message1 = message_senddm(user1['token'], dm2['dm_id'], msg1).json()
    requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user1['token'],
                                                                        'og_message_id': message1['message_id'],
                                                                        'message': msg2,
                                                                        'channel_id': -1,
                                                                        'dm_id': dm1['dm_id']}).json()

    dm =  requests.get(f"{BASE_URL}/dm/list/v1", params = {'token': user2['token']}).json()                                                                                                                 
    name = dm['dms'][0]['name']
    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    # assert data.json() == 55
    assert data.status_code == 200
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {f'{msg1} {msg2}'[0:19]}"

def test_notification_send_tag_msg_share_dm_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']
    
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']
    
    dm1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    dm2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user3['auth_user_id']]}).json()
    
    msg1 = f'I will share this to {handle2}.'
    msg2 = 'I have sent the message to dm1.'
    message1 = message_senddm(user1['token'], dm2['dm_id'], msg1).json()
    requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user1['token'],
                                                            'og_message_id': message1['message_id'],
                                                            'message': msg2,
                                                            'channel_id': -1,
                                                            'dm_id': dm1['dm_id']}).json()
    
    dm =  requests.get(f"{BASE_URL}/dm/list/v1", params = {'token': user2['token']}).json()                                                                                                                 
    name = dm['dms'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200                          
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {f'{msg1} {msg2}'[0:19]}"

def test_notification_send_tag_edit_channel_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']
    
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']
 
    channel = create_channel(token = user1['token']).json()

    # invite user2
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})

    # send msg
    response = message_send(user1['token'], channel['channel_id'], 'Wow cool channel')
    message_id = response.json()['message_id']

    # user1 attempts to change msg
    msg = f'Hehe, changing message {handle2}'
    requests.put(f"{BASE_URL}/message/edit/v1", json = {'token': user1['token'],
        'message_id': message_id, 'message': msg})

    channel = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']}).json()
    name = channel['channels'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200  
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {msg[0:19]}"

def test_notification_send_tag_edit_dm_valid(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']
    
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user2['token'], 'u_id': user2['auth_user_id']}).json()
    handle2 = data['user']['handle_str']

    # Create two DMs for coverage
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()

    message_senddm(user1['token'], dm['dm_id'], "Extra message for coverage")
    response = message_senddm(user1['token'], dm['dm_id'], "I'm talking to myself")
    message_id = response.json()['message_id']

    msg = f"I'm insane{handle2}"
    requests.put(f"{BASE_URL}/message/edit/v1", json = {'token': user1['token'],
        'message_id': message_id, 'message': msg})

    dm =  requests.get(f"{BASE_URL}/dm/list/v1", params = {'token': user2['token']}).json()                                                                                                                 
    name = dm['dms'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200  
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} tagged you in {name}: {msg[0:19]}"

# Test for correct scenario channel
def test_notification_send_react_correct_channel(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    channel = create_channel(token = user1['token'], name = 'ch_first').json()

    # invite user2
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})

    message = message_send(user2['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})

    channel = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']}).json()
    name = channel['channels'][0]['name']

    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200 
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} reacted to your message in {name}"

# Test for correct scenario dm's
def test_notification_send_react_correct_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()

    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user1['auth_user_id']}).json()
    handle1 = data['user']['handle_str']

    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = message_senddm(user2['token'], dm['dm_id'], 'This should be sent third').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})

    dm =  requests.get(f"{BASE_URL}/dm/list/v1", params = {'token': user2['token']}).json()                                                                                                                 
    name = dm['dms'][0]['name']


    data = requests.get(f"{BASE_URL}/notifications/get/v1", params = {'token': user2['token']})
    assert data.status_code == 200 
    assert data.json()['notifications'][0]['notification_message'] == f"{handle1} reacted to your message in {name}"
