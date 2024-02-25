import requests
from datetime import timezone, datetime
from tests.helpers import BASE_URL, setup, register_user, message_senddm, long_string

############################################
#                                          #
#           Tests for dm_create            #
#                                          #
############################################

def test_dm_create_invalid_u_id(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    u_ids = [user1['auth_user_id'], 2312312]
    # Create a dm between user1 and invalid user with user2 being owner
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 400

def test_dm_create(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    u_ids = [user1['auth_user_id'], user3['auth_user_id']]
    # Create a dm with user1 and user3 with user2 being the owner
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    u_ids = [user1['auth_user_id'], user2['auth_user_id']]
    # Create another dm with user1 and user2 with user3 being the owner
    response2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user3['token'],
                            'u_ids': u_ids
                            })
    assert response2.status_code == 200
    data_response2 = response2.json()

    assert data_response['dm_id'] != data_response2['dm_id']

############################################
#                                          #
#            Tests for dm_list             #
#                                          #
############################################

def test_dm_list(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    u_ids = [user1['auth_user_id'], user3['auth_user_id']]
    # Create a dm with user1 and user3 with user2 being the owner
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()
    # Create another dm with user1 and user2 with user3 being the owner
    u_ids = [user1['auth_user_id'], user2['auth_user_id']]
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user3['token'],
                            'u_ids': u_ids
                            })

    response = requests.get(f"{BASE_URL}/dm/list/v1", params = {
                            'token': user3['token'],
                            })
    assert response.status_code == 200

    data_response2 = response.json()
    assert len(data_response2['dms']) == 2
    assert data_response2['dms'][0]['dm_id'] == data_response['dm_id']
    assert data_response2['dms'][0]['name'] == 'givensur, givensur0, givensur1'

############################################
#                                          #
#           Tests for dm_remove            #
#                                          #
############################################

def test_dm_remove_invalid_dm_id(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    u_ids = [user1['auth_user_id']]
    # Create a dm with user1 and user2 being the owner
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })

    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
                            'token': user2['token'], 'dm_id': 2132312
                            })
    assert response.status_code == 400

def test_dm_remove_invalid_owner(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    u_ids = [user1['auth_user_id']]
    # Create a dm with user1 and user2 being the owner
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })

    data_response = response.json()
    # User1 tries to remove dm but is not an owner
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
                            'token': user1['token'], 'dm_id': data_response['dm_id']
                            })
    assert response.status_code == 403

