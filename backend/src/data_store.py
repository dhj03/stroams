import json
import os.path
'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it:)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

initial_object = {

    'session_num': 0,

    'message_num': 0,

    'users': [
#       {
#            'email': 'user_email',
#            'password': 'user_password',
#            'name_first': 'user_name_first',
#            'name_last': 'user_name_last',
#            'handle_str': 'user_handle_str',
#            'permission_id': 1,
#            'sessions': [],
#            'reset_code': '',
#            'stats': {
#                 'channels_joined': [{'num_channels_joined': 0, 'time_stamp': 0}],
#                 'dms_joined': [{'num_dms_joined': 0, 'time_stamp': 0}],
#                 'messages_sent': [{'num_messages_sent': 0, 'time_stamp': 0}],
#                 'involvement_rate': 0
#            },
#            'notifications':[]
#       },
    ],

    'channels': [
#        {
#             'name': 'channel0',
#             'is_public': 'True',
#             'owner_members': [
#                  0
#             ],
#             'all_members': [
#                  0
#             ],
#             'messages': [
#                  {
#                       'message_id': 0,
#                       'u_id': 0,
#                       'message': 'is a string',
#                       'time_created': 0,
#                       'reacts': {},
#                       'is_pinned': 'False'
#                  }
#             ],
#             'standup': {
#                  'time_finish': None,
#                  'messages': []
#             }
#        }
    ],

    'dms': [
#        {
#            'name': 'andwdd, bdnw2'
#            'members': []
#            'owner': user_id,
#            'messages': [
#               {
#                    'message_id': 0,
#                    'u_id': 0,
#                    'message': 'is a string',
#                    'time_created': 0
#                    'reacts': {},
#                    'is_pinned': 'True',
#               }
#           ]
#        }
    ],

    'workspace_stats' : {
#        'channels_exist': [{'num_channels_exist': 0, 'time_stamp': 0}],
#        'dms_exist': [{'num_dms_exist': 0, 'time_stamp': 0}],
#        'messages_exist': [{'num_messages_exist': 0, 'time_stamp': 0}],
#        'utilization_rate': 0
    }

}

if os.path.exists('data_store.json'):
    with open('data_store.json', 'r') as FILE:
        initial_object = json.load(FILE)

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):

        if not isinstance(store, dict):
            raise TypeError("Store must be of type dictionary")

        self.__store = store

        with open('data_store.json', 'w') as FILE:
            json.dump(store, FILE)

print("Loading Datastore...")

global data_store
data_store = Datastore()
