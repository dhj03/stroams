import requests
from datetime import timezone, datetime
import time
from tests.helpers import setup, message_setup, register_user, login_user, create_channel, message_send, message_get, message_senddm, long_string, BASE_URL


############################################
#                                          #
#         Tests for message_send           #
#                                          #
############################################

# Test for invalid channel_id
def test_message_send_invalid_channel_id(setup):
    user = register_user().json()
    response = message_send(user['token'], 0, 'message that they want to send')

    assert response.status_code == 400

# Test for authorised user
def test_message_send_unauthorised_user(setup):
    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user2['token']).json()
    response = message_send(user1['token'], channel['channel_id'], "Test message")

    assert response.status_code == 403

# Test for message length
def test_message_send_long_message(setup):
    user1 = register_user(email = 'user1@mail.com').json()
    channel = create_channel(token = user1['token']).json()
    response = message_send(user1['token'], channel['channel_id'], message = long_string)

    assert response.status_code == 400

# Make sure the message_id's are unique
def test_message_send_message_id(setup):
    user1 = register_user(email = 'user1@mail.com').json()
    channel = create_channel(token = user1['token']).json()
    response1 = message_send(user1['token'], channel['channel_id'], 'First message')
    data1 = response1.json()

    response2 = message_send(user1['token'], channel['channel_id'], 'Second message')
    data2 = response2.json()

    # Asserting message_id's are not equal
    assert data1['message_id'] != data2['message_id']

# Test for mesasge_id's are unique across channels
def test_message_send_across_channels(setup):
    user1 = register_user(email = 'user1@mail.com').json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    response1 = message_send(user1['token'], channel1['channel_id'], 'First message')
    data1 = response1.json()

    response2 = message_send(user1['token'], channel2['channel_id'], 'First message')
    data2 = response2.json()

    # Asserting message_id's are not equal
    assert data1['message_id'] != data2['message_id']

# Test for time_created
def test_message_send_time(setup):
    user1 = register_user(email = 'user1@mail.com').json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    message_send(user1['token'], channel1['channel_id'], 'Test for time')

    response = message_get(user1['token'], channel1['channel_id'], start = 0)
    data = response.json()

    # Get the time
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    # Assert the time should be the same
    assert data['messages'][0]['time_created'] == time


############################################
#                                          #
#         Tests for message_edit           #
#                                          #
############################################

