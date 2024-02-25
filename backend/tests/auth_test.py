import requests
from tests.helpers import BASE_URL, setup, register_user, login_user

############################################
#                                          #
#      Tests for auth_register             #
#                                          #
############################################

def test_auth_register_invalid_email(setup):

    response = register_user(email = 'notanemail')
    assert response.status_code == 400

def test_auth_register_duplicate_email(setup):

    response1 = register_user(email = 'user@mail.com')
    response2 = register_user(email = 'user@mail.com')
    assert response1.status_code == 200
    assert response2.status_code == 400

def test_auth_register_short_password(setup):

    response = register_user(password = 'lol')
    assert response.status_code == 400

def test_auth_register_empty_name_first(setup):

    response = register_user(name_first = '')
    assert response.status_code == 400

def test_auth_register_empty_name_last(setup):

    response = register_user(name_last = '')
    assert response.status_code == 400

def test_auth_register_long_name_first(setup):

    response = register_user(name_first = 'anunreasonablylongnamelikethis1thatgoesonfortoolong')
    assert response.status_code == 400

def test_auth_register_long_name_last(setup):

    response = register_user(name_last = 'anunreasonablylongnamelikethis1thatgoesonfortoolong')
    assert response.status_code == 400

def test_auth_register_long_handle(setup):

    response = register_user(name_first = 'morethan', name_last = 'twentycharacters')
    assert response.status_code == 200

def test_auth_register_same_name_users(setup):

    register_user(email = 'user1@mail.com', name_first = 'given', name_last = 'sur')
    response = register_user(email = 'user2@mail.com', name_first = 'given', name_last = 'sur')
    assert response.status_code == 200

def test_auth_register_diff_name_users(setup):

    register_user(email = 'user1@mail.com', name_first = 'given1', name_last = 'sur')
    response = register_user(email = 'user2@mail.com', name_first = 'given2', name_last = 'sur')
    assert response.status_code == 200

def test_auth_register_user_removed(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})
    response = register_user(email = 'user2@mail.com')
    assert response.status_code == 200

############################################
#                                          #
#          Tests for auth_login            #
#                                          #
############################################

def test_auth_login_id_and_token(setup):

    reg_user = register_user().json()
    log_user = login_user().json()

    assert reg_user['auth_user_id'] == log_user['auth_user_id']
    assert reg_user['token'] != log_user['token']

def test_email_not_registered(setup):

    register_user(email = 'user@mail.com')
    response = login_user(email = 'notregistered@mail.com')
    assert response.status_code == 400

def test_wrong_password(setup):

    register_user(password = 'passwordxd')
    response = login_user(password = 'passwordxdd')
    assert response.status_code == 400

############################################
#                                          #
#          Tests for auth_logout           #
#                                          #
############################################

def test_auth_logout(setup):
    # This user is only present for coverage; they will not log out
    register_user(email = 'extra@mail.com', name_first = 'extra')

    reg_user = register_user().json()
    log_user = login_user().json()

    requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': reg_user['token']})

    # Only the log_user token should be valid after logging out from the reg_user token
    response1 = requests.get(f"{BASE_URL}/channels/list/v2",
                            params = {'token': reg_user['token']})
    response2 = requests.get(f"{BASE_URL}/channels/list/v2",
                            params = {'token': log_user['token']})

    assert response1.status_code == 403
    assert response2.status_code == 200

def test_auth_logout_double(setup):
    user = register_user().json()

    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': user['token']})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': user['token']})
    assert response.status_code == 403

def test_auth_logout_removed(setup):
    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
                    'token': user1['token'], 'u_id': user2['auth_user_id']})
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': user2['token']})
    assert response.status_code == 403

############################################
#                                          #
#   Tests for auth_passwordreset_request   #
#                                          #
############################################

def test_auth_passwordreset_request(setup):

    register_user(email = 'fixfork@gmail.com').json()
    email = 'fixfork@gmail.com'
    response = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json = {'email': email})
    assert response.status_code == 200

def test_auth_passwordreset_logout_sessions(setup):
    
    reg_user = register_user(email = 'fixfork@gmail.com').json()
    log_user = login_user(email = 'fixfork@gmail.com').json()
    email = 'fixfork@gmail.com'
    response = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json = {'email': email})
    assert response.status_code == 200
    # None of the tokens will be valid as they are now log out from all sessions
    response1 = requests.get(f"{BASE_URL}/channels/list/v2",
                            params = {'token': reg_user['token']})
    response2 = requests.get(f"{BASE_URL}/channels/list/v2",
                            params = {'token': log_user['token']})

    assert response1.status_code == 403
    assert response2.status_code == 403

############################################
#                                          #
#   Tests for auth_passwordreset_reset     #
#                                          #
############################################

def test_auth_passwordreset_invalid_code(setup):
    user = {'reset_code': '2312', 'new_password': 'newpassword'}
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json = user)
    assert response.status_code == 400
