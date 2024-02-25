import requests

from src.config import url
'''
from src.echo import echo
from src.error import InputError

def test_echo_iter1():
    assert echo("1") == "1", "1 == 1"
    assert echo("abc") == "abc", "abc == abc"
    assert echo("trump") == "trump", "trump == trump"

def test_echo_except():
    with pytest.raises(InputError):
        assert echo("echo")
'''
def test_echo():
    response = requests.get(url + '/echo', params = {'data': 'hello'})
    assert response.json() == {'data': 'hello'}
