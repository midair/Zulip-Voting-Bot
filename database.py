import dataset
import os
import json

"""
This module handles the connection with a postgres database in a way that only
exposes a voting_topics_db object that can be used as a dictionary following
this structure:

Client exposed dictionary
-------------------------

voting_topics_db = {

    "movie": {

        "title": "Movie",

        "options": {
            0: ["Tron", 0],
            1: ["Back to the Future 1", 2],
            2: ["Hackers", 1]
        },

        "people_who_have_voted": {
            "agustin@hi.com": 1,
            "gonzalo@hi.com": 2,
            "claire@hi.com": 1
        }
    }
}

Database model
--------------

One table: "voting_topics"
Fields: "voting_title", "voting_dict"

"voting_title" is a string.
"voting_dict" values are string representations of a dictionary.
"""


class VotingTopics(object):

    """Voting topics database connection."""

    TABLE = "voting_topics"
    KEY_FIELD = "voting_title"
    VALUE_FIELD = "voting_dict"

    def __init__(self):
        self.db = self._connect_to_database()

    def _connect_to_database(self):

        database_name = str(os.environ["DB_NAME"])
        user = str(os.environ["DB_USER"])
        password = str(os.environ["DB_PASSWORD"])
        host = str(os.environ["DB_HOST"])
        port = str(os.environ["DB_PORT"])

        conn_str = "".join(["postgres://", user, ":-", password, "@",
                            host, ":", port, "/", database_name])

        db = dataset.connect(conn_str)

        return db

    def __iter__(self):
        return self.iterkeys()

    def __getitem__(self, voting_title):
        dict_params = {self.KEY_FIELD: voting_title}

        with self.db as db:
            row = db[self.TABLE].find_one(**dict_params)
            if not row:
                raise KeyError(voting_title)

        return json.loads(row[self.VALUE_FIELD])

    def __setitem__(self, voting_title, voting_dict):

        if voting_title not in self.keys():
            dict_params = {self.KEY_FIELD: voting_title,
                           self.VALUE_FIELD: json.dumps(voting_dict)}

            with self.db as db:
                db[self.TABLE].upsert(dict_params, [self.KEY_FIELD])

    def __delitem__(self, voting_title):
        # print "actually deleting", voting_title
        dict_params = {self.KEY_FIELD: voting_title}

        with self.db as db:
            db[self.TABLE].delete(**dict_params)

        print voting_title, "deleted!"

    def __contains__(self, voting_title):

        try:
            self[voting_title]
            return True

        except KeyError:
            return False

    has_key = __contains__

    # PUBLIC methods
    def get(self, voting_title):

        if voting_title not in self:
            return None

        else:
            return self[voting_title]

    def pop(self, voting_title):
        item = self[voting_title]
        del self[voting_title]

        return item

    def clear(self):
        for voting_title in self:
            del self[voting_title]

    # list methods
    def keys(self):
        with self.db as db:
            keys = [row[self.KEY_FIELD] for row in db[self.TABLE].all()]

        return keys

    def values(self):

        with self.db as db:
            values = [json.loads(row[self.VALUE_FIELD]) for
                      row in db[self.TABLE].all()]

        return values

    def items(self):

        with self.db as db:
            items = [(row[self.KEY_FIELD], json.loads(row[self.VALUE_FIELD]))
                     for row in db[self.TABLE].all()]

        return items

    # iter methods
    def iterkeys(self):

        with self.db as db:
            keys_iterator = (row[self.KEY_FIELD] for
                             row in db[self.TABLE].all())

        return keys_iterator

    def itervalues(self):
        with self.db as db:
            values_iterator = (json.loads(row[self.VALUE_FIELD]) for
                               row in db[self.TABLE].all())

        return values_iterator

    def iteritems(self):
        with self.db as db:
            items = ((row[self.KEY_FIELD], json.loads(row[self.VALUE_FIELD]))
                     for row in db[self.TABLE].all())

        return items
