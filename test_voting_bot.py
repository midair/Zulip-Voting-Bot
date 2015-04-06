#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest
import nose
from voting_bot import VotingBot


class VotingBotTest(unittest.TestCase):

    def setUp(self):
        self.vb = VotingBot

    def tearDown(self):
        del self.vb

    def test_parse_public_message(self):

        # voting topic
        content = "votingbot new poll\none\ntwo\nthree"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title = "topic", "new poll"
        e_arg = ["one", "two", "three"]
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll: one, two, three"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title = "topic", "new poll"
        e_arg = ["one", "two", "three"]
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll one, two, three"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title = "topic", "new poll"
        e_arg = ["one", "two", "three"]
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll one"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title = "topic", "new poll"
        e_arg = ["one"]
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        # new option for existing topic
        content = "votingbot new poll\nadd: four"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "option", "new poll", "Four"
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll: add: four"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "option", "new poll", "Four"
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll: add four"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "option", "new poll", "Four"
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll add four"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "option", "new poll", "Four"
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll ADD four"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "option", "new poll", "Four"
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        # vote
        content = "votingbot new poll\n1"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "vote", "new poll", 1
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll: 1"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "vote", "new poll", 1
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll 1"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "vote", "new poll", 1
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        # results
        content = "votingbot new poll\nresults"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "results", "new poll", None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll: results"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "results", "new poll", None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll results"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "results", "new poll", None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot new poll RESULTS"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "results", "new poll", None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        # help
        content = "votingbot\nhelp"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "help", None, None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot: help"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "help", None, None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot help"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "help", None, None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))

        content = "votingbot HELP"
        action, title, arg = self.vb._parse_public_message(content)
        e_action, e_title, e_arg = "help", None, None
        self.assertEqual((action, title, arg), (e_action, e_title, e_arg),
                         (content, action, title, arg))


# @unittest.skip("need a debug_run.py module to run this test")
# class VotingBotIntegrationTest(unittest.TestCase):
#     """Integration test for VotingBot.

#     It runs a test instance of the bot configured by a debug_run module not
#     included in GitHub because it must contain credentials. A template of
#     a debug_run for VotingBot is provided instead.
#     """

#     @classmethod
#     def setUpClass(cls):
#         from debug_run import get_voting_bot
#         cls.vb = get_voting_bot()
#         cls.vb.main()

#     @classmethod
#     def tearDownClass(cls):
#         pass

#     @unittest.skip("need a debug_run.py module to run this test")
#     def test_complete_voting_process(self):

#         stream = "test-bot"
#         subject = "votingbot tests"


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
