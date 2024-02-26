# Stroams Backend

### Running the server

To run the server you should always use the command from the root directory of the project:

```bash
python3 -m src.server
```

This will start the server on the port in the src/config.py file. All tests should import the port number from this file.

If you get an OSError stating that the address is already in use, you can change the port in the config file to any number from 1024 to 49151. Is it likely that another application may be using the original port number.

If you get any errors relating to `flask_cors`, ensure you have installed all the necessary Python libraries.

## Interface specifications

### 1. Input/Output types

<table>
  <tr>
    <th>Variable name</th>
    <th>Type</th>
  </tr>
  <tr>
    <td>named exactly <b>email</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>has suffix <b>id</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>named exactly <b>length</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>contains substring <b>password</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>named exactly <b>message</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>contains substring <b>name</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>has prefix <b>is_</b></td>
    <td>boolean</td>
  </tr>
  <tr>
    <td>has prefix <b>time_</b></td>
    <td>integer (unix timestamp), [check this out](https://www.tutorialspoint.com/How-to-convert-Python-date-to-Unix-timestamp)</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>channels</b></td>
    <td>List of dictionaries, where each dictionary contains types { channel_id, name }</td>
  </tr>
  <tr>
    <td>has suffix <b>_str</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>(outputs only) name ends in <b>members</b></td>
    <td>List of dictionaries, where each dictionary contains types of <b>user</b></td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>users</b></td>
    <td>List of dictionaries, where each dictionary contains types of <b>user</b></td>
  </tr>
  <tr>
    <td>named exactly <b>token</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>dms</b></td>
    <td>List of dictionaries, where each dictionary contains types { dm_id, name }</td>
  </tr>
  <tr>
    <td>named exactly <b>u_ids</b></td>
    <td>List of user ids</td>
  </tr>
  <tr>
    <td>contains substring <b>code</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>has prefix <b>num_</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>has suffix <b>_rate</b></td>
    <td>float between 0 and 1 inclusive</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>user_stats</b></td>
    <td> Dictionary of shape {<br />
    &emsp;channels_joined: [{num_channels_joined, time_stamp}],<br/>
    &emsp;dms_joined: [{num_dms_joined, time_stamp}], <br />
    &emsp;messages_sent: [{num_messages_sent, time_stamp}], <br />
    &emsp;involvement_rate <br />
    }
    </td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>workspace_stats</b></td>
    <td> Dictionary of shape {<br />
    &emsp;channels_exist: [{num_channels_exist, time_stamp}], <br />
    &emsp;dms_exist: [{num_dms_exist, time_stamp}], <br />
    &emsp;messages_exist: [{num_messages_exist, time_stamp}], <br />
    &emsp;utilization_rate <br />
    }
    </td>
  </tr>
  <tr>
    <td>has suffix <b>end</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>has suffix <b>start</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>has suffix <b>_url</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>(outputs only) name ends in <b>reacts</b></td>
    <td>List of dictionaries, where each dictionary contains types { react_id, u_ids, is_this_user_reacted } where react_id is the id of a react, and u_ids is a list of user id's of people who've reacted for that react. is_this_user_reacted is whether or not the authorised user has been one of the reacts to this post</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>notifications</b></td>
    <td>List of dictionaries, where each dictionary contains types { channel_id, dm_id, notification_message } where channel_id is the id of the channel that the event happened in, and is <code>-1</code> if it is being sent to a DM. dm_id is the DM that the event happened in, and is <code>-1</code> if it is being sent to a channel. Notification_message is a string of the following format for each trigger action:
      <ul>
        <li>tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"</li>
        <li>reacted message: "{User’s handle} reacted to your message in {channel/DM name}"</li>
        <li>added to a channel/DM: "{User’s handle} added you to {channel/DM name}"</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>user</b></td>
    <td>Dictionary containing u_id, email, name_first, name_last, handle_str, profile_img_url</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>messages</b></td>
    <td>List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_created, reacts, is_pinned  }</td>
  </tr>
