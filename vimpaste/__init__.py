import couchdb
import msg
import random
from base62 import b62encode, b62decode

documents = {
    123: "woot\nuber woot\n",
    432: "this is not a vimpaste\n\nyes it is",
}

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
    print("Generating %d blank documents..." % amount)

    res = db.view("usage/highest_id", reduce=True)
    if len(res) == 0:
        base_id = 0
    else:
        base_id = res.rows[0].value + 1

    for i in range(base_id, base_id+amount):
        doc = { "_id": str(i), "new": True }
        try:
            db.save(doc)
        except couchdb.ResourceConflict:
            pass

def get_available_doc():
    res = db.view("usage/reusable", limit=5, include_docs=True)

    # Generate a few more extra docs if needed.
    if len(res) == 0:
        generate_blanks()
        return get_available_doc()

    return random.choice([row.doc for row in res.rows])


def save_new_doc(id, data):
    doc = get_available_doc()
    new_doc = doc.copy()
    new_doc["raw"] = data
    new_doc["source"] = id
    new_doc["new"] = False
    try:
        db.save(new_doc)
    except ResourceConflict:
        return save_new_doc(id, data)
    return int(doc.id)


# Initialize couchdb db
print("Referencing CouchDB database.")
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


def app(env, start_response):
    method = env["REQUEST_METHOD"]
    path = env["PATH_INFO"]

    # Welcome page
    if path == "/":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ msg.welcome ]

    # Wrong syntax
    try:
        id = b62decode(path[1:])
    except ValueError:
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [ "Invalid VimPaste Id Syntax" ]

    # Create a new post
    if method == "POST":
        data = env["wsgi.input"].read(int(env["CONTENT_LENGTH"]))
        new_id = save_new_doc(id, data)
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ "vp:%s" % b62encode(new_id) ]

    # Document not found
    doc = db.get(str(id))
    if not doc or doc["new"]:
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [ "VimPaste Not Found" ]

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [ str(doc["raw"]) ]

