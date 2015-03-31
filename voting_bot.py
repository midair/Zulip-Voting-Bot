#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import zulip
import requests
import re
import pprint
import os
from database import VotingTopics


class Bot():

    """bot takes a zulip username and api key, a word or phrase to respond to,
        a search string for giphy, an optional caption or list of captions, and
        a list of the zulip streams it should be active in. It then posts a
        caption and a randomly selected gif in response to zulip messages.
    """

    def __init__(self, zulip_username, zulip_api_key, key_word,
                 subscribed_streams=[]):
        self.username = zulip_username
        self.api_key = zulip_api_key
        self.key_word = key_word.lower()
        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_username, zulip_api_key)
        self.subscriptions = self.subscribe_to_streams()
        self.voting_topics = VotingTopics()

    @property
    def streams(self):
        ''' Standardizes a list of streams in the form [{'name': stream}]
        '''
        if not self.subscribed_streams:
            streams = [{'name': stream['name']}
                       for stream in self.get_all_zulip_streams()]
            return streams
        else:
            streams = [{'name': stream} for stream in self.subscribed_streams]
            return streams

    def get_all_zulip_streams(self):
        ''' Call Zulip API to get a list of all streams
        '''
        response = requests.get('https://api.zulip.com/v1/streams',
                                auth=(self.username, self.api_key))

        if response.status_code == 200:
            return response.json()['streams']

        elif response.status_code == 401:
            raise RuntimeError('check yo auth')

        else:
            raise RuntimeError(':( we failed to GET streams.\n(%s)' % response)

    def subscribe_to_streams(self):
        ''' Subscribes to zulip streams
        '''
        self.client.add_subscriptions(self.streams)

    def respond(self, msg):
        ''' checks msg against key_word. If key_word is in msg, gets a gif url,
            picks a caption, and calls send_message()
        '''

        # decode if necessary
        if type(msg["content"]) == unicode:
            content = msg["content"]
        else:
            content = msg["content"].decode("utf-8", "replace")

        first_word = content.split()[0].lower().strip()

        # check if it's a relevant message fo the bot
        if self.key_word == first_word and msg["sender_email"] != self.username:
            self.parse_public_message(msg, content)

        elif msg["type"] == "private" and msg["sender_email"] != self.username:
            self.parse_private_message(msg, content)

    def send_message(self, msg):
        ''' Sends a message to zulip stream
        '''
        if msg["type"] == "stream":
            msg["to"] = msg['display_recipient']

        elif msg["type"] == "private":
            msg["to"] = msg["sender_email"]

        self.client.send_message(msg)

    def parse_public_message(self, msg, content):
        '''Parse public message given to the bot.

        The resulting actions can be:
            -send_results
            -add_vote
            -send_help
            -post_error
            -new_voting_topic
            -add_voting_option
        '''

        title = self._parse_title(content)

        if title.lower() == "help":
            self.send_help(msg)

        elif title.lower() in self.voting_topics:
            split_msg = content.split("\n")

            if len(split_msg) == 2:
                keyword = split_msg[1]
                regex = re.compile("[0-9]+")

                if keyword.lower().strip() == "results":
                    self.send_results(msg, content)

                elif regex.match(keyword):
                    self.add_vote(title.lower(), unicode(keyword), msg)

                elif "add:" in keyword.lower():
                    new_voting_option = keyword[4:].strip()
                    self.add_voting_option(msg, title,
                                           new_voting_option)

                else:
                    self.send_help(msg)
            else:
                self.send_repeated_voting(msg)
        else:
            self.new_voting_topic(msg, content)

    def _parse_title(self, content):
        title = content.split("\n")[0].split()[1:]
        return " ".join(title)

    def parse_private_message(self, msg, content):
        '''Parse private message given to the bot.

        The resulting actions can be:
            -add_vote
            -send_voting_help
            -post_error
        '''

        msg_content = content.lower()
        title = msg_content.split("\n")[0]

        if title.strip() in self.voting_topics.keys():
            split_msg = msg_content.split("\n")

            if len(split_msg) == 2:
                regex = re.compile("[0-9]+")
                option_number = split_msg[1].split(" ")[0]

                if regex.match(option_number):
                    option_number = int(option_number)
                    self.add_vote(title.lower(), option_number, msg)

                else:
                    print "regex did not match"
                    self.send_voting_help(msg)
            else:
                self.post_error(msg)
        else:
            print "title not in keys" + title
            pprint.pprint(self.voting_topics)
            self.send_voting_help(msg)

    def new_voting_topic(self, msg, content):
        '''Create a new voting topic.'''

        title = content.split("\n")[0].split()[1:]
        title = " ".join(title).strip()

        print "Voting topic", title, "already?:", title.lower() in self.voting_topics
        if title and title.lower() not in self.voting_topics:
            msg["content"] = title
            options = content.split("\n")[1:]
            options_dict = {}

            for x in range(len(options)):
                options_dict[x] = [options[x], 0]
                msg["content"] += "\n " + unicode(x) + ". " + options[x]

            self.voting_topics[title.lower()] = {"title": title,
                                                 "options": options_dict,
                                                 "people_who_have_voted": {}}
            self.send_message(msg)

        else:
            if title.lower() in self.voting_topics.keys():
                self.send_repeated_voting(msg)
            else:
                self.send_help(msg)

    def add_voting_option(self, msg, title, new_voting_option):
        '''Add a new voting option to an existing voting topic.'''

        if title.lower().strip() in self.voting_topics:
            vote = self.voting_topics[title.lower().strip()]
            options = vote["options"]

            if self._not_already_there(options, new_voting_option):
                options_num = options.keys()
                new_option_num = len(options_num)

                options[new_option_num] = [new_voting_option, 0]

                msg["content"] = "There is a new option in topic: " + title
                for x in range(len(options)):
                    msg["content"] += "\n " + unicode(x) + ". " + options[x][0]

                self.send_message(msg)

            else:
                msg["content"] = new_voting_option + \
                    " is already an option in topic: " + title + \
                    "\nDo not attempt to repeat options!"
                self.send_message(msg)

        self.voting_topics[title.lower().strip()] = vote

    def _not_already_there(self, vote_options, new_voting_option):
        options = [opt[0] for opt in vote_options.values()]
        return new_voting_option not in options

    def add_vote(self, title, option_number, msg):
        '''Add a vote to an existing voting topic.'''

        vote = self.voting_topics[title]
        print vote

        if option_number in vote["options"]:

            if msg["sender_email"] not in vote["people_who_have_voted"]:
                self._increment(vote["options"][option_number][1], 1)
                vote["people_who_have_voted"][
                    (msg["sender_email"])] = option_number
                msg["content"] = self._get_add_vote_msg(msg, vote,
                                                        option_number, False)

            else:
                old_vote_option = vote[
                    "people_who_have_voted"][msg["sender_email"]]
                self._increment(vote["options"][old_vote_option][1], -1)
                self._increment(vote["options"][option_number][1], 1)
                vote["people_who_have_voted"][
                    (msg["sender_email"])] = option_number
                msg["content"] = self._get_add_vote_msg(msg, vote,
                                                        option_number, True)
        else:
            msg["content"] = " ".join(["That option is not in the range of the",
                                       "voting options. Here are your options:",
                                       " \n"])
            options_list = []
            for i in xrange(len(vote["options"])):
                new_option = unicode(i) + ". " + vote["options"][unicode(i)][0]
                options_list.append(new_option)

            msg["content"] += "\n".join(options_list)

        self.send_message(msg)

        self.voting_topics[title.strip()] = vote

    def _increment(self, vote_option, num):

        vote_option_num = int(vote_option)
        vote_option_num += 1
        vote_option = unicode(vote_option_num)

    def _get_add_vote_msg(self, msg, vote, option_number, changed_vote):
        '''Creates a different msg if the vote was private or public.'''

        option_desc = vote["options"][option_number][0]

        if changed_vote:
            msg_content = "You have changed your vote. \n"
        else:
            msg_content = ""
        if msg["type"] == "private":
            msg_content += "One vote in this topic: " + vote["title"] + \
                " for this option: " + option_desc
        else:
            msg_content += "You just voted for '" + option_desc + \
                "' but remember! You can also vote privately if you want :)"

        return msg_content

    def send_help(self, msg):
        with open("help_msg.txt") as f:
            msg["content"] = f.read()
        self.send_message(msg)

    def send_repeated_voting(self, msg):
        msg["content"] = "This topic already exists! Choose another name."
        self.send_message(msg)

    def send_voting_help(self, msg):
        with open("voting_help_msg.txt") as f:
            msg["content"] = f.read()
        self.send_message(msg)

    def post_error(self, msg):
        return

    def send_results(self, msg, content):
        '''Publicly send results of voting in the thread that was used.'''

        msg_content = content.lower()
        title = msg_content.split("\n")[0].split()[1:]
        title = " ".join(title).strip()

        if title in self.voting_topics.keys():
            # print title in self.voting_topics.keys(), "tigle in keys"
            vote = self.voting_topics[title]
            results = "The results are in!!!! \nTopic: " + vote["title"]

            for option in vote["options"].values():
                results += "\n{0} has {1} votes.".format(
                    option[0], unicode(option[1]))

            msg["content"] = results
            # print "deleting"
            self.delete_voting_topic(title.lower())
            # print "deleted"
            self.send_message(msg)

        self.voting_topics[title.lower().strip()] = vote

    def delete_voting_topic(self, voting_title):
        print "deleting", voting_title

        dict_params = {self.voting_topics.KEY_FIELD: unicode(voting_title)}

        with self.voting_topics.db as db:
            db[self.voting_topics.TABLE].delete(**dict_params)

        print voting_title, "deleted from voting_bot.py!"

    def main(self):
        ''' Blocking call that runs forever. Calls self.respond() on every
            message received.
        '''
        self.client.call_on_each_message(lambda msg: self.respond(msg))
        # print msg


def main():
    zulip_username = 'voting-bot@students.hackerschool.com'
    zulip_api_key = os.environ['ZULIP_API_KEY']
    key_word = 'VotingBot'

    subscribed_streams = []

    new_bot = Bot(zulip_username, zulip_api_key, key_word, subscribed_streams)
    new_bot.main()

if __name__ == '__main__':
    main()
