"""
Thin and ugly couchdb access layer.
"""

import os
import couchdb
import time
import random

_db = None
_cache = []
_timestamp = 0
_timestamp_count = 0

# This is the design document we're trying to enforce on the connected
# database. It is checked at every startups.
design = {
    "_id": "_design/usage",
    "language": "javascript",
    "views": {
        "reusable": {
            "map": """
                function(doc) {
                    if (doc.expires >= (new Date()).getTime()) {
                        emit([doc.expires, doc.id], null)
                    } else if (doc.new) {
                        emit([0, doc.id], null)
                    }
                }"""
        },
        "highest_id": {
            "map": """function(doc) { emit("highest_id", parseInt(doc._id)) }""",
            "reduce": """
                function(keys, values) {
                    var max = 0;
                    for (var i = 0; i < values.length; i++) {
                        if (values[i] > max) {
                        max = values[i];
                        }
                    }
                    return max;
                }"""
        },
        "allocated": {
            "map": """function(doc) { emit("allocated", 1); }""",
            "reduce": """_sum"""
        }
    }
}

class TooManySaves(Exception):
    """Raised when we feel flooded."""
    pass

def generate_blanks(amount=5):
    """Generate documents when we're running out of expired posts."""
    print("Generating %d blank documents:" % amount)

    res = _db.view("usage/highest_id", reduce=True)
    if len(res) == 0:
        base_id = 0
    else:
        base_id = res.rows[0].value + 1

    print(" - Starting at %d" % base_id)

    for i in range(base_id, base_id+amount):
        doc = { "_id": str(i), "new": True }
        try:
            _db.save(doc)
        except couchdb.ResourceConflict:
            pass


def get_available_doc():
    """Get the first available paste, be it an expired one or a fresh
    new paste. If we can't find one, let's generate a few.
    """
    res = _db.view("usage/reusable", limit=5, include_docs=True)

    # Need some more!
    if len(res) == 0:
        generate_blanks()
        return get_available_doc()

    return random.choice([row.doc for row in res.rows])


def save_paste(source_id, data, expiration):
    """Let's save this stuff somewhere, find an available doc and update it."""
    global _timestamp, _timestamp_count

    # Clumsy flood management
    now = int(time.time())
    if _timestamp != now:
        _timestamp = now
        _timestamp_count = 1
    else:
        _timestamp_count += 1

    if _timestamp_count > 10:
        raise TooManySaves()

    doc = get_available_doc()
    new_doc = doc.copy()
    new_doc["raw"] = data
    new_doc["source"] = source_id
    new_doc["new"] = False
    # Keep it two weeks by default
    new_doc["expires"] = int(time.time() + expiration)
    try:
        _db.save(new_doc)
    except ResourceConflict:
        return save_paste(id, data, expiration)
    id = int(doc.id)
    _cache.append(new_doc)
    while len(_cache) > 50:
        _cache.pop(0)
    return id


def get_paste(id):
    for doc in _cache:
        if int(doc["_id"]) == id:
            print("Fetching %d from cache..." % id)
            return doc
    return _db.get(str(id))


def allocated_slots():
    """How many slots are allocated in the database at the moment."""
    res = _db.view("usage/allocated", reduce=True)
    return res.rows[0].value


def cache_len():
    """Return the current size of the cache."""
    return len(_cache)


def last_paste_id():
    """Return the identifier of the latest paste created if any."""
    if _cache:
        return int(_cache[-1]["_id"])
    else:
        return 0


def init():
    """Reference the database and enforce the design document."""
    global _db

    if _db: return

    # That's in case we are hosted in Heroku...
    couch_url = os.environ.get("CLOUDANT_URL")
    if couch_url:
        kwargs = {"url": couch_url}
    else:
        kwargs = {}

    server = couchdb.Server(**kwargs)
    if "vimpaste" not in server:
        print("Creating initial database.")
        _db = server.create("vimpaste")
    else:
        _db = server["vimpaste"]

    # Make sure the design docs are in place.
    current_design = _db.get("_design/usage")
    if not current_design:
        print("Creating initial design document.")
        _db.save(design)
    elif current_design["views"] != design["views"]:
        print("Updating design document...")
        new_design = current_design.copy()
        new_design["views"] = design["views"]
        _db.save(new_design)


