def user_is_valid(store, u_id):
    if 0 <= u_id < len(store['users']) and store['users'][u_id]['permission_id'] is not None:
        return True
    return False

def channel_is_valid(store, channel_id):
    if 0 <= channel_id < len(store['channels']):
        return True
    return False

def dm_is_valid(store, dm_id):
    if 0 <= dm_id < len(store['dms']):
        return True
    return False

def user_in_channel(store, channel_id, u_id):
    for user in store['channels'][channel_id]['all_members']:
        if user == u_id:
            return True
    return False

def user_in_dm(store, dm_id, u_id):
    for user in store['dms'][dm_id]['members']:
        if user == u_id:
            return True
    return False

def user_is_channel_owner(store, channel_id, u_id):
    if store['users'][u_id]['permission_id'] == 1:
        for user in store['channels'][channel_id]['all_members']:
            if user == u_id:
                return True
        return False
    else:
        for user in store['channels'][channel_id]['owner_members']:
            if user == u_id:
                return True
        return False


