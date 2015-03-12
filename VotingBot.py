import zulip
import json
import requests
import random


class bot():
    ''' bot takes a zulip username and api key, a word or phrase to respond to, a search string for giphy,
        an optional caption or list of captions, and a list of the zulip streams it should be active in.
        it then posts a caption and a randomly selected gif in response to zulip messages.
     '''
    def __init__(self, zulip_username, zulip_api_key, key_word, subscribed_streams=[]):
        self.username = zulip_username
        self.api_key = zulip_api_key
        self.key_word = key_word.lower()
        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_username, zulip_api_key)
        self.subscriptions = self.subscribe_to_streams()
        self.voting_topics = {}


    @property
    def streams(self):
        ''' Standardizes a list of streams in the form [{'name': stream}]
        '''
        if not self.subscribed_streams:
            streams = [{'name': stream['name']} for stream in self.get_all_zulip_streams()]
            return streams
        else:
            streams = [{'name': stream} for stream in self.subscribed_streams]
            return streams


    def get_all_zulip_streams(self):
        ''' Call Zulip API to get a list of all streams
        '''
        response = requests.get('https://api.zulip.com/v1/streams', auth=(self.username, self.api_key))
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
        content = msg['content'].lower()
        if self.key_word in content:
            self.parse_public_message(msg)
        elif msg["type"] == "private":
            self.parse_private_message(msg)
               

    def send_message(self, msg):
        ''' Sends a message to zulip stream
        '''
        if msg["type"] == "stream":
            msg["to"] = msg['display_recipient']
        elif msg["type"] == "private":
            msg["to"] = msg["sender_email"]

        self.client.send_message(msg)

    def parse_public_message(self, msg):
        msg_content = msg["content"].lower()
        title = msg_content.split("\n")[0].split()[1:]
        title = " ".join(title)
        if title in self.voting_topics.keys():
            split_msg = msg_content.split("\n")
            if len(split_msg) == 2:
                keyword = split_msg[1]
                regex = re.compile("[0-9]")
                if keyword == "results":
                   self.send_results(msg)
                elif regex.match(keyword):
                    self.add_vote(title.lower(),msg)
                else:
                    self.send_help(msg)
            else:
                self.post_error(msg)
        else:
            self.new_voting_topic(msg)

    def parse_private_message(self, msg):
        msg_content = msg["content"].lower()
        title = msg_content.split("\n")
        if title in self.voting_topics.keys():
            split_msg = msg_content.split("\n")
            if len(split_msg) == 2:
                regex = re.compile("[0-9]+")
                optionNumber = split_msg[1].split(" ")[0]
                if regex.match(optionNumber):
                    optionNumber = int(optionNumber)
                    self.add_vote(title.lower(), optionNumber,msg)
                else:
                    self.send_voting_help(msg)
            else:
                self.post_error(msg)
        else:
            self.send_voting_help(msg)


    def new_voting_topic(self, msg):
        msg_content = msg["content"]
        title = msg_content.split("\n")[0].split()[1:]
        title = " ".join(title)
        if title:
            msg["content"] = title
            options = msg_content.split("\n")[1:]
            options_dict = {}
            for x in range(len(options)):
                options_dict[x] = [options[x], 0]
                msg["content"] += "\n " +x +". " + options[x]

            self.voting_topics = {title.lower():{"title":title, "options":options_dict, "msg":msg, "people_who_have_voted": []}}

            self.send_message(msg)
        else:
            self.send_help(msg)

    def add_vote(self, title, optionNumber, msg):
        vote = self.voting_topics[title]
        vote["options"][optionNumber][1] += 1
        msg["content"] = "One vote in this topic: " + vote["title"] + " for this option: " + vote["options"][optionNumber][0]
        self.send_message(msg)

    def send_help(self, msg):
        msg["content"] = '''You look like you need some VotingBot tips!'''
        self.send_message(msg)

    def send_voting_help(self, msg):
        msg["content"] = '''You look like you need some VotingBot tips on how to vote!'''
        self.send_message(msg)


    def post_error(self, msg):
        return


    def main(self):
        ''' Blocking call that runs forever. Calls self.respond() on every message received.
        '''
        self.client.call_on_each_message(lambda msg: self.respond(msg))



''' The Customization Part!
    
    Create a zulip bot under "settings" on zulip.
    Zulip will give you a username and API key
    key_word is the text in Zulip you would like the bot to respond to. This may be a 
        single word or a phrase.
    search_string is what you want the bot to search giphy for.
    caption may be one of: [] OR 'a single string' OR ['or a list', 'of strings']
    subscribed_streams is a list of the streams the bot should be active on. An empty 
        list defaults to ALL zulip streams

'''

zulip_username = 'zulip_newbie_bot-bot@students.hackerschool.com'
zulip_api_key = 'w9r2FyGMYrWaueeoooLC8qEmarIZvNT2'
key_word = 'VotingBot'

subscribed_streams = [] 

new_bot = bot(zulip_username, zulip_api_key, key_word, subscribed_streams)
new_bot.main()