</table>

### 2. Interface


<table>
  <tr>
    <th>Name & Description</th>
    <th>HTTP Method</th>
    <th style="width:18%">Data Types</th>
    <th style="width:32%">Exceptions</th>
  </tr>
  <tr>
    <td><code>auth/login/v2</code><br /><br />Given a registered user's email and password, returns their `token` value.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ email, password }</code><br /><br /><b>Return Type:</b><br /><code>{ token, auth_user_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>email entered does not belong to a user</li>
        <li>password is not correct</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>auth/register/v2</code><br /><br />Given a user's first and last name, email address, and password, create a new account for them and return a new `token`.<br /><br />A handle is generated that is the concatenation of their casted-to-lowercase alphanumeric (a-z0-9) first name and last name (i.e. make lowercase then remove non-alphanumeric characters). If the concatenation is longer than 20 characters, it is cut off at 20 characters. Once you've concatenated it, if the handle is once again taken, append the concatenated names with the smallest number (starting from 0) that forms a new handle that isn't already taken. The addition of this final number may result in the handle exceeding the 20 character limit (the handle 'abcdefghijklmnopqrst0' is allowed if the handle 'abcdefghijklmnopqrst' is already taken).</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ email, password, name_first, name_last }</code><br /><br /><b>Return Type:</b><br /><code>{ token, auth_user_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>email entered is not a valid email (more in section 6.4)</li>
        <li>email address is already being used by another user</li>
        <li>length of password is less than 6 characters</li>
        <li>length of name_first is not between 1 and 50 characters inclusive</li>
        <li>length of name_last is not between 1 and 50 characters inclusive</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>auth/logout/v1</code><br /><br />Given an active token, invalidates the token to log the user out.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>channels/create/v2</code><br /><br />Creates a new channel with the given name that is either a public or private channel. The user who created it automatically joins the channel.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, name, is_public }</code><br /><br /><b>Return Type:</b><br /><code>{ channel_id }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>length of name is less than 1 or more than 20 characters</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channels/list/v2</code><br /><br />Provide a list of all channels (and their associated details) that the authorised user is part of.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ channels }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>channels/listall/v2</code><br /><br />Provide a list of all channels, including private channels, (and their associated details)</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ channels }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>channel/details/v2</code><br /><br />Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id }</code><br /><br /><b>Return Type:</b><br /><code>{ name, is_public, owner_members, all_members }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel/join/v2</code><br /><br />Given a channel_id of a channel that the authorised user can join, adds them to that channel.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>the authorised user is already a member of the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel/invite/v2</code><br /><br />Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to the channel immediately. In both public and private channels, all members are able to invite users.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>u_id does not refer to a valid user</li>
        <li>u_id refers to a user who is already a member of the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel/messages/v2</code><br /><br />Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50". Message with index 0 is the most recent message in the channel. This function returns a new index "end" which is the value of "start + 50", or, if this function has returned the least recent messages in the channel, returns -1 in "end" to indicate there are no more messages to load after this return.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, start }</code><br /><br /><b>Return Type:</b><br /><code>{ messages, start, end }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>start is greater than the total number of messages in the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel/leave/v1</code><br /><br />Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the channel. Their messages should remain in the channel. If the only channel owner leaves, the channel will remain.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel/addowner/v1</code><br /><br />Make user with user id u_id an owner of the channel.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code>
    </td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>u_id does not refer to a valid user</li>
        <li>u_id refers to a user who is not a member of the channel</li>
        <li>u_id refers to a user who is already an owner of the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user does not have owner permissions in the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel/removeowner/v1</code><br /><br />Remove user with user id u_id as an owner of the channel.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>u_id does not refer to a valid user</li>
        <li>u_id refers to a user who is not an owner of the channel</li>
        <li>u_id refers to a user who is currently the only owner of the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user does not have owner permissions in the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/send/v1</code><br /><br />Send a message from the authorised user to the channel specified by channel_id. Note: Each message should have its own unique ID, i.e. no messages should share an ID with another message, even if that other message is in a different channel.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, message }</code><br /><br /><b>Return Type:</b><br /><code>{ message_id }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>length of message is less than 1 or over 1000 characters</li>
      </ul>
        <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/edit/v1</code><br /><br />Given a message, update its text with new text. If the new message is an empty string, the message is deleted.</td>
    <td style="font-weight: bold; color: brown;">PUT</td>
    <td><b>Parameters:</b><br /><code>{ token, message_id, message }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>length of message is over 1000 characters</li>
        <li>message_id does not refer to a valid message within a channel/DM that the authorised user has joined</li>
      </ul>
      <b>AccessError</b> when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      <ul>
        <li>the message was sent by the authorised user making this request</li>
        <li>the authorised user has owner permissions in the channel/DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/remove/v1</code><br /><br />Given a message_id for a message, this message is removed from the channel/DM</td>
    <td style="color: red; font-weight: bold;">DELETE</td>
    <td><b>Parameters:</b><br /><code>{ token, message_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>message_id does not refer to a valid message within a channel/DM that the authorised user has joined</li>
      </ul>
      <b>AccessError</b> when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      <ul>
        <li>the message was sent by the authorised user making this request</li>
        <li>the authorised user has owner permissions in the channel/DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>dm/create/v1</code><br /><br /><code>u_ids</code> contains the user(s) that this DM is directed to, and will not include the creator. The creator is the owner of the DM. <code>name</code> should be automatically generated based on the users that are in this DM. The name should be an alphabetically-sorted, comma-and-space-separated list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, u_ids }</code><br /><br /><b>Return Type:</b><br /><code>{ dm_id }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>any u_id in u_ids does not refer to a valid user</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>dm/list/v1</code><br /><br />Returns the list of DMs that the user is a member of.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ dms }</code></td>
    <td> N/A </td>
  </tr>
  <tr>
    <td><code>dm/remove/v1</code><br /><br />Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.</td>
    <td style="color: red; font-weight: bold;">DELETE</td>
    <td><b>Parameters:</b><br /><code>{ token, dm_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>dm_id does not refer to a valid DM</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>dm_id is valid and the authorised user is not the original DM creator</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>dm/details/v1</code><br /><br />Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, dm_id }</code><br /><br /><b>Return Type:</b><br /><code>{ name, members }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>dm_id does not refer to a valid DM</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>dm_id is valid and the authorised user is not a member of the DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>dm/leave/v1</code><br /><br />Given a DM ID, the user is removed as a member of this DM. The creator is allowed to leave and the DM will still exist if this happens. This does not update the name of the DM.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, dm_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>dm_id does not refer to a valid DM</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>dm_id is valid and the authorised user is not a member of the DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>dm/messages/v1</code><br /><br />Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50". Message with index 0 is the most recent message in the DM. This function returns a new index "end" which is the value of "start + 50", or, if this function has returned the least recent messages in the DM, returns -1 in "end" to indicate there are no more messages to load after this return.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, dm_id, start }</code><br /><br /><b>Return Type:</b><br /><code>{ messages, start, end }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>dm_id does not refer to a valid DM</li>
        <li>start is greater than the total number of messages in the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>dm_id is valid and the authorised user is not a member of the DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/senddm/v1</code><br /><br />Send a message from authorised_user to the DM specified by dm_id. Note: Each message should have it's own unique ID, i.e. no messages should share an ID with another message, even if that other message is in a different channel or DM.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, dm_id, message }</code><br /><br /><b>Return Type:</b><br /><code>{ message_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>dm_id does not refer to a valid DM</li>
        <li>length of message is less than 1 or over 1000 characters</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>dm_id is valid and the authorised user is not a member of the DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>users/all/v1</code><br /><br />Returns a list of all users and their associated details.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ users }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>user/profile/v1</code><br /><br />For a valid user, returns information about their user_id, email, first name, last name, and handle</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{ user }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>u_id does not refer to a valid user</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>user/profile/setname/v1</code><br /><br />Update the authorised user's first and last name</td>
    <td style="font-weight: bold; color: brown;">PUT</td>
    <td><b>Parameters:</b><br /><code>{ token, name_first, name_last }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>length of name_first is not between 1 and 50 characters inclusive</li>
        <li>length of name_last is not between 1 and 50 characters inclusive</li>
      </ul>
  </tr>
  <tr>
    <td><code>user/profile/setemail/v1</code><br /><br />Update the authorised user's email address</td>
    <td style="font-weight: bold; color: brown;">PUT</td>
    <td><b>Parameters:</b><br /><code>{ token, email }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>email entered is not a valid email (more in section 6.4)</li>
        <li>email address is already being used by another user</li>
      </ul>
  </tr>
  <tr>
    <td><code>user/profile/sethandle/v1</code><br /><br />Update the authorised user's handle (i.e. display name)</td>
    <td style="font-weight: bold; color: brown;">PUT</td>
    <td><b>Parameters:</b><br /><code>{ token, handle_str }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>length of handle_str is not between 3 and 20 characters inclusive</li>
        <li>handle_str contains characters that are not alphanumeric</li>
        <li>the handle is already used by another user</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>admin/user/remove/v1</code><br /><br />Given a user by their u_id, remove them from the Stroams. This means they should be removed from all channels/DMs, and will not be included in the list of users returned by users/all. Stroams owners can remove other Stroams owners (including the original first owner). Once users are removed, the contents of the messages they sent will be replaced by 'Removed user'. Their profile must still be retrievable with user/profile, however name_first should be 'Removed' and name_last should be 'user'. The user's email and handle should be reusable.</td>
    <td style="color: red; font-weight: bold;">DELETE</td>
    <td><b>Parameters:</b><br /><code>{ token, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>u_id does not refer to a valid user</li>
        <li>u_id refers to a user who is the only global owner</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>the authorised user is not a global owner</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>admin/userpermission/change/v1</code><br /><br />Given a user by their user ID, set their permissions to new permissions described by permission_id.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, u_id, permission_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>u_id does not refer to a valid user</li>
        <li>u_id refers to a user who is the only global owner and they are being demoted to a user</li>
        <li>permission_id is invalid</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>the authorised user is not a global owner</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>clear/v1</code><br /><br />Resets the internal data of the application to its initial state</td>
    <td style="color: red; font-weight: bold;">DELETE</td>
    <td><b>Parameters:</b><br /><code>{}</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>notifications/get/v1</code><br /><br />Return the user's most recent 20 notifications, ordered from most recent to least recent.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ notifications }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>search/v1</code><br /><br />Given a query string, return a collection of messages in all of the channels/DMs that the user has joined that contain the query.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, query_str }</code><br /><br /><b>Return Type:</b><br /><code>{ messages }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>length of query_str is less than 1 or over 1000 characters</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/share/v1</code><br /><br /><code>og_message_id</code> is the ID of the original message. <code>channel_id</code> is the channel that the message is being shared to, and is <code>-1</code> if it is being sent to a DM. <code>dm_id</code> is the DM that the message is being shared to, and is <code>-1</code> if it is being sent to a channel. <code>message</code> is the optional message in addition to the shared message, and will be an empty string <code>''</code> if no message is given. A new message should be sent to the channel/DM identified by the channel_id/dm_id that contains the contents of both the original message and the optional message. The format does not matter as long as both the original and optional message exist as a substring within the new message.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, og_message_id, message, channel_id, dm_id }</code><br /><br /><b>Return Type:</b><br /><code>{ shared_message_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>both channel_id and dm_id are invalid</li>
        <li>neither channel_id nor dm_id are -1
        <li>og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined</li>
        <li>length of message is more than 1000 characters</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are trying to share the message to</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/react/v1</code><br /><br />Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, message_id, react_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>message_id is not a valid message within a channel or DM that the authorised user has joined</li>
        <li>react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1</li>
        <li>the message already contains a react with ID react_id from the authorised user</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/unreact/v1</code><br /><br />Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, message_id, react_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>message_id is not a valid message within a channel or DM that the authorised user has joined</li>
        <li>react_id is not a valid react ID</li>
        <li>the message does not contain a react with ID react_id from the authorised user</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/pin/v1</code><br /><br />Given a message within a channel or DM, mark it as "pinned".</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, message_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>message_id is not a valid message within a channel or DM that the authorised user has joined</li>
        <li>the message is already pinned</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/unpin/v1</code><br /><br />Given a message within a channel or DM, remove its mark as pinned.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, message_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>message_id is not a valid message within a channel or DM that the authorised user has joined</li>
        <li>the message is not already pinned</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/sendlater/v1</code><br /><br />Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, message, time_sent }</code><br /><br /><b>Return Type:</b><br /><code>{ message_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>length of message is over 1000 characters</li>
        <li>time_sent is a time in the past</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel they are trying to post to</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>message/sendlaterdm/v1</code><br /><br />Send a message from the authorised user to the DM specified by dm_id automatically at a specified time in the future.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, dm_id, message, time_sent }</code><br /><br /><b>Return Type:</b><br /><code>{ message_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>dm_id does not refer to a valid DM</li>
        <li>length of message is over 1000 characters</li>
        <li>time_sent is a time in the past</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>dm_id is valid and the authorised user is not a member of the DM they are trying to post to</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>standup/start/v1</code><br /><br />For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup/send" with a message, it is buffered during the X second window then at the end of the X second window a message will be added to the message queue in the channel from the user who started the standup. "length" is an integer that denotes the number of seconds that the standup occurs for.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, length }</code><br /><br /><b>Return Type:</b><br /><code>{ time_finish }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>length is a negative integer</li>
        <li>an active standup is currently running in the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>standup/active/v1</code><br /><br />For a given channel, return whether a standup is active in it, and what time the standup finishes. If no standup is active, then time_finish returns <code>None</code>.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id }</code><br /><br /><b>Return Type:</b><br /><code>{ is_active, time_finish }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>standup/send/v1</code><br /><br />Sending a message to get buffered in the standup queue, assuming a standup is currently active. Note: We do not expect @ tags to be parsed as proper tags when sending to standup/send</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, channel_id, message }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>length of message is over 1000 characters</li>
        <li>an active standup is not currently running in the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>auth/passwordreset/request/v1</code><br /><br />Given an email address, if the user is a registered user, sends them an email containing a specific secret code, that when entered in auth/passwordreset/reset, shows that the user trying to reset the password is the one who got sent this email. No error should be raised when passed an invalid email, as that would pose a security/privacy concern. When a user requests a password reset, they should be logged out of all current sessions.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ email }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      N/A
    </td>
  </tr>
  <tr>
    <td><code>auth/passwordreset/reset/v1</code><br /><br />Given a reset code for a user, set that user's new password to the password provided.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ reset_code, new_password }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>reset_code is not a valid reset code</li>
        <li>password entered is less than 6 characters long</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>user/profile/uploadphoto/v1</code><br /><br />Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left. Please note: the URL needs to be a non-https URL (it should just have "http://" in the URL. We will only test with non-https URLs.</td>
    <td style="font-weight: bold; color: blue;">POST</td>
    <td><b>Parameters:</b><br /><code>{ token, img_url, x_start, y_start, x_end, y_end }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>img_url returns an HTTP status other than 200</li>
        <li>any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL</li>
        <li>x_end is less than x_start or y_end is less than y_start</li>
        <li>image uploaded is not a JPG</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>user/stats/v1</code><br /><br />Fetches the required statistics about this user's use of Stroams.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ user_stats }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>users/stats/v1</code><br /><br />Fetches the required statistics about the use of Stroams.</td>
    <td style="font-weight: bold; color: green;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token }</code><br /><br /><b>Return Type:</b><br /><code>{ workspace_stats }</code></td>
    <td>N/A</td>
  </tr>
</table>

### 3. Errors for all functions

Either an `InputError` or `AccessError` is thrown when something goes wrong. All of these cases are listed in the **Interface** table. If input implies that both errors should be thrown, throw an `AccessError`.

One exception is that, even though it's not listed in the table, for all functions except `auth/register`, `auth/login`, `auth/passwordreset/request` and `auth/passwordreset/reset`, an `AccessError` is thrown when the token passed in is invalid.

### 4. Valid email format

A valid email should match the following regular expression:

```
'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
```

The Python `re` (regular expression) module allows you to determine whether a string matches a regular expression. You do not need to understand regular expressions to effectively utilise the `re` module to check if the email is correct. Check [this link](https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/) if you need more help.

### 5. Testing

A common question asked throughout the project is usually "How can I test this?" or "Can I test this?" In any situation, most things can be tested thoroughly. However, some things can only be tested sparsely, and in some other rare occasions, some things can't be tested at all. A challenge of this project is for you to use your discretion to figure out what to test, and how much to test.

### 6. Pagination

The behaviour in which channel_messages returns data is called **pagination**. It's a commonly used method when it comes to getting theoretially unbounded amounts of data from a server to display on a page in chunks. Most of the timelines you know and love - Facebook, Instagram, LinkedIn - do this.

For example, if we imagine a user with `auth_user_id` "12345" is trying to read messages from channel with ID 6, and this channel has 124 messages in it, 3 calls from the client to the server would be made. These calls, and their corresponding return values would be:
 * `channel_messages("12345", 6, 0) => { [messages], 0, 50 }`
 * `channel_messages("12345", 6, 50) => { [messages], 50, 100 }`
 * `channel_messages("12345", 6, 100) => { [messages], 100, -1 }`

Pagination should also apply to messages in DMs.

### 7. Permissions

 * Members in a channel/DM have one of two channel/DM permissions
   1) Owner of the channel/DM
   2) Members of the channel/DM
 * Stroams users have two global permissions
   1) Owners (permission id 1), who can also modify other owners' permissions
   2) Members (permission id 2), who do not have any special permissions
