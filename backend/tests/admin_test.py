import requests
from tests.helpers import BASE_URL, setup, register_user

############################################
#                                          #
#       Tests for admin_user_remove        #
#                                          #
############################################

def test_admin_user_remove_invalid_u_id(setup):

    user = register_user().json()
    response = requests.delete( f"{BASE_URL}/admin/user/remove/v1", json = {
                                'token': user['token'], 'u_id': user['auth_user_id'] + 1})
    assert response.status_code == 400

def test_admin_user_remove_only_global_owner(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    register_user(email = 'user2@mail.com').json()

    response = requests.delete( f"{BASE_URL}/admin/user/remove/v1", json = {
                                'token': user1['token'], 'u_id': user1['auth_user_id']})
    assert response.status_code == 400

def test_admin_user_remove_unauthorised(setup):

    register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    # user2 is not a global owner
    response = requests.delete( f"{BASE_URL}/admin/user/remove/v1", json = {
                                'token': user2['token'], 'u_id': user2['auth_user_id']})
    assert response.status_code == 403

def test_admin_user_remove_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()

    response = requests.delete( f"{BASE_URL}/admin/user/remove/v1", json = {
                                'token': user1['token'], 'u_id': user2['auth_user_id']})
    assert response.status_code == 200
    # user2 no longer exists
    response = requests.delete( f"{BASE_URL}/admin/user/remove/v1", json = {
                                'token': user1['token'], 'u_id': user2['auth_user_id']})
    assert response.status_code == 400

############################################
#                                          #
#  Tests for admin_userpermission_change   #
#                                          #
############################################

def test_admin_userpermission_change_invalid_u_id(setup):

    user = register_user().json()
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user['token'], 'u_id': user['auth_user_id'] + 1,
                            'permission_id': 2})
    assert response.status_code == 400

def test_admin_userpermission_change_only_global_owner(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    register_user(email = 'user2@mail.com').json()

    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user1['token'], 'u_id': user1['auth_user_id'],
                            'permission_id': 2})
    assert response.status_code == 400

def test_admin_userpermission_change_invalid_permission_id(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user1['token'], 'u_id': user2['auth_user_id'],
                            'permission_id': 0})
    assert response.status_code == 400

def test_admin_userpermission_change_unauthorised(setup):

    register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    # user2 is not a global owner
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user2['token'], 'u_id': user2['auth_user_id'],
                            'permission_id': 2})
    assert response.status_code == 403

def test_admin_userpermission_change_valid(setup):

    user1 = register_user(email = 'user1@mail.com').json()
    user2 = register_user(email = 'user2@mail.com').json()
    # Make user2 a global owner
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user1['token'], 'u_id': user2['auth_user_id'],
                            'permission_id': 1})
    assert response.status_code == 200
    # Make user1 a user
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user2['token'], 'u_id': user1['auth_user_id'],
                            'permission_id': 2})
    assert response.status_code == 200
    # Attempt to make user1 a global owner by themself - it will fail
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
                            'token': user1['token'], 'u_id': user1['auth_user_id'],
                            'permission_id': 1})
    assert response.status_code == 403