# Test for message length
def test_message_edit_long_message(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token']).json()

    response = message_send(user1['token'], channel['channel_id'], 'Wow cool channel')
    message_id = response.json()['message_id']

    response = requests.put(f"{BASE_URL}/message/edit/v1", json = {
        'token': user1['token'], 'message_id': message_id, 'message': long_string })

    assert response.status_code == 400

def test_message_edit_empty_message(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token']).json()

    response = message_send(user1['token'], channel['channel_id'], "Gonna be gone")
    message_id = response.json()['message_id']

    requests.put(f"{BASE_URL}/message/edit/v1", json = {
        'token': user1['token'], 'message_id': message_id, 'message': "" })
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert len(data['messages']) == 0

# Test for invalid message ID
def test_message_edit_invalid_message_id(message_setup):
    user1 = message_setup[0].json()
    response = requests.put(f"{BASE_URL}/message/edit/v1", json = {
        'token': user1['token'], 'message_id': -1, 'message': 'Hehe' })

    assert response.status_code == 400

# Test for non-admin non-author user editing message
def test_message_edit_unauthorised_notauthor(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user2['token']).json()

    # user1 is not in the channel so they are not a channel owner
    # send msg
    response = message_send(user2['token'], channel['channel_id'], 'Wow cool channel')
    message_id = response.json()['message_id']

    # user1 attempts to change msg
    response = requests.put(f"{BASE_URL}/message/edit/v1", json = {
        'token': user1['token'], 'message_id': message_id, 'message':'Hehe, changing message' })

    assert response.status_code == 403

# Test for if authorised person changes a message that isn't theirs
def test_message_edit_authorised_non_author(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user2['token']).json()

    # invite user1
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user2['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user1['auth_user_id']})
    # send msg
    response = message_send(user1['token'], channel['channel_id'], 'Wow cool channel')
    message_id = response.json()['message_id']

    # user1 attempts to change msg
    requests.put(f"{BASE_URL}/message/edit/v1", json = {'token': user1['token'],
        'message_id': message_id, 'message': 'Hehe, changing message' })

    # get messages
    response = message_get(user1['token'], channel['channel_id'], start = 0)

    assert response.status_code == 200

# Test for if user is not owner member but did send that message
def test_message_edit_author(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user2['token']).json()

    # invite user1
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user2['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user1['auth_user_id']})
    # send msg
    response = message_send(user1['token'], channel['channel_id'], 'Wow cool channel')
    message_id = response.json()['message_id']

    # user1 attempts to change msg
    requests.put(f"{BASE_URL}/message/edit/v1", json = {'token': user1['token'],
        'message_id': message_id, 'message': 'Hehe, changing message' })

    # get messages
    response = message_get(user1['token'], channel['channel_id'], start = 0)

    assert response.status_code == 200

# Test for if it actually edits message
def test_message_edit_working_channel(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token']).json()

    # send msg
    response = message_send(user1['token'], channel['channel_id'], 'Wow cool channel')
    message_id = response.json()['message_id']

    # user1 attempts to change msg
    requests.put(f"{BASE_URL}/message/edit/v1", json = {'token': user1['token'],
        'message_id': message_id, 'message': 'Hehe, changing message'})

    # get messages
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert data['messages'][0]['message'] == 'Hehe, changing message'

# Test for if message_edit is working in dm's
def test_message_edit_working_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@mail.com').json()
    # Create two DMs for coverage
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    # dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
    #     'token': user1['token'], 'u_ids': []}).json()

    message_senddm(user1['token'], dm['dm_id'], "Extra message for coverage")
    response = message_senddm(user1['token'], dm['dm_id'], "I'm talking to myself")
    message_id = response.json()['message_id']

    requests.put(f"{BASE_URL}/message/edit/v1", json = {'token': user1['token'],
        'message_id': message_id, 'message': "I'm insane"})

    data = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
        'token': user1['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert data['messages'][0]['message'] == "I'm insane"

############################################
#                                          #
#        Tests for message_remove          #
#                                          #
############################################

# Test for invalid message_id
def test_message_remove_invalid_message_id(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message_send(user1['token'], channel['channel_id'], 'Test')
    response = requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user1['token'], 'message_id': -1})

    assert response.status_code == 400

# Test for non-admin non-author user removing message
def test_message_remove_unauthorised_notauthor(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@gmail.com').json()

    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    requests.post(  f"{BASE_URL}/channel/invite/v2", json = {'token': user1['token'],
                    'channel_id': channel['channel_id'], 'u_id': user2['auth_user_id']})
    response = message_send(user1['token'], channel['channel_id'], "Test message")
    message_id = response.json()['message_id']
    response2 = requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user2['token'], 'message_id': message_id})

    assert response2.status_code == 403

# Test for if authorised person removes a message
def test_message_remove_authorised_non_author(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user2['token'], name = 'ch_first').json()

    requests.post(  f"{BASE_URL}/channel/invite/v2", json = {'token': user2['token'],
                    'channel_id': channel['channel_id'], 'u_id': user1['auth_user_id']})
    response = message_send(user1['token'], channel['channel_id'], "Test message")
    message_id = response.json()['message_id']

    requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user2['token'],'message_id': message_id})
    response2 = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': user1['token'], 'channel_id': channel['channel_id'], 'start': 0})
    data2 = response2.json()
    assert data2['messages'] == []

# Test for if user is not owner member but did send that message
def test_message_remove_author_of_message(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@gmail.com').json()

    channel = create_channel(token = user2['token'], name = 'ch_first').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = {'token': user2['token'],
        'channel_id': channel['channel_id'], 'u_id': user1['auth_user_id']})
    response = message_send(user1['token'], channel['channel_id'], "Test message")
    message_id = response.json()['message_id']

    requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user1['token'], 'message_id': message_id})
    response2 = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': user1['token'], 'channel_id': channel['channel_id'], 'start': 0})
    data2 = response2.json()
    assert data2['messages'] == []

# Test for if global owner can remove message
def test_message_remove_global_owner(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@gmail.com').json()

    channel = create_channel(token = user2['token'], name = 'ch_first').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = {'token': user2['token'],
        'channel_id': channel['channel_id'], 'u_id': user1['auth_user_id']})
    response = message_send(user2['token'], channel['channel_id'], "Test message")
    message_id = response.json()['message_id']

    requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user1['token'], 'message_id': message_id})
    response2 = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': user1['token'], 'channel_id': channel['channel_id'], 'start': 0})
    data2 = response2.json()
    assert data2['messages'] == []