* All Stroams users are members by default, except for the very first user who signs up, who is an owner

A user's primary permissions are their global permissions (except in DMs). Then the channel/DM permissions are layered on top. For example:
* An owner of Stroams has channel owner permissions in every channel they've joined. Despite obtaining owner permissions upon joining a channel, they do not become channel owners unless a channel owner adds them as one, meaning if they are removed as a global owner, they will no longer have those channel owner permissions.
* Stroams owners do not have owner permissions in DMs. The only users with owner permissions in DMs are the original creators of each DM.
* A member of Stroams is a member in channels they are not owners of
* A member of Stroams is an owner in channels they are owners of


### 8. Token

Many of these functions (nearly all of them) need to be called from the perspective of a user who is logged in already. When calling these "authorised" functions, we need to know:
1) Which user is calling it
2) That the person who claims they are that user, is actually that user

We could solve this trivially by storing the user ID of the logged in user on the frontend, and every time the frontend calls your background, they just sent a user ID. This solves our first problem (1), but doesn't solve our second problem! Because someone could just "hack" the frontend and change their user id and then log themselves in as someone else.

To solve this when a user logs in or registers the backend should return a "token" (an authorisation hash) that the frontend will store and pass into most of the functions in future. When these "authorised" functions are called, those tokens returned from register/login will be passed into those functions, and from there you can check if a token or auth_user_id is valid, and determine the user ID.

