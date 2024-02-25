import requests
from tests.helpers import BASE_URL, setup, register_user, create_channel
from tests.helpers import message_send, message_senddm

############################################
#                                          #
#      Tests for user_all                  #
#                                          #
############################################

def test_user_all(setup):

    # Set up the users
    user = register_user().json()

    data = requests.get(f"{BASE_URL}/users/all/v1", params = {'token': user['token']}).json()
    # Assert the response is as expected
    assert len(data['users']) == 1
    assert data['users'][0]['u_id'] == 0
    assert data['users'][0]['email'] == 'user@mail.com'

    register_user(email = 'user2@mail.com')

    data = requests.get(f"{BASE_URL}/users/all/v1", params = {'token': user['token']}).json()
    assert len(data['users']) == 2

def test_user_all_removed(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})

    data = requests.get(f"{BASE_URL}/users/all/v1", params = {'token': user1['token']}).json()
    assert len(data['users']) == 1

############################################
#                                          #
#      Tests for user_profile              #
#                                          #
############################################

def test_user_profile(setup):

    # Register some other users to activate loop
    register_user(email = 'john@gmail.com')
    register_user(email = 'john1@gmail.com')

    # Set up the user
    user = register_user().json()

    # Add some other users
    register_user(email = 'john2@gmail.com')


    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user['token'], 'u_id': user['auth_user_id']}).json()

    # Assert the response is as expected
    assert data['user']['email'] == 'user@mail.com'
    assert data['user']['u_id'] == 2


def test_user_profile_invalid_user_id(setup):

    # Register some other users to activate loop
    register_user(email = 'john@gmail.com')
    register_user(email = 'john1@gmail.com')
    register_user(email = 'john2@gmail.com')

    # Set up the user
    user = register_user().json()

    response = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                            'token': user['token'], 'u_id': user['auth_user_id'] + 1})

    # Assert the response is as expected
    assert response.status_code == 400

def test_user_profile_user_removed(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})
    data = requests.get(f"{BASE_URL}/user/profile/v1", params = {
                        'token': user1['token'], 'u_id': user2['auth_user_id']}).json()
    assert data['user']['name_first'] == 'Removed'
    assert data['user']['name_last'] == 'user'

############################################
#                                          #
#      Tests for user_profile_setname      #
#                                          #
############################################

def test_user_profile_setname_invalid_first_name(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}user/profile/setname/v1", json = {
                            'token': register['token'],
                            'name_first': 'thisnameijohsodhoihsoihdoihsohdoihsiodhoishdoihoisd',
                            'name_last': 'smith'})
    assert response.status_code == 400

def test_user_profile_setname_invalid_last_name(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}user/profile/setname/v1", json = {
                            'token': register['token'], 'name_first': 'john',
                            'name_last': 'ggygwiuyeuiyweiugiuwegiuwgeiugwiugiugweiugweiuuiewi'})
    assert response.status_code == 400


def test_user_profile_setname(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}user/profile/setname/v1", json = {
                            'token': register['token'],
                            'name_first': 'john', 'name_last': 'smith'})
    assert response.status_code == 200
    assert response.json() == {}

############################################
#                                          #
#      Tests for user_profile_setemail     #
#                                          #
############################################

def test_user_profile_setemail_invalid(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = {
                            'token': register['token'], 'email': 'invalid123'})
    assert response.status_code == 400

def test_user_profile_valid_email(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = {
                            'token': register['token'], 'email': 'email@gmail.com'})
    assert response.status_code == 200

def test_user_profile_duplicate_email_user(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = {
                            'token': register['token'], 'email': 'user@mail.com'})
    assert response.status_code == 400

############################################
#                                          #
#      Tests for user_profile_sethandle    #
#                                          #
############################################

def test_user_profile_handlestr_non_alphanumeric(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = {
                            'token': register['token'], 'handle_str': '^(&hsj445'})
    assert response.status_code == 400

def test_user_profile_long_handlestr(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = {
                            'token': register['token'],
                            'handle_str': 'thishndlestringiswaytoolong'})
    assert response.status_code == 400

def test_user_profile_duplicate_handle_str(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = {
                            'token': register['token'], 'handle_str': 'givensur'})
    assert response.status_code == 400

def test_user_profile_vaild_handle_str(setup):

    register = register_user().json()
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = {
                            'token': register['token'], 'handle_str': 'vaild'})
    assert response.status_code == 200


############################################
#                                          #
#      Tests for user_stats                #
#                                          #
############################################

def test_user_stats_simple(setup):

    # Create the users
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    user4 = register_user(email = 'user4@gmail.com').json()

    # Make a channel
    channel = create_channel(user1['token']).json()

    # Add a different person to the channell
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': user4['token'], 'channel_id': channel['channel_id']})

    # Send a message
    message_send(user1['token'], channel["channel_id"], "whatever")
    message_send(user4['token'], channel["channel_id"], "whpllr")

    # Create a DM
    u_ids = [user2['auth_user_id'], user3['auth_user_id']]
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user1['token'],
                            'u_ids': u_ids
                            }).json()

    # Send a DM message
    message_senddm(user1['token'], dm['dm_id'], 'Help')
    message_senddm(user2['token'], dm['dm_id'], 'ok')

    # Get the statistics
    stats = requests.get(f"{BASE_URL}/user/stats/v1",
                        params = {'token': user1['token']}).json()

    print(stats)

    # Assert the response
    assert stats['user_stats']['channels_joined'][1]['num_channels_joined'] == 1
    assert stats['user_stats']['messages_sent'][2]['num_messages_sent'] == 2
    assert stats['user_stats']['dms_joined'][1]['num_dms_joined'] == 1

