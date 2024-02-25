import pytest
import requests
from src.config import url as BASE_URL

long_string =  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

@pytest.fixture
def setup():
    requests.delete(f"{BASE_URL}/clear/v1")

# Helper functions
def register_user(  email = 'user@mail.com', password = 'passwordxd',
                    name_first = 'given', name_last = 'sur'):
    user = {'email': email, 'password': password,
            'name_first': name_first, 'name_last': name_last}
    return requests.post(f"{BASE_URL}/auth/register/v2", json = user)

def login_user(email = 'user@mail.com', password = 'passwordxd'):
    user = {'email': email, 'password': password}
    return requests.post(f"{BASE_URL}/auth/login/v2", json = user)

def create_channel(token, name = 'ch_name', is_public = True):
    channel = {'token': token, 'name': name, 'is_public': is_public}
    return requests.post(f"{BASE_URL}/channels/create/v2", json = channel)

def message_send(token, channel_id, message):
    message = {'token': token, 'channel_id': channel_id, 'message': message}
    return requests.post(f"{BASE_URL}/message/send/v1", json = message)

def message_get(token, channel_id, start):
    message = {'token': token, 'channel_id': channel_id, 'start': start}
    return requests.get(f"{BASE_URL}/channel/messages/v2", params = message)

def message_senddm(token, dm_id, message):
    message = {'token': token, 'dm_id': dm_id, 'message': message}
    return requests.post(f"{BASE_URL}/message/senddm/v1", json = message)

@pytest.fixture
def message_setup():
    requests.delete(f"{BASE_URL}/clear/v1")
    user = register_user(  email = 'haydensmaden@unsw.edu.au', password = 'password',
                        name_first = 'hayden', name_last = 'smith')
    user_id = login_user(email = 'hayden@unsw.edu.a', password = 'password')
    return (user, user_id)