Passwords must be stored in an encrypted form, and tokens must use JWTs (or similar).

### 9. Working with the frontend

The frontend is located in a separate directory. If you run the frontend at the same time as the flask server is running on the backend, then you can power the frontend via the backend.

For errors to be appropriately raised on the frontend, they must be raised by the following:

```python
if True: # condition here
    raise InputError(description='Description of problem')
```

### 10. User Sessions

When a user logs in or registers, they receive a "token" (think of it like a ticket to a concert) for a session. These tokens are stored on the web browser, and nearly every time that user wants to make a request to the server, they will pass this "token" as part of this request. In this way, the server is able to take this token, look at it (like checking a ticket), and determine whether it's really you or not.

This notion of a session is explored in the authentication (Hashing) & authorisation (JWT).

The application is also able to handle multiple concurrent sessions. I.E. One user can log in on two different browser tabs, click logout on tab 1, but still functionally use the website on tab 2.

### 11. Tagging users

A user is tagged when a message contains the @ symbol, followed immediately by the user’s handle. The end of the handle is signified by the end of the message, or a non-alphanumeric character. If the handle is invalid, or the user is not a member of the channel or DM, no one is tagged.

Tagging should also occur when messages are edited to contain tags and when the message/share optional message contains tags.

### 12. Analytics

