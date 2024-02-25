import requests
from tests.helpers import BASE_URL, setup, register_user, create_channel
from tests.helpers import message_send, message_get, message_senddm, long_string

def test_search_query_too_short(setup):

    user = register_user().json()
    response = requests.get(f"{BASE_URL}/search/v1", params = {
        'token': user['token'], 'query_str': ""})
    assert response.status_code == 400

def test_search_query_too_long(setup):

    user = register_user().json()
    response = requests.get(f"{BASE_URL}/search/v1", params = {
        'token': user['token'], 'query_str': long_string})
    assert response.status_code == 400

def test_search_return_format(setup):

    user = register_user().json()

    channel = create_channel(token = user['token']).json()
    message_send(user['token'], channel['channel_id'], "some relevant text").json()
    data = message_get(user['token'], channel['channel_id'], start = 0).json()
    msg = data['messages']

    data = requests.get(f"{BASE_URL}/search/v1", params = {
        'token': user['token'], 'query_str': "me relevant"}).json()
    assert data['messages'] == msg

def test_search_count(setup):

    user = register_user().json()

    channel = create_channel(token = user['token']).json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user['token'], 'u_ids': []}).json()

    message_send(user['token'], channel['channel_id'], "some irrelevant text")
    message_send(user['token'], channel['channel_id'], "some relevant text")
    message_senddm(user['token'], dm['dm_id'], "some relevant text")
    message_senddm(user['token'], channel['channel_id'], "some other irrelevant text")

    data = requests.get(f"{BASE_URL}/search/v1", params = {
        'token': user['token'], 'query_str': "me relevant"}).json()
    assert len(data['messages']) == 2

def test_not_in_channel_or_dm(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()

    channel = create_channel(token = user1['token']).json()
    dm = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': user1['token'], 'u_ids': []}).json()

    message_send(user1['token'], channel['channel_id'], "some text")
    message_senddm(user1['token'], dm['dm_id'], "some text")

    data = requests.get(f"{BASE_URL}/search/v1", params = {
        'token': user1['token'], 'query_str': "text"}).json()
    assert len(data['messages']) == 2
    data = requests.get(f"{BASE_URL}/search/v1", params = {
        'token': user2['token'], 'query_str': "text"}).json()
    assert len(data['messages']) == 0