# Test for if it actually removes message
def test_message_remove_working_channel(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token']).json()

    response = message_send(user1['token'], channel['channel_id'], "Test message")
    message_id = response.json()['message_id']

    requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user1['token'], 'message_id': message_id})
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': user1['token'], 'channel_id': channel['channel_id'], 'start': 0})
    data = response.json()
    assert data['messages'] == []

# Test for if it actually removes messages in dms
def test_message_remove_working_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()

    response = message_senddm(user1['token'], dm['dm_id'], "I'm talking to myself")
    message_id = response.json()['message_id']

    requests.delete(f"{BASE_URL}/message/remove/v1", json = {
        'token': user1['token'], 'message_id': message_id})

    data = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
        'token': user1['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert data['messages'] == []

'''
<message/pin/v1>
'''
# Test for invalid message_id
def test_message_pin_invalid_message_id(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message_send(user1['token'], channel['channel_id'], 'Test')
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': -1})

    assert response.status_code == 400

# Test for message is already pinned
def test_message_pin_already_pinned(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    response2 = requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})

    assert response2.status_code == 400

# Test for unauthorised member
def test_message_pin_unauthorised(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user2['token'], 'message_id': message['message_id']})

    assert response.status_code == 403

# Test for correct scenario channel
def test_message_pin_correct_channel(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert data['messages'][0]['is_pinned'] == True

# Test for correct scenario dm's
def test_message_pin_correct_dm(message_setup):
    user1 = message_setup[0].json()
    #Register second user
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = message_senddm(user1['token'], dm['dm_id'], "I'm talking to myself").json()
    requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    data = requests.get(f"{BASE_URL}/dm/messages/v1", params = {'token': user1['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert data['messages'][0]['is_pinned'] == True

'''
<message/unpin/v1>
'''
# Test for invalid message_id
def test_message_unpin_invalid_message_id(message_setup):
    user1 = message_setup[0].json()
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = {'token': user1['token'], 'message_id': -1})

    assert response.status_code == 400

# Test for already not pinned
def test_message_unpin_already_unpinned(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})

    assert response.status_code == 400

# Test for unauthorised member
def test_message_unpin_unauthorised(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = {'token': user2['token'], 'message_id': message['message_id']})

    assert response.status_code == 403

# Test for correct scenario channel
def test_message_unpin_correct_channel(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    requests.post(f"{BASE_URL}/message/unpin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert data['messages'][0]['is_pinned'] == False

# Test for corret scenario dm's
def test_message_unpin_correct_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = message_senddm(user1['token'], dm['dm_id'], "I'm talking to myself").json()
    requests.post(f"{BASE_URL}/message/pin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    requests.post(f"{BASE_URL}/message/unpin/v1", json = {'token': user1['token'], 'message_id': message['message_id']})
    data = requests.get(f"{BASE_URL}/dm/messages/v1", params = {'token': user2['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert data['messages'][0]['is_pinned'] == False

'''
<message/share/v1>
'''
# Test for a lot of messages
def test_message_share_a_lot_of_messages(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    dm2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user3['auth_user_id']]}).json()
    message_senddm(user1['token'], dm1['dm_id'], "Test1").json()
    message_senddm(user1['token'], dm2['dm_id'], "Test2").json()
    message_senddm(user1['token'], dm2['dm_id'], "Test3").json()
    message_senddm(user1['token'], dm2['dm_id'], "Test4").json()
    message_senddm(user1['token'], dm2['dm_id'], "Test5").json()
    message6 = message_senddm(user1['token'], dm2['dm_id'], "Test5").json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user1['token'],
                                                                        'og_message_id': message6['message_id'],
                                                                        'message': '',
                                                                        'channel_id': -1,
                                                                        'dm_id': dm1['dm_id']})

    assert response.status_code == 200

# Test for both channel_id and dm_id are negative 1
def test_message_share_both_negative_one(message_setup):
    user1 = message_setup[0].json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel1['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user1['token'],
                                                                        'og_message_id': message['message_id'],
                                                                        'message': '',
                                                                        'channel_id': -1,
                                                                        'dm_id': -1})

    assert response.status_code == 400

# Test for valid id in both channel_id and dm_id
def test_message_share_both_valid_id(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel2['channel_id'],
                                                            'u_id': user2['auth_user_id']})
    message = message_send(user1['token'], channel2['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user2['token'],
                                                                        'og_message_id': message['message_id'],
                                                                        'message': '',
                                                                        'channel_id': channel1['channel_id'],
                                                                        'dm_id': dm['dm_id']})

    assert response.status_code == 400

# Test for invalid channel_id
def test_message_share_invalid_channel_ids(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {'token': user1['token'], 'og_message_id': message['message_id'], 'message': '', 'channel_id': 12345, 'dm_id': -1})

    assert response.status_code == 400

# Test for invalid dm_id
def test_message_share_invalid_dm_ids(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = message_senddm(user1['token'], dm['dm_id'], "I'm talking to myself").json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {'token': user1['token'], 'og_message_id': message['message_id'], 'message': '', 'channel_id': -1, 'dm_id': 12345})

    assert response.status_code == 400

# Test for sending to both channel and dm (Neither channel_id nor dm_id are -1)
def test_message_share_invalid_ids(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {'token': user1['token'], 'og_message_id': message['message_id'], 'message': '', 'channel_id': 12345, 'dm_id': 12345})

    assert response.status_code == 400

# Test for invalid og_message_id
def test_message_share_invalid_og_message_id(message_setup):
    user1 = message_setup[0].json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    message_send(user1['token'], channel1['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {'token': user1['token'], 'og_message_id': -1, 'message': '', 'channel_id': channel2['channel_id'], 'dm_id': -1})

    assert response.status_code == 400
    
# Test for length of optional message > 1000
def test_message_share_long_message(message_setup):
    user1 = message_setup[0].json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    message = message_send(user1['token'], channel1['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {'token': user1['token'], 'og_message_id': message['message_id'], 'message': long_string, 'channel_id': channel2['channel_id'], 'dm_id': -1})

    assert response.status_code == 400

# Test for user not in channel that message is in
def test_message_share_user_not_in_message_channel(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel2['channel_id'],
                                                            'u_id': user2['auth_user_id']})
    message = message_send(user1['token'], channel1['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user2['token'],
                                                                        'og_message_id': message['message_id'],
                                                                        'message': '',
                                                                        'channel_id': channel2['channel_id'],
                                                                        'dm_id': -1})

    assert response.status_code == 403

# Test for user not in channel that they want to share to
def test_message_share_user_not_in_channel(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel1['channel_id'],
                                                            'u_id': user2['auth_user_id']})
    message = message_send(user1['token'], channel1['channel_id'], 'Test').json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user2['token'],
                                                                        'og_message_id': message['message_id'],
                                                                        'message': '',
                                                                        'channel_id': channel2['channel_id'],
                                                                        'dm_id': -1})

    assert response.status_code == 403

# Test for user not in dm that they want to share to
def test_message_share_user_not_in_shared_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    dm2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user3['auth_user_id']]}).json()
    message1 = message_senddm(user1['token'], dm1['dm_id'], "I will share this to Emidus5.").json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user2['token'],
                                                                        'og_message_id': message1['message_id'],
                                                                        'message': '',
                                                                        'channel_id': -1,
                                                                        'dm_id': dm2['dm_id']})

    assert response.status_code == 403

