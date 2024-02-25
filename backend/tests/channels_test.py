import requests
from tests.helpers import BASE_URL, setup, register_user, create_channel

############################################
#                                          #
#      Tests for channels_create           #
#                                          #
############################################

def test_channels_create_name(setup):

    user = register_user().json()
    # Create bad channel names
    response1 = create_channel(token = user['token'], name = '')
    response2 = create_channel(token = user['token'], name = 'anameovertwentycharslong')

    assert response1.status_code == 400
    assert response2.status_code == 400

def test_channels_create_invalid_token(setup):

    # Attempt to create channel with invalid token
    response = create_channel(token = 323132)

    assert response.status_code == 403

def test_channels_create_invalid_public_status(setup):

    user = register_user().json()
    response = create_channel(token = user['token'], is_public = 'invalid')

    assert response.status_code == 400

def test_channels_create_duplicate_name(setup):

    user = register_user().json()
    response = create_channel(token = user['token'], name = 'ch_name')

    assert response.status_code == 200
    # Try to make another channel but with same name
    response = create_channel(token = user['token'], name = 'ch_name')

    assert response.status_code == 400

def test_channels_create_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel1 = create_channel(token = user1['token'], name = 'ch_first').json()
    channel2 = create_channel(token = user2['token'], name = 'ch_second').json()

    assert channel1['channel_id'] is not None
    assert channel2['channel_id'] is not None
    assert channel1['channel_id'] != channel2['channel_id']

############################################
#                                          #
#      Tests for channels_list             #
#                                          #
############################################

def test_channels_list(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    create_channel(token = user1['token'], name = 'ch_first')
    channel2 = create_channel(token = user2['token'], name = 'ch_second').json()

    # Get the channel that user2 is part of
    response = requests.get(f"{BASE_URL}/channels/list/v2", params = {'token': user2['token']})
    data = response.json()

    assert len(data['channels']) == 1
    assert data['channels'][0]['channel_id'] == channel2['channel_id']
    assert data['channels'][0]['name'] == 'ch_second'

############################################
#                                          #
#      Tests for channels_listall          #
#                                          #
############################################

def test_channels_listall_token_id(setup):

    response = requests.get(f"{BASE_URL}/channels/listall/v2", params = {'token': 32132})
    assert response.status_code == 403

def test_channels_listall_return_value(setup):

    user = register_user(email = 'user@mail.com').json()
    channel = create_channel(token = user['token'], name = 'ch_first').json()
    # Get all requested channels by user2
    response = requests.get(f"{BASE_URL}/channels/listall/v2", params = {
                            'token': user['token']})
    data = response.json()

    assert len(data['channels']) == 1
    assert data['channels'][0]['name'] == 'ch_first'
    assert data['channels'][0]['channel_id'] == channel['channel_id']

def test_channels_listall_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    create_channel(token = user1['token'], name = 'ch_first')
    create_channel(token = user2['token'], name = 'ch_second')

    # Get all requested channels by user2
    response = requests.get(f"{BASE_URL}/channels/listall/v2", params = {
                            'token': user2['token']})
    data = response.json()

    assert len(data['channels']) == 2
