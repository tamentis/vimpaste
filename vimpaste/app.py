import msg
import base64
from tools import b62encode, b62decode, extract_expiration
from db import init_db, save_paste, get_paste, TooManySaves


__version__ = "0.1.4"

MAX_LEN = 65536


def app(env, start_response):
    method = env["REQUEST_METHOD"]
    path = env["PATH_INFO"]

    init_db()

    # "Static" pages.
    if method == "GET" and path == "/":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ msg.welcome % { "version": __version__ } ]
    elif path == "/vimpaste.vim":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ msg.plugin % { "version": __version__ } ]

    # Get expiration if any
    path, exp = extract_expiration(path)

    # Wrong syntax
    try:
        id = b62decode(path[1:])
    except ValueError:
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [ "Invalid VimPaste Id Syntax" ]

    # Create a new post
    if method == "POST":
        data = env["wsgi.input"].read(int(env["CONTENT_LENGTH"]))[:MAX_LEN]
        try:
            new_id = save_paste(id, base64.b64encode(data), exp)
        except TooManySaves:
            start_response("400 Bad Request", [("Content-Type", "text/plain")])
            print("Too many saves! Flood?")
            return [ "Too many saves!" ]

        print("New Paste: %d" % new_id)
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [ "vp:%s" % b62encode(new_id) ]

    # Document not found
    doc = get_paste(id)
    if not doc or doc["new"]:
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [ "VimPaste Not Found" ]

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [ base64.b64decode(doc["raw"]) ]

