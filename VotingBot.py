#!/usr/bin/env python

import zulip
import sys

# Keyword arguments 'email' and 'api_key' are not required if you are
# using ~/.zuliprc
client = zulip.Client(email="othello-bot@example.com",
                      api_key="a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5")

voting_topics = {}


def parseMessage(msg):
    msg_content = msg["content"].lower()
    title = msg_content.split("\n")[0]
    if title in voting_topics.keys():
        split_msg = msg_content.split("\n")
        if len(split_msg) == 2:
            keyword = split_msg[1]
            regex = re.compile("[0-9]")
            if keyword == "results":
                sendResults(msg)
            elif regex.match(keyword):
                addVote(msg)
            else:
                sendHelp(msg)
    else:
        newVotingTopic(msg)


def sendResults(msg):
    client.send_message(
        {
            "type"
        }
    )


def addVote(msg):
    return


def sendHelp(msg):
    return


def newVotingTopic(msg):
    global voting_topics
    title = msg.split(":")[0]
    msg_without_title = ":".join(msg.split(":")[1:])
    options = re.compile("[0-9]\.?\s?").split(msg_without_title)
    options_dict = {}
    for option in options:
        options_dict[option] = 0

    voting_topics = {title: options_dict}


# Send a stream message
client.send_message({
    "type": "stream",
    "to": "Denmark",
    "subject": "Castle",
    "content": "Something is rotten in the state of Denmark."
})
# Send a private message
client.send_message({
    "type": "private",
    "to": "hamlet@example.com",
    "content": "I come not, friends, to steal away your hearts."
})

# Print each message the user receives
# This is a blocking call that will run forever
client.call_on_each_message(lambda msg: parseMessage(msg))