# Test for user not in dm that message is in
def test_message_share_user_not_in_message_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    dm2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user3['auth_user_id']]}).json()
    message1 = message_senddm(user1['token'], dm1['dm_id'], "I will share this to Emidus5.").json()
    response = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user3['token'],
                                                                        'og_message_id': message1['message_id'],
                                                                        'message': '',
                                                                        'channel_id': -1,
                                                                        'dm_id': dm2['dm_id']})

    assert response.status_code == 403

# Test for working in channels
def test_message_share_correct_channels(message_setup):
    user1 = message_setup[0].json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user1['token'], name = 'ch_second').json()
    message1 = message_send(user1['token'], channel1['channel_id'], 'I want to share this message to channel 2.').json()
    message2 = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user1['token'],
                                                                        'og_message_id': message1['message_id'],
                                                                        'message': 'I have shared the message.',
                                                                        'channel_id': channel2['channel_id'],
                                                                        'dm_id': -1}).json()
    data = message_get(user1['token'], channel2['channel_id'], start = 0).json()
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    print(message2)
    assert data['messages'][0]['message_id'] == message2['shared_message_id']
    assert data['messages'][0]['message'] == 'I want to share this message to channel 2. I have shared the message.'
    assert data['messages'][0]['time_created'] - time <= 1

