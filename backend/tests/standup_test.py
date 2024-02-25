import requests
import time
from datetime import timezone, datetime
from tests.helpers import BASE_URL, setup, register_user, create_channel
from tests.helpers import message_get, long_string

############################################
#                                          #
#        Tests for standup_start           #
#                                          #
############################################

def test_standup_start_invalid_channel(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': 0, 'length': 0})
    assert response.status_code == 400

def test_standup_start_negative_length(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': -1})
    assert response.status_code == 400

def test_standup_start_already_active(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': 1})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': 1})
    assert response.status_code == 400

    time.sleep(1)

def test_standup_start_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user2['token'], 'channel_id': channel['channel_id'], 'length': 1})
    assert response.status_code == 403

def test_standup_start_return_format(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    data = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': 2}).json()

    timestamp = int(datetime.now(timezone.utc).timestamp())

    assert data['time_finish'] == timestamp + 2

    time.sleep(2)

############################################
#                                          #
#        Tests for standup_active          #
#                                          #
############################################

def test_standup_active_invalid_channel(setup):

    user = register_user().json()
    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': user['token'], 'channel_id': 0})
    assert response.status_code == 400

def test_standup_active_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': user2['token'], 'channel_id': channel['channel_id']})
    assert response.status_code == 403

def test_standup_active_is_active(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': 2}).json()

    timestamp = int(datetime.now(timezone.utc).timestamp())

    data = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': user['token'], 'channel_id': channel['channel_id']}).json()
    assert data['is_active'] is True
    assert data['time_finish'] == timestamp + 2

    time.sleep(2)

def test_standup_active_not_active(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    data = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': user['token'], 'channel_id': channel['channel_id']}).json()
    assert data['is_active'] is False
    assert data['time_finish'] is None

############################################
#                                          #
#         Tests for standup_send           #
#                                          #
############################################

def test_standup_send_invalid_channel(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        'token': user['token'], 'channel_id': 0, 'message': "test"})
    assert response.status_code == 400

def test_standup_send_too_long(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': 1})
    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'message': long_string})
    assert response.status_code == 400

    time.sleep(1)

def test_standup_send_not_active(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'message': "test"})
    assert response.status_code == 400

def test_standup_send_unauthorised(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    channel = create_channel(token = user1['token']).json()

    requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user1['token'], 'channel_id': channel['channel_id'], 'length': 1})
    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        'token': user2['token'], 'channel_id': channel['channel_id'], 'message': "test"})
    assert response.status_code == 403

    time.sleep(1)

def test_standup_send_flush_buffer(setup):

    user = register_user().json()
    channel = create_channel(token = user['token']).json()

    requests.post(f"{BASE_URL}/standup/start/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'length': 1})

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'message': "first"})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        'token': user['token'], 'channel_id': channel['channel_id'], 'message': "second"})
    assert response.status_code == 200

    time.sleep(1)

    data = message_get(user['token'], channel['channel_id'], start = 0).json()
    assert len(data['messages']) == 1
    assert data['messages'][0]['message'] == "givensur: first\ngivensur: second"
