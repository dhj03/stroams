# Streams

## Introduction

Streams is a messaging platform application, similar to Messenger. It allows users to send DMs, create channels, invite other users to them, and post messages in them.

## Running the Program

This program contains a frontend and a backend, which must be run separately. For information on each of them, navigate to the `README.md` files in each respective folder.

## Authentication

Authentication is used to allow each user to control their messaging individually and independently from other users. Using all features of this application requires a user to be logged in. Each user has an email, password, first and last name, and handle. A user only requires the first two to sign in, and will appear as their handle on their messages.

## DMs and Channels

DMs and channels provide an interface on which users are able to communicate with each other.

DMs only exist between two users, and there is no concept of authority in one. A channel can have any number of members, of which at least one is an owner. By default, the creator of a channel is an owner, and owners can promote members to becoming owners as well. DMs and channels can each contain any number of messages, sent by its users.

## Messages

Messages contain text, and reactions. They may be reacted to, pinned, edited, or deleted. Only the sender of a message or an owner of the channel in which the message was sent may pin, edit, or delete the message. A user may also choose to send a message in a given number of seconds, rather than immediately.

## Standups

A user may also choose to begin a standup in a channel for a given number of seconds, during which any messages sent in the channel are buffered until the time has elapsed, at which point all messages will be sent under the initiator of the standup's name, in a single message.
