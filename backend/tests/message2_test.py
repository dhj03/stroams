import pytest
from datetime import timezone, datetime
from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_invite_v1, channel_details_v1, channel_messages_v1, channel_join_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1
from src.dm import dm_create_v1, dm_messages_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.admin import admin_userpermission_change_v1

long_string =  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

# Fixture: Registers and returns a user id
@pytest.fixture(name='return_list')
def fixture_user_id():
    clear_v1()
    auth_register_v1('hayden@unsw.edu.au', 'password', 'hayden', 'smith')
    # Getting user id
    login_return = auth_login_v1('hayden@unsw.edu.au', 'password')
    user_id1 = login_return['auth_user_id']
    return user_id1


############################################
#                                          #
#      Tests for message_send_v1           #
#                                          #
############################################


# Test for invalid channel_id
def test_message_send_invalid_channel_id(return_list):
    user_id = return_list
    with pytest.raises(InputError):
        message_send_v1(user_id, -1, 'message that they want to send')


# Test for authorised user
def test_message_send_unauthorised_user(return_list):
    user_id1 = return_list
    # Create an exta user
    auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Get their login info
    login_return = auth_login_v1('wendypendy@unsw.edu.au', 'wendypassword')
    # Return user_id
    user_id2 = login_return['auth_user_id']
    # Wendy makes a channel that Hayden is not a part of
    channel = channels_create_v1(user_id2, 'Super Channel', False)

    #Hayden tries to send a message through to Super Channel

    with pytest.raises(AccessError):
        message_send_v1(user_id1, channel['channel_id'], 'message that they want to send')


# Test for message length
def test_message_send_long_message(return_list):
    user_id = return_list
    with pytest.raises(InputError):
        message_send_v1(user_id, 1, long_string)


# Make sure the message_id's are unique
def test_message_send_message_id(return_list):
    user_id = return_list
    # Create a channel
    channel = channels_create_v1(user_id, 'Fun Channel', False)
    # Send two valid messages
    message_id1 = message_send_v1(user_id, channel['channel_id'], 'Good luck have fun!')['message_id']
    message_id2 = message_send_v1(user_id, channel['channel_id'], 'Normal summon Aleister')['message_id']

    assert message_id1 != message_id2

# Test for time_created
def test_message_send_time(return_list):
    user_id = return_list
    # Create a channel
    channel = channels_create_v1(user_id, 'Fun Channel', False)
    # Send a valid message
    message_send_v1(user_id, channel['channel_id'], 'I love COMP1531')
    # Get the time
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    # Pull the message details
    message = channel_messages_v1(user_id, channel['channel_id'], 0)

    assert time == message['messages'][0]['time_created']

# Test for message_id across different channels
def test_message_send_across_channels(return_list):
    user_id = return_list
    # Create channels
    channel1 = channels_create_v1(user_id, 'First Channel', False)
    channel2 = channels_create_v1(user_id, 'Second Channel', False)
    # Message on both channels
    message_id1 = message_send_v1(user_id, channel1['channel_id'], 'Message on First Channel')['message_id']
    message_id2 = message_send_v1(user_id, channel2['channel_id'], 'Message on Second Channel')['message_id']

    assert message_id1 != message_id2

############################################
#                                          #
#      Tests for message_edit_v1           #
#                                          #
############################################

# Test for message length
def test_message_edit_long_message(return_list):
    user_id = return_list
    channel_id = channels_create_v1(user_id, 'Super Channel', False)
    message_id = message_send_v1(user_id, channel_id['channel_id'], 'Wow cool channel')['message_id']
    with pytest.raises(InputError):
        message_edit_v1(user_id, message_id, long_string)


# Test for invalid message id
def test_message_edit_invalid_message_id(return_list):
    user_id = return_list
    with pytest.raises(InputError):
        message_edit_v1(user_id, -1, 'message that they want to send')


