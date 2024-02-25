import re
from src.data_store import data_store
from src.error import InputError
from src.token import token_generate, decode_jwt, generate_jwt, generate_new_session_id

def test_encode_decode():
    jwt = generate_jwt(0, 1)
    data = decode_jwt(jwt)

    assert data['u_id'] == 0
    assert data['session_id'] == 1

def test_format_jwt():

    token = generate_jwt(0, 1)

    regex = "^[A-Za-z0-9\\-_=]+\\.[A-Za-z0-9\\-_=]+(\\.[A-Za-z0-9\\-_.+/=]+)?$"

    assert re.fullmatch(regex, token) is not None

def test_different_jwt():
    jwt1 = generate_jwt(0, 1)
    jwt2 = generate_jwt(0, 2)

    assert jwt1 != jwt2