# Test for working in dm's
def test_message_share_correct_dms(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    dm2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user3['auth_user_id']]}).json()
    message1 = message_senddm(user1['token'], dm1['dm_id'], "I will share this to Emidus5.").json()
    message2 = requests.post(f"{BASE_URL}/message/share/v1", json = {   'token': user1['token'],
                                                                        'og_message_id': message1['message_id'],
                                                                        'message': 'I have sent the message to Emidus5.',
                                                                        'channel_id': -1,
                                                                        'dm_id': dm2['dm_id']}).json()
    data = requests.get(f"{BASE_URL}/dm/messages/v1", params = {    'token': user3['token'],
                                                                    'dm_id': dm2['dm_id'],
                                                                    'start': 0}).json()
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)

    assert data['messages'][0]['message_id'] == message2['shared_message_id']
    assert data['messages'][0]['message'] == 'I will share this to Emidus5. I have sent the message to Emidus5.'
    assert data['messages'][0]['time_created'] - time <= 1

'''
<message/react/v1>
'''
# Test for user not in dm
def test_message_react_user_not_in_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message1 = message_senddm(user1['token'], dm['dm_id'], "I will share this to Emidus5.").json()
    response = requests.post(f"{BASE_URL}/message/react/v1", json = {   'token': user3['token'],
                                                                        'message_id': message1['message_id'],
                                                                        'react_id': 1})
    
    assert response.status_code == 403
# Test for invalid message_id
def test_message_react_invalid_message_id(message_setup):
    user1 = message_setup[0].json()
    response = requests.post(f"{BASE_URL}/message/react/v1", json = {   'token': user1['token'],
                                                                        'message_id': -1,
                                                                        'react_id': 1})
    
    assert response.status_code == 400

# Test for invalid react_id
def test_message_react_invalid_react_id(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'I will react to this message').json()
    response = requests.post(f"{BASE_URL}/message/react/v1", json = {   'token': user1['token'],
                                                                        'message_id': message['message_id'],
                                                                        'react_id': -1})

    assert response.status_code == 400

# Test for already reacted
def test_message_react_already_reacted(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})
    message_send(user1['token'], channel['channel_id'], 'I will react to this message').json()
    message_send(user1['token'], channel['channel_id'], 'I will react to this message').json()
    message3 = message_send(user1['token'], channel['channel_id'], 'I will react to this message').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {      'token': user2['token'],
                                                                'message_id': message3['message_id'],
                                                                'react_id': 1})
    response = requests.post(f"{BASE_URL}/message/react/v1", json = {   'token': user2['token'],
                                                                        'message_id': message3['message_id'],
                                                                        'react_id': 1})

    assert response.status_code == 400
