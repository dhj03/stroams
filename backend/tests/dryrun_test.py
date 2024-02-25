import sys
import os
sys.path.append(os.getcwd())
from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_list_v1
from src.other import clear_v1


def test_clear():
    clear_v1()
    auth_register_v1('email@email.com', 'password', 'first', 'last')
    clear_v1()
    auth_register_v1('email@email.com', 'password', 'first', 'last')

def test_auth_register():
    clear_v1()
    data = auth_register_v1('email@email.com', 'password', 'first', 'last')
    assert isinstance(data, dict) and 'auth_user_id' in data and isinstance(data['auth_user_id'], int)

def test_channels_create():
    clear_v1()
    auth_user_id = auth_register_v1('email@email.com', 'password', 'first', 'last')['auth_user_id']
    data = channels_create_v1(auth_user_id, 'channel name', True)
    assert isinstance(data, dict) and 'channel_id' in data and isinstance(data['channel_id'], int)

def test_channels_list():
    name = 'channel name'
    clear_v1()
    auth_user_id = auth_register_v1('email@email.com', 'password', 'first', 'last')['auth_user_id']
    channel_id = channels_create_v1(auth_user_id, name, True)['channel_id']
    data = channels_list_v1(auth_user_id)
    assert isinstance(data, dict) and 'channels' in data and len(data['channels']) == 1
    assert isinstance(data['channels'][0], dict) and 'channel_id' in data['channels'][0] and 'name' in data['channels'][0]
    assert isinstance(data['channels'][0]['channel_id'], int) and data['channels'][0]['channel_id'] == channel_id
    assert isinstance(data['channels'][0]['name'], str) and data['channels'][0]['name'] == name