def test_nothing_registered_user_stats(setup):

    # Create the users
    user1 = register_user(email = 'user1@gmail.com').json()

    # Get the statistics
    stats = requests.get(f"{BASE_URL}/user/stats/v1",
                        params = {'token': user1['token']}).json()

    # Assert the response
    assert stats['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stats['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 0

def test_user_part_of_everything(setup):

    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()

    # Make a channel
    channel = create_channel(user1['token']).json()

    # Send a message
    message_send(user1['token'], channel["channel_id"], "whatever")

    # Create a DM
    u_ids = [user2['auth_user_id'], user3['auth_user_id']]
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user1['token'],
                            'u_ids': u_ids
                            })

    # Get the statistics
    stats = requests.get(f"{BASE_URL}/user/stats/v1",
                        params = {'token': user1['token']}).json()

    # Assert the response
    assert stats['user_stats']['channels_joined'][1]['num_channels_joined'] == 1
    assert stats['user_stats']['messages_sent'][1]['num_messages_sent'] == 1
    assert stats['user_stats']['dms_joined'][1]['num_dms_joined'] == 1

############################################
#                                          #
#      Tests for users_stats               #
#                                          #
############################################

def test_users_stats_simple(setup):

    # Create the users
    user1 = register_user(email = 'user1@gmail.com').json()
    user2 = register_user(email = 'user2@gmail.com').json()
    user3 = register_user(email = 'user3@gmail.com').json()
    user4 = register_user(email = 'user4@gmail.com').json()

    # Make two channels
    channel1 = create_channel(user1['token']).json()
    channel2 = create_channel(user2['token'], name = 'ch_name1', is_public = True).json()
    create_channel(user2['token'], name = 'ch_name2', is_public = True).json()


    # Join a channel
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': user4['token'], 'channel_id': channel1['channel_id']})

    # Send a message
    message_send(user1['token'], channel1["channel_id"], "whatever")
    message_send(user2['token'], channel2["channel_id"], "hope this works")

    # Create two DMs
    u_ids1 = [user1['auth_user_id'], user2['auth_user_id']]
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user1['token'],
                            'u_ids': u_ids1
                            })

    u_ids2 = [user1['auth_user_id'], user3['auth_user_id']]
    requests.post(f"{BASE_URL}/dm/create/v1", json = {
                            'token': user1['token'],
                            'u_ids': u_ids2
                            })

    # Get the statistics
    stats = requests.get(f"{BASE_URL}/users/stats/v1",
                        params = {'token': user2['token']}).json()

    print(stats)

    # Assert the response
    assert stats['workspace_stats']['channels_exist'][3]['num_channels_exist'] == 3
    assert stats['workspace_stats']['dms_exist'][2]['num_dms_exist'] == 2
    assert stats['workspace_stats']['messages_exist'][2]['num_messages_exist'] == 2

def test_users_stats_nothing_registered(setup):

    # Create the users
    user1 = register_user(email = 'user1@gmail.com').json()

    # Get the statistics
    stats = requests.get(f"{BASE_URL}/users/stats/v1",
                        params = {'token': user1['token']}).json()

    # Assert the response
    assert stats['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert stats['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0


############################################
#                                          #
#       Tests for user_upload_photo        #
#                                          #
############################################

# Test start out of dimention
def test_dimentions(setup):

    user = register_user().json()
    response = requests.post( f"{BASE_URL}user/profile/uploadphoto/v1", json = {
                                'token': user['token'], 
                                'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                'x_start' : 1,
                                'y_start' : 1,
                                'x_end' : 60,
                                'y_end' : 60 
                                })

    assert response.status_code == 200

# Test for invalid crop s
def test_invalid_crop(setup):

    user = register_user().json()
    response = requests.post( f"{BASE_URL}user/profile/uploadphoto/v1", json = {
                                'token': user['token'], 
                                'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                'x_start' : 5,
                                'y_start' : 5,
                                'x_end' : 1,
                                'y_end' : 1 
                                })
                                
    assert response.status_code == 400

# Test for invalid crop s
def test_invalid_crop1(setup):

    user = register_user().json()
    response = requests.post( f"{BASE_URL}user/profile/uploadphoto/v1", json = {
                                'token': user['token'], 
                                'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                'x_start' : 5,
                                'y_start' : 5,
                                'x_end' : 6,
                                'y_end' : 1 
                                })
                                
    assert response.status_code == 400

# Test for invalid crop s
def test_too_large_x(setup):

    user = register_user().json()
    response = requests.post( f"{BASE_URL}user/profile/uploadphoto/v1", json = {
                                'token': user['token'], 
                                'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                'x_start' : 100000,
                                'y_start' : 5,
                                'x_end' : 6,
                                'y_end' : 1 
                                })
                                
    assert response.status_code == 400

# Test for invalid crop s
def test_too_large_x1(setup):

    user = register_user().json()
    response = requests.post( f"{BASE_URL}user/profile/uploadphoto/v1", json = {
                                'token': user['token'], 
                                'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                'x_start' : 1,
                                'y_start' : 1,
                                'x_end' : 100000,
                                'y_end' : 5 
                                })
                                
    assert response.status_code == 400

# Test for invalid crop s
def test_too_large_y(setup):

    user = register_user().json()
    response = requests.post( f"{BASE_URL}user/profile/uploadphoto/v1", json = {
                                'token': user['token'], 
                                'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                'x_start' : 1,
                                'y_start' : 5,
                                'x_end' : 6,
                                'y_end' : 100000 
                                })
                                
    assert response.status_code == 400
