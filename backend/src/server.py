import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory, send_file
from flask_cors import CORS
from src.error import InputError, AccessError
from src import config
from src.data_store import data_store
from src.token import token_generate, decode_jwt, generate_jwt
from src.token import generate_new_session_id, valid_session
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1
from src.auth import auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_details_v1, channel_messages_v1, channel_invite_v1
from src.channel import channel_join_v1, channel_leave_v1
from src.channel import channel_addowner_v1, channel_removeowner_v1
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1
from src.dm import dm_details_v1, dm_leave_v1, dm_messages_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1
from src.message import message_senddm_v1, message_pin_v1, message_unpin_v1
from src.message import message_react_v1, message_unreact_v1, message_share_v1
from src.message import message_sendlater_v1, message_sendlaterdm_v1
from src.search import search_v1
from src.user import users_all_v1, user_profile_v1, user_profile_setname_v1
from src.user import user_profile_setemail_v1, user_profile_sethandle_v1
from src.user import user_stats, users_stats, user_uploadphoto
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.notifications import notifications_get_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        'code': err.code,
        'name': 'System Error',
        'message': err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

def get_u_id(token):

    session = decode_jwt(token)

    if not valid_session(session):
        raise AccessError("Invalid token")

    return session['u_id']

'''
<echo>
'''
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    return dumps({'data': data})

'''
<clear_v1>
'''
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    return dumps(clear_v1())

'''
<auth_register_v1>
'''
@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()
    return dumps(auth_register_v1(  data['email'], data['password'],
                                    data['name_first'], data['name_last']))

'''
<auth_login_v1>
'''
@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()
    return dumps(auth_login_v1(data['email'], data['password']))

'''
<auth/logout/v1>
'''
@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    data = request.get_json()
    return dumps(auth_logout_v1(data['token']))

'''
<auth/passwordreset/request/v1>
'''
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def pass_request():
    data = request.get_json()
    return dumps(auth_passwordreset_request_v1(data['email']))

'''
<auth/passwordreset/reset/v1>
'''
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def pass_reset():
    data = request.get_json()
    return dumps(auth_passwordreset_reset_v1(data['reset_code'], data['new_password']))

'''
<channels/create/v2>
'''
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    data = request.get_json()
    u_id = get_u_id(data['token'])
    return dumps(channels_create_v1(u_id, data['name'], data['is_public']))

'''
<channels/list/v2>
'''
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    auth_user_id = get_u_id(token)
    return dumps(channels_list_v1(auth_user_id))

'''
<channels/listall/v2>
'''
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get('token')
    auth_user_id = get_u_id(token)
    return dumps(channels_listall_v1(auth_user_id))

'''
<channel/details/v2>
'''
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    data = request.args.to_dict()
    channel_id = int(data['channel_id'])
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_details_v1(auth_user_id, channel_id))

'''
<channel/join/v2>
'''
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_join_v1(auth_user_id, data['channel_id']))

'''
<channel/invite/v2>
'''
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_invite_v1(auth_user_id, data['channel_id'], data['u_id']))

'''
<channel/leave/v1>
'''
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_leave_v1(auth_user_id, data['channel_id']))

'''
<channel/addowner/v1>
'''
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_addowner_v1(auth_user_id, data['channel_id'], data['u_id']))

'''
<channel/removeowner/v1>
'''
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_removeowner_v1(auth_user_id, data['channel_id'], data['u_id']))

'''
<channel/messages/v2>
'''
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    data = request.args.to_dict()
    channel_id = int(data['channel_id'])
    start = int(data['start'])
    auth_user_id = get_u_id(data['token'])
    return dumps(channel_messages_v1(auth_user_id, channel_id, start))

'''
<message/send/v1>
'''
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_send_v1(auth_user_id, data['channel_id'], data['message']))

'''
<message/edit/v1>
'''
@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    message_edit_v1(auth_user_id, data['message_id'], data['message'])
    return dumps({})

'''
<message/remove/v1>
'''
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_remove_v1(auth_user_id, data['message_id']))

'''
<message/pin/v1>
'''
@APP.route("/message/pin/v1", methods = ['POST'])
def message_pin():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_pin_v1(auth_user_id, data['message_id']))

'''
<message/unpin/v1>
'''
@APP.route("/message/unpin/v1", methods = ['POST'])
def message_unpin():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_unpin_v1(auth_user_id, data['message_id']))

'''
<message/share/v1>
'''
@APP.route("/message/share/v1", methods = ['POST'])
def message_share():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_share_v1(auth_user_id, data['og_message_id'],
        data['message'], data['channel_id'], data['dm_id']))

'''
<message/react/v1>
'''
@APP.route("/message/react/v1", methods = ['POST'])
def message_react():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_react_v1(auth_user_id, data['message_id'], data['react_id']))

'''
<message/unreact/v1>
'''
@APP.route("/message/unreact/v1", methods = ['POST'])
def message_unreact():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_unreact_v1(auth_user_id, data['message_id'], data['react_id']))