Analytics pages for users and for the Stroams workspace on the frontend need data. The backend keeps track of these metrics:

For users:
  * The number of channels the user is a part of
  * The number of DMs the user is a part of
  * The number of messages the user has sent
  * The user's involvement, as defined by this pseudocode: `sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_channels, num_dms, num_msgs)`. If the denominator is 0, involvement should be 0. If the involvement is greater than 1, it should be capped at 1.

For the Stroams workspace:
  * The number of channels that exist currently
  * The number of DMs that exist currently
  * The number of messages that exist currently
  * The workspace's utilization, which is a ratio of the number of users who have joined at least one channel/DM to the current total number of users, as defined by this pseudocode: `num_users_who_have_joined_at_least_one_channel_or_dm / num_users`

As we are very interested in our users' engagement, the analytics must be **time-series data**. This means every change to the above metrics (excluding `involvement_rate` and `utilization_rate`) must be timestamped, rather than just the most recent change. For users, the first data point should be 0 for all metrics at the time that their account was created. Similarly, for the workspace, the first data point should be 0 for all metrics at the time that the first user registers.

For users, the number of channels and DMs that they have joined can increase and decrease over time, however the number of messages sent will only increase (the removal of messages does not affect it).

For the workspace, `num_msgs` is the number of messages that exist at the current time, and should decrease when messages are removed. `num_channels` will never decrease as there is no way to remove channels, and `num_dms` will only decrease when `dm/remove` is called.

