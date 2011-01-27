"""
Thin and ugly couchdb access layer.
"""

import couchdb
import time
import random


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
        }
    }
}

def generate_blanks(amount=10):
    """Generate documents when we're running out of expired posts."""
    print("Generating %d blank documents:" % amount)

    res = db.view("usage/highest_id", reduce=True)
    if len(res) == 0:
        base_id = 0
    else:
        base_id = res.rows[0].value + 1

    print(" - Starting at %d" % base_id)

    for i in range(base_id, base_id+amount):
        doc = { "_id": str(i), "new": True }
        try:
            db.save(doc)
        except couchdb.ResourceConflict:
            pass


def get_available_doc():
    """Get the first available paste, be it an expired one or a fresh
    new paste. If we can't find one, let's generate a few.
    """
    res = db.view("usage/reusable", limit=5, include_docs=True)

    # Need some more!
    if len(res) == 0:
        generate_blanks()
        return get_available_doc()

    return random.choice([row.doc for row in res.rows])


def save_new_doc(id, data):
    """Let's save this stuff somewhere, find an available doc and update it."""
    doc = get_available_doc()
    new_doc = doc.copy()
    new_doc["raw"] = data
    new_doc["source"] = id
    new_doc["new"] = False
    # Keep it two weeks by default
    new_doc["expires"] = int(time.time() + 60 * 60 * 24 * 14)
    try:
        db.save(new_doc)
    except ResourceConflict:
        return save_new_doc(id, data)
    return int(doc.id)


def init_db():
    """Reference the database and enforce the design document."""
    server = couchdb.Server()
    if "vimpaste" not in server:
        print("Creating initial database.")
        server.create("vimpaste")
        generate_blanks()
    db = server["vimpaste"]

    # Make sure the design docs are in place.
    current_design = db.get("_design/usage")
    if not current_design:
        print("Creating initial design document.")
        db.save(design)
    elif current_design["views"] != design["views"]:
        print("Updating design document...")
        new_design = current_design.copy()
        new_design["views"] = design["views"]
        db.save(new_design)

    return db

