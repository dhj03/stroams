import pytest
from src.data_store import data_store
from src.other import clear_v1

def test_clear_users():
    store = data_store.get()
    store['users'].append({'key': 'value'})
    data_store.set(store)
    clear_v1()
    assert store['users'] == []

def test_clear_channels():
    store = data_store.get()
    store['channels'].append({'key': 'value'})
    data_store.set(store)
    clear_v1()
    assert store['channels'] == []

def test_store_not_dict():
    with pytest.raises(TypeError):
        store = ['wrong', 'type', 'fool']
        data_store.set(store)