# Test for non-admin non-author user editing message
def test_message_edit_unauthorised_notauthor(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Return user_id
    user_id2 = login_return['auth_user_id']

    # Wendy makes a channel
    channel_id = channels_create_v1(user_id2, 'Super Channel', False)
    # Wendy makes a message
    message_id1 = message_send_v1(user_id2, channel_id['channel_id'], 'I hope Hayden doesnt change this message again')['message_id']

    # Hayden tries to change Wendy's message even when he's not in the channel
    with pytest.raises(AccessError):
        message_edit_v1(user_id1, message_id1, 'Hehe, changing her message')

# Test for if authorised person changes a message that isn theres
def test_message_edit_authorised_non_author(return_list):
    # Hayden's info
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Wendy makes a channel
    channel_id = channels_create_v1(user_id2, 'Super Channel', False)
    # Wendy invites Hayden to the channel
    channel_invite_v1(user_id2, channel_id['channel_id'], user_id1)
    # Hayden makes a message
    message_id = message_send_v1(user_id1, channel_id['channel_id'], 'I hope Wendy doesn change this message')['message_id']
    # Wendy changes the message
    message_edit_v1(user_id2, message_id, 'Hehe I am changing his message')
    # Pull information about the message
    message = channel_messages_v1(user_id1, channel_id['channel_id'], 0)

    assert message['messages'][0]['message'] == 'Hehe I am changing his message'

# Test for if user is not owner member but did send that message
def test_message_edit_author(return_list):
    # Hayden's info
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Wendy makes a channel
    channel_id = channels_create_v1(user_id2, 'Super Channel', False)
    # Wendy invites Hayden to the channel
    channel_invite_v1(user_id2, channel_id['channel_id'], user_id1)
    # Hayden makes a message
    message_id = message_send_v1(user_id1, channel_id['channel_id'], 'I hope Wendy doesn change this message')['message_id']
    # Hayden changes the message
    message_edit_v1(user_id1, message_id, 'Hehe I am changing my message')
    # Pull information about the message
    message = channel_messages_v1(user_id1, channel_id['channel_id'], 0)

    assert message['messages'][0]['message'] == 'Hehe I am changing my message'


# Test for if it actually edits message
def test_message_edit_returning_correctly(return_list):
    user_id = return_list

    # Hayden makes a channel
    channel_id = channels_create_v1(user_id, 'Super Channel', False)
    # Hayden sends a message through the channel
    message_id = message_send_v1(user_id, channel_id['channel_id'], 'Looking to edit this message')['message_id']
    # Hayden attemps to edit the message
    message_edit_v1(user_id, message_id, 'This is the edited message')
    # Pull information about the message
    message = channel_messages_v1(user_id, channel_id['channel_id'], 0)

    assert message['messages'][0]['message'] == 'This is the edited message'

# Test for making two messages and editing both
def test_message_edit_make_two_edit_both(return_list):
    user_id = return_list

    # Hayden makes a channel
    channel_id = channels_create_v1(user_id, 'Super Channel', False)
    # Hayden sends two messages through the channel
    message_id1 = message_send_v1(user_id, channel_id['channel_id'], 'This is my first message')['message_id']
    message_id2 = message_send_v1(user_id, channel_id['channel_id'], 'This is my second message')['message_id']
    # Edit both messages
    message_edit_v1(user_id, message_id1, 'I edited the first message')
    message_edit_v1(user_id, message_id2, 'I edited the second message')
    # Pull information on the messages
    messages = channel_messages_v1(user_id, channel_id['channel_id'], 0)

    assert messages['messages'][1]['message'] == 'I edited the first message'
    assert messages['messages'][0]['message'] == 'I edited the second message'

# Test for if message_edit works in dm's
def test_message_edit_working_dm(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Create a dm with Wendy and Hayden
    dm_return = dm_create_v1(user_id1, [user_id2])
    # Wendy sends a message in the dm's
    message_id = message_senddm_v1(user_id2, dm_return['dm_id'], 'I am going to edit this message')
    # Wendy edits her own message
    message_edit_v1(user_id1, message_id['message_id'], 'I have edited the message')
    # Pull the messages
    messages = dm_messages_v1(user_id1, dm_return['dm_id'], 0)

    assert messages['messages'][0]['message'] == 'I have edited the message'

############################################
#                                          #
#      Tests for message_remove_v1         #
#                                          #
############################################

# Test for invalid message id
def test_message_remove_invalid_message_id(return_list):
    user_id = return_list
    with pytest.raises(InputError):
        message_remove_v1(user_id, -1)

# Test for non-admin non-author user removing message
def test_message_remove_unauthorised_notauthor(return_list):
    # Hayden's info
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Return user_id
    user_id2 = login_return['auth_user_id']

    # Hayden makes a channel
    channel_id = channels_create_v1(user_id1, 'Super Channel', False)
    # Hayden invites Wendy to the channel
    channel_invite_v1(user_id1, channel_id['channel_id'], user_id2)
    # Hayden makes a message
    message_id1 = message_send_v1(user_id1, channel_id['channel_id'], 'I hope Hayden doesnt change this message again')['message_id']

    # Wendy tries to remove Hayden's message
    with pytest.raises(AccessError):
        message_remove_v1(user_id2, message_id1)

# Test for if authorised person removes a message
def test_message_remove_authorised_non_author(return_list):
    # Hayden's info
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Wendy makes a channel
    channel_id = channels_create_v1(user_id2, 'Super Channel', False)
    # Wendy invites Hayden to the channel
    channel_invite_v1(user_id2, channel_id['channel_id'], user_id1)
    # Hayden makes a message
    message_id = message_send_v1(user_id1, channel_id['channel_id'], 'I hope Wendy doesn change this message')['message_id']
    # Wendy removes the message
    message_remove_v1(user_id2, message_id)
    # Pull information about the message
    message = channel_messages_v1(user_id1, channel_id['channel_id'], 0)

    assert message['messages'] == []

# Test for if user is not owner member but did send that message
def test_message_remove_author_of_message(return_list):
    # Hayden's info
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Wendy makes a channel
    channel_id = channels_create_v1(user_id2, 'Super Channel', False)
    # Wendy invites Hayden to the channel
    channel_invite_v1(user_id2, channel_id['channel_id'], user_id1)
    # Hayden makes a message
    message_id = message_send_v1(user_id1, channel_id['channel_id'], 'I hope Wendy doesn change this message')['message_id']
    # Hayden removes the message
    message_remove_v1(user_id1, message_id)
    # Pull information about the message
    message = channel_messages_v1(user_id1, channel_id['channel_id'], 0)

    assert message['messages'] == []

# Test for if global owner can remove message
def test_message_remove_global_owner(return_list):
    # Hayden's info
    user_id1 = return_list
    
    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Wendy makes a channel
    channel_id = channels_create_v1(user_id2, 'Super Channel', False)
    # Wendy invites Wendy to the channel
    channel_invite_v1(user_id2, channel_id['channel_id'], user_id1)
    # Wendy sends a message on that channel
    message_id = message_send_v1(user_id2, channel_id['channel_id'], 'Hayden is going to remove this message')
    # Hayden removes the message as a global owner
    message_remove_v1(user_id1, message_id['message_id'])
    # Pull information about the message
    messages = channel_messages_v1(user_id1, channel_id['channel_id'], 0)

    assert messages['messages'] == []

# Test for if it actually removes message
def test_message_remove_returning_correctly(return_list):
    user_id = return_list

    # Hayden makes a channel
    channel_id = channels_create_v1(user_id, 'Super Channel', False)
    # Hayden sends a message through the channel
    message_id = message_send_v1(user_id, channel_id['channel_id'], 'Looking to remove this message')['message_id']
    # Hayden attemps to remove the message
    message_remove_v1(user_id, message_id)
    # Pull information about the message
    message = channel_messages_v1(user_id, channel_id['channel_id'], 0)

    assert message['messages'] == []

# Test if message_remove works in dm's
def test_message_remove_working_dm(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Create a dm with Wendy and Hayden
    dm_return = dm_create_v1(user_id1, [user_id2])
    # Wendy sends a message in the dm's
    message_id = message_senddm_v1(user_id2, dm_return['dm_id'], 'I am going to edit this message')
    # Wendy removes her own message
    message_remove_v1(user_id1, message_id['message_id'])
    # Pull the messages
    messages = dm_messages_v1(user_id1, dm_return['dm_id'], 0)

    assert messages['messages'] == []

############################################
#                                          #
#      Tests for message_senddm_v1         #
#                                          #
############################################

# Test for invalid dm_id
def test_message_senddm_invalid_dm_id(return_list):
    user_id = return_list
    with pytest.raises(InputError):
        message_senddm_v1(user_id, -1, 'I want to send you a dm')

# Test for invalid member trying to send dm
def test_message_senddm_invalid_member(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']
    # Create an extra user Yubikiri
    login_return = auth_register_v1('yubikiri@unsw.edu.au', 'yubikiripassword', 'Yubikiri', 'Azaelia')
    # Yubikiri's info
    user_id3 = login_return['auth_user_id']

    # Create a dm between Wendy and Yubikiri
    dm_return = dm_create_v1(user_id2, [user_id3])

    # Hayden attempts to send a message to that dm
    with pytest.raises(AccessError):
        message_senddm_v1(user_id1, dm_return['dm_id'], 'I want to send you a dm')

# Test for message length
def test_message_senddm_long_message(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Create a dm between Wendy and Hayden
    dm_return = dm_create_v1(user_id2, [user_id1])

    with pytest.raises(InputError):
        message_send_v1(user_id1, dm_return['dm_id'], long_string)

# Make sure the message_id's are unique
def test_message_senddm_message_id(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Create a dm between Wendy and Hayden
    dm_return = dm_create_v1(user_id2, [user_id1])
    # Send two valid messages
    message_id1 = message_senddm_v1(user_id1, dm_return['dm_id'], 'Good luck have fun!')['message_id']
    message_id2 = message_senddm_v1(user_id1, dm_return['dm_id'], 'Normal summon Aleister')['message_id']

    assert message_id1 != message_id2


# Test for time_created
def test_message_senddm_time(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']

    # Create a dm between Wendy and Hayden
    dm_return = dm_create_v1(user_id2, [user_id1])
    # Send a valid message
    message_senddm_v1(user_id1, dm_return['dm_id'], 'This is a message between Wendy and Hayden')
    # Get the time
    dt = datetime.now(timezone.utc)
    time = dt.timestamp()
    time = int(time)
    # Pull the message details
    messages = dm_messages_v1(user_id1, dm_return['dm_id'], 0)

    assert time == messages['messages'][0]['time_created']

# Test for message_id across different channels
def test_message_senddm_across_dms(return_list):
    user_id1 = return_list

    # Create an exta user Wendy
    login_return = auth_register_v1('wendypendy@unsw.edu.au', 'wendypassword', 'wendy', 'pendy')
    # Wendy's info
    user_id2 = login_return['auth_user_id']
    # Create an extra user Yubikiri
    login_return = auth_register_v1('yubikiri@unsw.edu.au', 'yubikiripassword', 'Yubikiri', 'Azaelia')
    # Yubikiri's info
    user_id3 = login_return['auth_user_id']

    # Create dms between Wendy and Yubikiri, Wendy and Hayden
    dm_return1 = dm_create_v1(user_id2, [user_id3])
    dm_return2 = dm_create_v1(user_id2, [user_id1])

    # Wendy messages to Yubikiri and Hayden
    message_id1 = message_senddm_v1(user_id2, dm_return1['dm_id'], 'This is a message between Wendy and Yubikiri')['message_id']
    message_id2 = message_senddm_v1(user_id2, dm_return2['dm_id'], 'This is a message between Wendy and Hayden')['message_id']

    assert message_id1 != message_id2