def test_dm_remove(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    # Create a dm with user1 and user3 with user2 being the owner
    u_ids = [user1['auth_user_id'], user3['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    u_ids = [user3['auth_user_id']]
    # Create a private dm with just user2 and user 3
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    # Now check the dms that user3 is in
    response = requests.get(f"{BASE_URL}/dm/list/v1", params = {
                            'token': user3['token'],
                            })
    assert response.status_code == 200

    data_response2 = response.json()
    assert len(data_response2['dms']) == 2

    requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
                            'token': user2['token'], 'dm_id': data_response['dm_id']
                            })
    # Now check the dms that user3 is in
    response = requests.get(f"{BASE_URL}/dm/list/v1", params = {
                            'token': user3['token'],
                            })
    assert response.status_code == 200

    data_response2 = response.json()
    assert len(data_response2['dms']) == 1

############################################
#                                          #
#          Tests for dm_details            #
#                                          #
############################################

def test_dm_details_invalid_dm(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    u_ids = [user1['auth_user_id']]
    # Create a dm with user1 and user2 being the owner
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    # Invalid dm id is used
    response = requests.get(f"{BASE_URL}/dm/details/v1", params = {
                            'token': user2['token'], 'dm_id': 2132312
                            })
    assert response.status_code == 400

def test_dm_details_invalid_member(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    # Create a dm with user1 and user2 being the owner
    u_ids = [user1['auth_user_id']]
    # Create a dm with user1 and user2 being the owner
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    data_response = response.json()
    # User3 tries to get the details of a dm
    response = requests.get(f"{BASE_URL}/dm/details/v1", params = {
                            'token': user3['token'], 'dm_id': data_response['dm_id']
                            })
    assert response.status_code == 403

def test_dm_details_return_format(setup):

    user = register_user().json()

    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user['token'], 'u_ids': []}).json()
    data = requests.get(f"{BASE_URL}/dm/details/v1", params = {
        'token': user['token'], 'dm_id': dm['dm_id']}).json()

    assert data['name'] == 'givensur'
    assert len(data['members']) == 1
    assert data['members'][0]['u_id'] == user['auth_user_id']
    assert data['members'][0]['email'] == 'user@mail.com'
    assert data['members'][0]['name_first'] == 'given'
    assert data['members'][0]['name_last'] == 'sur'

def test_dm_details(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    # Create a dm with user1 and user3 with user2 being the owner
    u_ids = [user1['auth_user_id'], user3['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    # User1 wants to get the details of a dm
    response = requests.get(f"{BASE_URL}/dm/details/v1", params = {
                            'token': user1['token'], 'dm_id': data_response['dm_id']
                            })
    assert response.status_code == 200
    data_response = response.json()

    assert data_response['name'] == 'givensur, givensur0, givensur1'
    assert len(data_response['members']) == 3

def test_dm_details_user_removed(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
        'token': user1['token'], 'u_id': user2['auth_user_id']})
    data = requests.get(f"{BASE_URL}/dm/details/v1", params = {
        'token': user1['token'], 'dm_id': dm['dm_id']}).json()

    assert len(data['members']) == 1

############################################
#                                          #
#           Tests for dm_leave             #
#                                          #
############################################

def test_dm_leave_invalid_dm(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    # Create a dm with user1 and user2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    # Invalid dm id is used
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json = {
                            'token': user2['token'], 'dm_id': 2132312
                            })
    assert response.status_code == 400

def test_dm_leave_invalid_member(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    # Create a dm with user1 and user2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    data_response = response.json()
    # User3 tries to leave
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json = {
                            'token': user3['token'], 'dm_id': data_response['dm_id']
                            })
    assert response.status_code == 403

def test_dm_leave(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    # Create a dm with user1 and user3 with user2 being the owner
    u_ids = [user1['auth_user_id'], user3['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    # Now check the dms that user2 is in
    response = requests.get(f"{BASE_URL}/dm/list/v1", params = {
                            'token': user2['token'],
                            })
    assert response.status_code == 200

    data_response2 = response.json()
    assert len(data_response2['dms']) == 1

    # User1 wants to check the details of the dm
    response = requests.get(f"{BASE_URL}/dm/details/v1", params = {
                            'token': user1['token'], 'dm_id': data_response['dm_id']
                            })
    data_response3 = response.json()

    assert data_response3['name'] == 'givensur, givensur0, givensur1'
    assert len(data_response3['members']) == 3

    # User2 now wants to leave due to bullying
    requests.post(f"{BASE_URL}/dm/leave/v1", json = {
                            'token': user2['token'], 'dm_id': data_response['dm_id']
                            })

    # Now check the dms that user2 is in
    response = requests.get(f"{BASE_URL}/dm/list/v1", params = {
                            'token': user2['token'],
                            })
    data_response2 = response.json()
    assert len(data_response2['dms']) == 0

    # User1 wants to check the details of the dm
    response = requests.get(f"{BASE_URL}/dm/details/v1", params = {
                            'token': user1['token'], 'dm_id': data_response['dm_id']
                            })
    data_response3 = response.json()

    assert data_response3['name'] == 'givensur, givensur0, givensur1'
    assert len(data_response3['members']) == 2

############################################
#                                          #
#          Tests for dm_messages           #
#                                          #
############################################

# Test for invalid channel_id
def test_dm_messages_invalid_channel_id(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    # User1 wants to check the details of the dm
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                            'token': user1['token'],
                            'dm_id': 51951595919,
                            'start': 10
                            })

    assert response.status_code == 400

# Test for invalid start value (start > # of messages)
def test_dm_messages_invalid_start(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    # Create a dm with user1 and user2 with user2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                            'token': user1['token'],
                            'dm_id': data_response['dm_id'],
                            'start': 145236987
                            })
    assert response.status_code == 400

# Test for message_id across different channels
def test_dm_messages_unauthorised(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    # Create a dm with user1 and user2 with user2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                            'token': user3['token'],
                            'dm_id': data_response['dm_id'],
                            'start': 145236987
                            })
    assert response.status_code == 403

# Test for valid response
def test_dm_messages_valid_return(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    # Create a dm with user1 and user2 with user2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    message_senddm(user1['token'], data_response['dm_id'], 'Hehe fun message')

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response['dm_id'],
                                'start': 0
                                })
    message_return = response.json()

    assert message_return['messages'][0]['message'] == 'Hehe fun message'
    assert message_return['start'] == 0
    assert message_return['end'] == -1

# Test for 124 messages correct returns
def test_dm_messages_124(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    # Create a dm with user1 and user2 with user2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    # Send 124 messages
    counter = 0
    while counter < 125:
        message_senddm(user1['token'], data_response['dm_id'], 'Help')
        counter += 1

    # Pull messages 0-50
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response['dm_id'],
                                'start': 0
                                })
    message_return50 = response.json()

    # Pull messages 50-100
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response['dm_id'],
                                'start': 50
                                })
    message_return100 = response.json()

    # Pull messages 100 - 124
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response['dm_id'],
                                'start': 100
                                })
    message_return124 = response.json()

    # Asserting for first 50 mesasges
    assert message_return50['start'] == 0
    assert message_return50['end'] == 50

    # Asserting for first 100 mesasges
    assert message_return100['start'] == 50
    assert message_return100['end'] == 100

    # Asserting for first 100 mesasges
    assert message_return124['start'] == 100
    assert message_return124['end'] == -1

