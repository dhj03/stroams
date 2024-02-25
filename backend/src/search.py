import pytest
from src.data_store import data_store
from src.error import InputError

'''
<search_v1>

Returns a list of messages in all of the channels/DMs
that the user has joined that contain the query string

Arguments:
    'u_id' (int)        - ID of user
    'query_str' (str)   - String of query

Exceptions:
    InputError  - Length of query is less than 1 or over 1000 characters

Return Value:
    Returns {'messages'}
'''
def search_v1(u_id, query_str):

    length = len(query_str)
    if not (1 <= length <= 1000):
        raise InputError("Length of query is less than 1 or over 1000 characters")

    store = data_store.get()

    messages = []

    for channel in store['channels']:
        if u_id in channel['all_members']:
            for message in channel['messages']:
                if query_str in message['message']:
                    messages.append(message)

    for dm in store['dms']:
        if u_id in dm['members']:
            for message in dm['messages']:
                if query_str in message['message']:
                    messages.append(message)

    return {'messages': messages}
