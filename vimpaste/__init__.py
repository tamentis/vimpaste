import msg
from vimpaste.base62 import b62encode, b62decode
from vimpaste.db import init_db, save_new_doc


__version__ = "0.1.1"


def app(env, start_response):
    db = init_db()
    method = env["REQUEST_METHOD"]
    path = env["PATH_INFO"]

    # Welcome page
    if method == "GET" and path == "/":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ msg.welcome % { "version": __version__ } ]
    elif path == "/vimpaste.vim":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ msg.plugin % { "version": __version__ } ]

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