def test_dm_messages_user_removed(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    dm = requests.post( f"{BASE_URL}/dm/create/v1", json = {
                        'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()
    # Create an extra DM for coverage
    requests.post(  f"{BASE_URL}/dm/create/v1", json = {
                    'token': user1['token'], 'u_ids': []})

    message_senddm(user1['token'], dm['dm_id'], "Test message")
    message_senddm(user2['token'], dm['dm_id'], "Test message")
    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})
    # user2 no longer exists
    data = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                        'token': user1['token'], 'dm_id': dm['dm_id'], 'start': 0}).json()

    assert data['messages'][0]['message'] == "Removed user"
    assert data['messages'][1]['message'] == "Test message"

############################################
#                                          #
#        Tests for message_senddm          #
#                                          #
############################################

# Test for invalid dm_id
def test_message_senddm_invalid_dm_id(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    # Create dm with user1 with user 2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    response2 = message_senddm(user1['token'], dm_id = 2, message = 'test')

    assert response2.status_code == 400

# Test for invalid member trying to send dm
def test_message_senddm_invalid_member(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    # Create dm with user1 with user 2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    # User3 tries to send dm but is not a member
    response2 = message_senddm(user3['token'], data_response['dm_id'], 'User3 message')

    assert response2.status_code == 403

# Test for message length
def test_message_senddm_long_message(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    # Create dm with user1 with user 2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

    # User 1 sends very long string
    response2 = message_senddm(user1['token'], data_response['dm_id'], message = long_string)

    assert response2.status_code == 400

# Testing for unique ids
def test_message_senddm_message_id(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    # Create dm with user1 with user 2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

     # User 1 sends 2 messages
    message_senddm(user1['token'], data_response['dm_id'], 'message one')
    message_senddm(user1['token'], data_response['dm_id'], 'message two')

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response['dm_id'],
                                'start': 0
                                })
    message_return = response.json()

    assert message_return['messages'][0]['message_id']\
        != message_return['messages'][1]['message_id']

# Test for time created
def test_message_senddm_time(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    # Create dm with user1 with user 2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response = response.json()

     # User 1 sends 1 message
    message_senddm(user1['token'], data_response['dm_id'], 'message one')
    # Get the time
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response['dm_id'],
                                'start': 0
                                })
    message_return = response.json()

    assert time == message_return['messages'][0]['time_created']

# Test for message_id across different channels
def test_message_senddm_across_dms(setup):
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    # Create dm with user1 with user 2 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user2['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response1 = response.json()
    # Create dm with user1 with user 3 being the owner
    u_ids = [user1['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user3['token'],
                            'u_ids': u_ids
                            })
    assert response.status_code == 200
    data_response2 = response.json()

    # User 1 sends a message to dm 1 and 2
    message_senddm(user1['token'], data_response1['dm_id'], 'message one')
    message_senddm(user1['token'], data_response2['dm_id'], 'message two')

    # Pull info from both dm sessions
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response1['dm_id'],
                                'start': 0
                                })
    message_return1 = response.json()
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params = {
                                'token': user1['token'],
                                'dm_id': data_response2['dm_id'],
                                'start': 0
                                })
    message_return2 = response.json()

    assert message_return1['messages'][0]['message_id']\
        != message_return2['messages'][0]['message_id']