'''
<message/sendlater/v1>
'''
@APP.route("/message/sendlater/v1", methods = ['POST'])
def message_sendlater():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_sendlater_v1(auth_user_id,
        data['channel_id'], data['message'], data['time_sent']))

'''
<message/sendlaterdm/v1>
'''
@APP.route("/message/sendlaterdm/v1", methods = ['POST'])
def message_sendlaterdm():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_sendlaterdm_v1(auth_user_id,
        data['dm_id'], data['message'], data['time_sent']))

############################################
#                                          #
#          search implementation           #
#                                          #
############################################

'''
<search/v1>
'''
@APP.route("/search/v1", methods=['GET'])
def search():
    data = request.args.to_dict()
    auth_user_id = get_u_id(data['token'])
    return dumps(search_v1(auth_user_id, str(data['query_str'])))

############################################
#                                          #
#          standup implementation          #
#                                          #
############################################

'''
<standup/start/v1>
'''
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(standup_start_v1(auth_user_id, data['channel_id'], data['length']))

'''
<standup/active/v1>
'''
@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    data = request.args.to_dict()
    auth_user_id = get_u_id(data['token'])
    return dumps(standup_active_v1(auth_user_id, int(data['channel_id'])))

'''
<standup/send/v1>
'''
@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(standup_send_v1(auth_user_id, data['channel_id'], data['message']))

############################################
#                                          #
#            dm implementation             #
#                                          #
############################################

'''
<dm/create/v1>
'''
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(dm_create_v1(auth_user_id, data['u_ids']))

'''
<dm/list/v1>
'''
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    auth_user_id = get_u_id(token)
    return dumps(dm_list_v1(auth_user_id))

'''
<dm/remove/v1>
'''
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(dm_remove_v1(auth_user_id, data['dm_id']))

'''
<dm/details/v1>
'''
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    data = request.args.to_dict()
    dm_id = int(data['dm_id'])
    auth_user_id = get_u_id(data['token'])
    return dumps(dm_details_v1(auth_user_id, dm_id))

'''
<dm/leave/v1>
'''
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(dm_leave_v1(auth_user_id, data['dm_id']))

'''
<dm/messages/v1>
'''
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_message():
    data = request.args.to_dict()
    dm_id = int(data['dm_id'])
    start = int(data['start'])
    auth_user_id = get_u_id(data['token'])
    return dumps(dm_messages_v1(auth_user_id, dm_id, start))

'''
<message/senddm/v1>
'''
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(message_senddm_v1(auth_user_id, data['dm_id'], data['message']))

############################################
#                                          #
#        user implementation               #
#                                          #
############################################

'''
<users/all/v1>
'''
@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get('token')

    if not valid_session(decode_jwt(token)):
        raise AccessError("Invalid token")

    return dumps(users_all_v1())

'''
<user/profile/v1>
'''
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    data = request.args.to_dict()
    token = data['token']

    if not valid_session(decode_jwt(token)):
        raise AccessError("Invalid token")

    u_id = int(data['u_id'])

    return dumps(user_profile_v1(u_id))

'''
<user/profile/setname/v1>
'''
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_setname():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(user_profile_setname_v1(auth_user_id, data['name_first'], data['name_last']))

'''
<user/profile/setemail/v1>
'''
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_set_email():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(user_profile_setemail_v1(auth_user_id, data['email']))

'''
<user/profile/sethandle/v1>
'''
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_set_handlestr():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(user_profile_sethandle_v1(auth_user_id, data['handle_str']))

'''
<user/stats/v1>
'''
@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_server():
    token = request.args.get('token')
    auth_user_id = get_u_id(token)
    return dumps(user_stats('print', auth_user_id, 1))

'''
<users/stats/v1>
'''
@APP.route("/users/stats/v1", methods=['GET'])
def users_stats_server():
    token = request.args.get('token')
    auth_user_id = get_u_id(token)
    return dumps(users_stats('print', auth_user_id, 1))

'''
<user/profile/uploadphoto/v1>
'''
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_uploadphoto_server():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    user_uploadphoto(auth_user_id, data['img_url'],
        data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    return dumps({})

@APP.route('/profilephoto/<variable>')
def send_js(variable):
    return send_file(variable, mimetype='image/jpg')


############################################
#                                          #
#        admin implementation              #
#                                          #
############################################

'''
admin/user/remove/v1
'''
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(admin_user_remove_v1(auth_user_id, data['u_id']))

'''
admin/userpermission/change/v1
'''
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    data = request.get_json()
    auth_user_id = get_u_id(data['token'])
    return dumps(admin_userpermission_change_v1(auth_user_id, data['u_id'],
                                                data['permission_id']))

############################################
#                                          #
#       notification implementation        #
#                                          #
############################################

'''
<notifications/get/v1>
'''
@APP.route("/notifications/get/v1", methods=['GET'])
def get_notifications():
    token = request.args.get('token')
    auth_user_id = get_u_id(token)
    return dumps(notifications_get_v1(auth_user_id))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
