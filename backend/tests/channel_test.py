import requests
from tests.helpers import BASE_URL, setup, register_user, create_channel
from tests.helpers import message_send, message_get

############################################
#                                          #
#      Tests for channel_details           #
#                                          #
############################################

def test_channel_details_invalid_channel_id(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
                            'token': user1['token'], 'channel_id': 0})
    assert response.status_code == 400


def test_channel_details_is_user_member(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token'], name = 'ch_first').json()

    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': user2['token'], 'channel_id': channel['channel_id']})

    # User not found
    assert response.status_code == 403


def test_channel_details(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Allow user2 to join the channel
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': user2['token'], 'channel_id': channel['channel_id']})

    # test valid
    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 200
    data = response.json()

    # Confirm user joined server through details function
    assert data['all_members'][1]['email'] == 'user2@mail.com'


def test_channel_details_return_value(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()
    # Get all requested channels by user2
    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': user['token'], 'channel_id': channel['channel_id']})

    data = response.json()
    print(data)
    assert data == {
        'name': 'ch_name',
        'is_public': True,
        'owner_members': [
            {
                'u_id': user['auth_user_id'],
                'email': 'user@mail.com',
                'name_first': 'given',
                'name_last': 'sur',
                'handle_str': 'givensur'
            }
        ],
        'all_members': [
            {
                'u_id': user['auth_user_id'],
                'email': 'user@mail.com',
                'name_first': 'given',
                'name_last': 'sur',
                'handle_str': 'givensur'
            }
        ]
    }

def test_channel_details_user_removed(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': user2['token'], 'channel_id': channel['channel_id']})

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})
    data = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': user1['token'], 'channel_id': channel['channel_id']}).json()

    assert len(data['all_members']) == 1

############################################
#                                          #
#      Tests for channel_join              #
#                                          #
############################################

def test_channel_join_invalid_channel_id(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
                            'token': user['token'], 'channel_id': 0})
    assert response.status_code == 400

def test_channel_join_already_member(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
                            'token': user['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 400

def test_channel_join_private_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token'], is_public = False).json()

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 403

def test_channel_join_private_authorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user2['token'], is_public = False).json()

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 200

def test_channel_join_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Allow user2 to join the channel
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.json() == {}

    # Check if user2 is part of the channel
    ch_list = requests.get( f"{BASE_URL}/channels/list/v2",
                            params = {'token': user2['token']}).json()
    assert len(ch_list['channels']) == 1
    assert ch_list['channels'][0]['channel_id'] == channel['channel_id']
    assert ch_list['channels'][0]['name'] == 'ch_name'

############################################
#                                          #
#      Tests for channel_invite            #
#                                          #
############################################

def test_channel_invite_invalid_channel_id(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
                            'token': user1['token'], 'channel_id': 0,
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 400

def test_channel_invite_invalid_u_id(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
                            'token': user['token'], 'channel_id': channel['channel_id'],
                            'u_id': user['auth_user_id'] + 1})
    assert response.status_code == 400

def test_channel_invite_already_member(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
                            'token': user['token'], 'channel_id': channel['channel_id'],
                            'u_id': user['auth_user_id']})
    assert response.status_code == 400

def test_channel_invite_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    user3 = register_user(email = 'user3@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id'],
                            'u_id': user3['auth_user_id']})
    assert response.status_code == 403

def test_channel_invite_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user1 invite user2 to the channel
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {'token': user1['token'],
                            'channel_id': channel['channel_id'], 'u_id': user2['auth_user_id']})
    assert response.json() == {}

    # Check if user2 is part of the channel
    ch_list = requests.get( f"{BASE_URL}/channels/list/v2",
                            params = {'token': user2['token']}).json()
    assert len(ch_list['channels']) == 1
    assert ch_list['channels'][0]['channel_id'] == channel['channel_id']
    assert ch_list['channels'][0]['name'] == 'ch_name'

############################################
#                                          #
#        Tests for channel_leave           #
#                                          #
############################################

def test_channel_leave_invalid_channel(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json = {
                            'token': user['token'], 'channel_id': 0})
    assert response.status_code == 400

def test_channel_leave_not_member(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    response = requests.post(f"{BASE_URL}/channel/leave/v1", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 403

def test_channel_leave_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user2 join the channel
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})
    # Make both users leave the channel
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 200
    # User is no longer a member of the channel
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 403

    response = requests.post(f"{BASE_URL}/channel/leave/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 200
    assert response.json() == {}

############################################
#                                          #
#       Tests for channel_addowner         #
#                                          #
############################################

def test_channel_addowner_invalid_channel(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user['token'], 'channel_id': 0,
                            'u_id': user['auth_user_id']})
    assert response.status_code == 400

def test_channel_addowner_invalid_u_id(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user['token'], 'channel_id': channel['channel_id'],
                            'u_id': user['auth_user_id'] + 1})
    assert response.status_code == 400

def test_channel_addowner_not_member(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 400

def test_channel_addowner_already_owner(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user['token'], 'channel_id': channel['channel_id'],
                            'u_id': user['auth_user_id']})
    assert response.status_code == 400

def test_channel_addowner_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user2 join the channel - note that they are not an owner
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 403

def test_channel_addowner_unauthorised_global_owner(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user2['token']).json()
    # Note that user1 is not in the channel
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id'],
                            'u_id': user1['auth_user_id']})
    assert response.status_code == 403