In addition to keeping track of these metrics, there are also two other endpoints, `user/stats` and `users/stats`.

### 13. Reacts

The only React ID currently associated with the frontend is React ID 1, which is a thumbs up. You are welcome to add more (this will require some frontend work).

### 14. Standups

Once standups are finished, all of the messages sent to standup/send are packaged together in *one single message* posted by *the user who started the standup* and sent as a message to the channel the standup was started in, timestamped at the moment the standup finished.

The structure of the packaged message is like this:

```txt
[message_sender1_handle]: [message1]
[message_sender2_handle]: [message2]
[message_sender3_handle]: [message3]
[message_sender4_handle]: [message4]
```

For example:

```txt
hayden: I ate a catfish
jake: I went to kmart
emily: I ate a toaster
nick: my catfish ate a kmart toaster
```

Standups can be started on the frontend by typing "/standup X", where X is the number of seconds that the standup lasts for, into the message input and clicking send.

### 15. profile_img_url & image uploads

For outputs with data pertaining to a user, a profile_img_url is present. When images are uploaded for a user profile, after processing them you should store them on the server such that the server now locally has a copy of the cropped image of the original file linked. Then, the profile_img_url should be a URL to the server, such as http://localhost:5001/imgurl/adfnajnerkn23k4234.jpg (a unique url you generate).

For any given user, if they have yet to upload an image, there should be a site-wide default image used.

Note: This is most likely the most challenging part of the project. Don't get lost in this, we would strongly recommend most teams complete this capability *last*.