# Test for unauthorised member
def test_message_react_unauthorised(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    response = requests.post(f"{BASE_URL}/message/react/v1", json = {   'token': user2['token'],
                                                                        'message_id': message['message_id'],
                                                                        'react_id': 1})

    assert response.status_code == 403

# Test for correct scenario channel
def test_message_react_correct_channel(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert data['messages'][0]['reacts'] == [{'0':1}]

# Test for correct scenario dm's
def test_message_react_correct_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = message_senddm(user1['token'], dm['dm_id'], 'This should be sent third').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user2['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    messages = requests.get(f"{BASE_URL}/dm/messages/v1", params = {'token': user2['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert messages['messages'][0]['reacts'] == [{'1':1}]
'''
<message/unreact/v1>
'''
# Test for user not in dm
def test_message_unreact_user_not_in_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id'], user3['auth_user_id']]}).json()
    message1 = message_senddm(user1['token'], dm['dm_id'], 'This should be sent third').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user3['token'],
                                                            'message_id': message1['message_id'],
                                                            'react_id': 1})
    requests.post(f"{BASE_URL}/dm/leave/v1", json = {   'token': user3['token'],
                                                        'dm_id': dm['dm_id']})
    response = requests.post(f"{BASE_URL}/message/unreact/v1", json = {     'token': user3['token'],
                                                                            'message_id': message1['message_id'],
                                                                            'react_id': 1})

    assert response.status_code == 403


# Test for invalid message_id
def test_message_unreact_invalid_message_id(message_setup):
    user1 = message_setup[0].json()
    response = requests.post(f"{BASE_URL}/message/unreact/v1", json = { 'token': user1['token'],
                                                                        'message_id': -1,
                                                                        'react_id': 1})
    
    assert response.status_code == 400

# Test for invalid react_id
def test_message_unreact_invalid_react_id(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    response = requests.post(f"{BASE_URL}/message/unreact/v1", json = { 'token': user1['token'],
                                                                        'message_id': message['message_id'],
                                                                        'react_id': -1})
    
    assert response.status_code == 400

# Test for no current user react
def test_message_unreact_no_user_react(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})
    message = message_send(user1['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    response = requests.post(f"{BASE_URL}/message/unreact/v1", json = { 'token': user2['token'],
                                                                        'message_id': message['message_id'],
                                                                        'react_id': 1})

    assert response.status_code == 400

# Test for unauthorised member
def test_message_unreact_unauthorised(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = message_send(user1['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    response = requests.post(f"{BASE_URL}/message/unreact/v1", json = { 'token': user2['token'],
                                                                        'message_id': message['message_id'],
                                                                        'react_id': 1})
    
    assert response.status_code == 403

# Test for correct scenario channel
def test_message_unreact_correct_channel(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    requests.post(f"{BASE_URL}/channel/invite/v2", json = { 'token': user1['token'],
                                                            'channel_id': channel['channel_id'],
                                                            'u_id': user2['auth_user_id']})
    message = message_send(user1['token'], channel['channel_id'], 'Wendy will fail to react to this.').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    requests.post(f"{BASE_URL}/message/unreact/v1", json = { 'token': user1['token'],
                                                             'message_id': message['message_id'],
                                                             'react_id': 1})
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user2['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert data['messages'][0]['reacts'] == [{'1':1}]

# Test for correct scenario dms
def test_message_unreact_correct_dm(message_setup):
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = message_senddm(user1['token'], dm['dm_id'], 'This should be sent third').json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user1['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    requests.post(f"{BASE_URL}/message/unreact/v1", json = { 'token': user1['token'],
                                                             'message_id': message['message_id'],
                                                             'react_id': 1})
    requests.post(f"{BASE_URL}/message/react/v1", json = {  'token': user2['token'],
                                                            'message_id': message['message_id'],
                                                            'react_id': 1})
    messages = requests.get(f"{BASE_URL}/dm/messages/v1", params = {'token': user2['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert messages['messages'][0]['reacts'] == [{'1':1}]
'''
<message/sendlater/v1>
'''
# Test for time_sent is a time in the past
def test_message_sendlater_invalid_time(message_setup):
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    fake_time = time-200
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {   'token': user1['token'],
                                                                            'channel_id': channel['channel_id'],
                                                                            'message': 'I am sending this to the past',
                                                                            'time_sent': fake_time})

    assert response.status_code == 400

# Test for message is over 1000 characters
def test_message_sendlater_long_message(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    future_time = time+10
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {  'token': user1['token'],
                                                                'channel_id': channel['channel_id'],
                                                                'message': long_string,
                                                                'time_sent': future_time})
    
    assert response.status_code == 400

# Test for invalid channel_id
def test_message_sendlater_invalid_channel(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    future_time = time+10
    user1 = message_setup[0].json()
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {  'token': user1['token'],
                                                                'channel_id': -1,
                                                                'message': 'Sending this to invalid channel',
                                                                'time_sent': future_time})
    
    assert response.status_code == 400

# Test for unauthorised user
def test_message_sendlater_invalid_user(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    future_time = time+10
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {   'token': user2['token'],
                                                                            'channel_id': channel['channel_id'],
                                                                            'message': 'I am not authorised in this channel',
                                                                            'time_sent': future_time})

    assert response.status_code == 403

# Test for generates message_id immediately
def test_message_sendlater_generate_id(message_setup):
    dt = datetime.now(timezone.utc)
    current_time = dt.timestamp()
    current_time = int(current_time)
    future_time = current_time+3
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    message = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {   'token': user1['token'],
                                                                            'channel_id': channel['channel_id'],
                                                                            'message': 'This messages goes hard feel free to screenshot.',
                                                                            'time_sent': future_time}).json()
    assert message['message_id'] == 1
    time.sleep(4)

# Test for correct implementation
def test_message_sendlater_working(message_setup):
    dt = datetime.now(timezone.utc)
    current_time1 = dt.timestamp()
    current_time1 = int(current_time1)
    future_time = current_time1+3
    user1 = message_setup[0].json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()
    requests.post(f"{BASE_URL}/message/sendlater/v1", json = {      'token': user1['token'],
                                                                    'channel_id': channel['channel_id'],
                                                                    'message': 'This should be sent second',
                                                                    'time_sent': future_time})
    message_send(user1['token'], channel['channel_id'], 'This should be sent first')
    time.sleep(4)
    dt2 = datetime.now(timezone.utc)
    current_time2 = dt2.timestamp()
    current_time2 = int(current_time2)
    message_send(user1['token'], channel['channel_id'], 'This should be sent third')
    messages = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert messages['messages'][0]['message_id'] == 3
    assert messages['messages'][0]['message'] == 'This should be sent third'
    assert messages['messages'][0]['time_created'] - current_time2 <= 1
    assert messages['messages'][1]['message_id'] == 1
    assert messages['messages'][1]['message'] == 'This should be sent second'
    assert messages['messages'][1]['time_created'] - future_time <= 1
    assert messages['messages'][2]['message_id'] == 2
    assert messages['messages'][2]['message'] == 'This should be sent first'
    assert messages['messages'][2]['time_created'] - current_time1 <= 1

'''
<message/sendlaterdm/v1>
'''
def test_message_sendlaterdm_invalid_time(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    past_time = time-200
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = { 'token': user1['token'],
                                                                            'dm_id': dm['dm_id'],
                                                                            'message': 'Sending this to the past',
                                                                            'time_sent': past_time})
    
    assert response.status_code == 400

def test_message_sendlaterdm_long_message(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    future_time = time+10
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = { 'token': user1['token'],
                                                                            'dm_id': dm['dm_id'],
                                                                            'message': long_string,
                                                                            'time_sent': future_time})
    
    assert response.status_code == 400

def test_message_sendlaterdm_invalid_dm(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    future_time = time+10
    user1 = message_setup[0].json()
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = { 'token': user1['token'],
                                                                            'dm_id': -1,
                                                                            'message': 'No more long string',
                                                                            'time_sent': future_time})

    assert response.status_code == 400

def test_message_sendlaterdm_invalid_user(message_setup):
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    future_time = time+10
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = { 'token': user3['token'],
                                                                            'dm_id': dm['dm_id'],
                                                                            'message': 'I am sending this to Hayden and Wendy',
                                                                            'time_sent': future_time})

    assert response.status_code == 403

def test_message_sendlaterdm_generate_id(message_setup):
    dt = datetime.now(timezone.utc)
    current_time = dt.timestamp()
    current_time = int(current_time)
    future_time = current_time+3
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    message = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = { 'token': user1['token'],
                                                                            'dm_id': dm['dm_id'],
                                                                            'message': 'I am sending this to Hayden and Wendy',
                                                                            'time_sent': future_time}).json()

    assert message['message_id'] == 1
    time.sleep(4)

def test_message_sendlaterdm_working(message_setup):
    # Get the time
    dt1 = datetime.now(timezone.utc)
    current_time1 = dt1.timestamp()
    current_time1 = int(current_time1)
    future_time = current_time1+3
    user1 = message_setup[0].json()
    user2 = register_user(email = 'user2@gmail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {    'token': user1['token'],
                                                                    'dm_id': dm['dm_id'],
                                                                    'message': 'This should be sent second',
                                                                    'time_sent': future_time}).json()
    message_senddm(user1['token'], dm['dm_id'], 'This should be sent first').json()
    time.sleep(4)
    dt2 = datetime.now(timezone.utc)
    current_time2 = dt2.timestamp()
    current_time2 = int(current_time2)
    message_senddm(user1['token'], dm['dm_id'], 'This should be sent third').json()
    messages = requests.get(f"{BASE_URL}/dm/messages/v1", params = {'token': user2['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    # Assert the second normal message was sent and details are correct
    assert messages['messages'][0]['message_id'] == 3
    assert messages['messages'][0]['message'] == 'This should be sent third'
    assert messages['messages'][0]['time_created'] - current_time2 <= 1
    # Assert the sendlater message was sent and the details are correct
    assert messages['messages'][1]['message_id'] == 1
    assert messages['messages'][1]['message'] == 'This should be sent second'
    assert messages['messages'][1]['time_created'] - future_time <= 1
    # Assert the first normal message was sent and details are correct
    assert messages['messages'][2]['message_id'] == 2
    assert messages['messages'][2]['message'] == 'This should be sent first'
    assert messages['messages'][2]['time_created'] - current_time1 <= 1