def test_channel_addowner_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    user3 = register_user(email = 'user3@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user2 and user3 join the channel
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user3['token'], 'channel_id': channel['channel_id']})
    # Make user2 an owner, who in turn should be able to make user3 an owner
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id'],
                            'u_id': user3['auth_user_id']})
    assert response.status_code == 200
    assert response.json() == {}

############################################
#                                          #
#      Tests for channel_removeowner       #
#                                          #
############################################

def test_channel_removeowner_invalid_channel(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user['token'], 'channel_id': 0,
                            'u_id': user['auth_user_id']})
    assert response.status_code == 400

def test_channel_removeowner_invalid_u_id(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user['token'], 'channel_id': channel['channel_id'],
                            'u_id': user['auth_user_id'] + 1})
    assert response.status_code == 400

def test_channel_removeowner_not_owner(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user2 join the channel - note that they are not an owner
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 400

def test_channel_removeowner_only_owner(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user['token'], 'channel_id': channel['channel_id'],
                            'u_id': user['auth_user_id']})
    assert response.status_code == 400

def test_channel_removeowner_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    user3 = register_user(email = 'user3@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user2 join the channel with ownership
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})
    requests.post   (f"{BASE_URL}/channel/addowner/v1", json = {
                    'token': user1['token'], 'channel_id': channel['channel_id'],
                    'u_id': user2['auth_user_id']})
    # Make user3 join the channel without ownership
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user3['token'], 'channel_id': channel['channel_id']})
    # Attempt to make user3 remove user2's ownership - it will fail
    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user3['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 403

def test_channel_removeowner_unauthorised_global_owner(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    user3 = register_user(email = 'user3@mail.com').json()
    channel = create_channel(token = user2['token']).json()
    # Note that user1 is not in the channel
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user3['token'], 'channel_id': channel['channel_id']})
    requests.post(  f"{BASE_URL}/channel/addowner/v1", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id'],
                    'u_id': user3['auth_user_id']})
    # Now user2 is no longer the only owner, and can be removed - if authorised
    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    # But user1 is not authorised
    assert response.status_code == 403

def test_channel_removeowner_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    # Make user2 join the channel with ownership
    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})
    requests.post   (f"{BASE_URL}/channel/addowner/v1", json = {
                    'token': user1['token'], 'channel_id': channel['channel_id'],
                    'u_id': user2['auth_user_id']})
    # Take away user2's ownership - it will pass
    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user2['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 200
    assert response.json() == {}
    # Attempt to take it away again - it will fail
    response = requests.post(f"{BASE_URL}/channel/removeowner/v1", json = {
                            'token': user1['token'], 'channel_id': channel['channel_id'],
                            'u_id': user2['auth_user_id']})
    assert response.status_code == 400

############################################
#                                          #
#      Tests for channel_messages          #
#                                          #
############################################

# Test for invalid channel_id
def test_channel_messages_invalid_channel_id(setup):

    user = register_user().json()
    response = message_get(user['token'], 0, start = 10)

    assert response.status_code == 400

# Test for invalid start value (start > # of messages)
def test_channel_messages_invalid_start(setup):

    user = register_user(email = 'user@mail.com').json()
    channel = create_channel(token = user['token']).json()

    response = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'start': 218})
    assert response.status_code == 400

# Test for user is not valid member for channel
def test_channel_messages_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    response = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': user2['token'], 'channel_id': channel['channel_id'], 'start': 10})
    assert response.status_code == 403

# Test for valid response
def test_channel_messages_valid_return(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    channel = create_channel(token = user1['token']).json()
    message_send(user1['token'], channel['channel_id'], 'Happy')
    response = message_get(user1['token'], channel['channel_id'], start = 0)
    data = response.json()

    assert data['messages'][0]['message'] == 'Happy'
    assert data['start'] == 0
    assert data['end'] == -1

# Test for 124 messages correct returns
def test_channel_messages_124(setup):
    user = register_user(email = 'user1@gmail.com').json()
    channel = create_channel(token = user['token']).json()

    # Send 124 messages
    counter = 0
    while counter < 125:
        message_send(user['token'], channel['channel_id'], 'Happy')
        counter += 1

    # Pull messages 0-50
    response50 = message_get(user['token'], channel['channel_id'], start = 0)
    data50 = response50.json()

    # Pull messages 50-100
    response100 = message_get(user['token'], channel['channel_id'], start = 50)
    data100 = response100.json()

    # Pull messages 100 -124
    response124 = message_get(user['token'], channel['channel_id'], start = 100)
    data124 = response124.json()

    # Asserting for first 50 mesasges
    assert data50['start'] == 0
    assert data50['end'] == 50

    # Asserting for first 100 mesasges
    assert data100['start'] == 50
    assert data100['end'] == 100

    # Asserting for first 100 mesasges
    assert data124['start'] == 100
    assert data124['end'] == -1

# Test for a user which has been removed
def test_channel_messages_user_removed(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    create_channel(token = user1['token'], name = 'justforcoverage')

    requests.post(  f"{BASE_URL}/channel/join/v2", json = {
                    'token': user2['token'], 'channel_id': channel['channel_id']})
    message_send(user1['token'], channel['channel_id'], "Test message")
    message_send(user2['token'], channel['channel_id'], "Test message")
    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})
    # user2 no longer exists
    data = message_get(user1['token'], channel['channel_id'], start = 0).json()

    assert data['messages'][0]['message'] == "Removed user"
    assert data['messages'][1]['message'] == "Test message"
