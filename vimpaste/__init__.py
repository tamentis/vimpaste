import msg
import base64
from vimpaste.tools import b62encode, b62decode, extract_expiration
from vimpaste.db import init_db, save_paste, get_paste


__version__ = "0.1.1"


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
        data = env["wsgi.input"].read(int(env["CONTENT_LENGTH"]))
        new_id = save_paste(id, base64.b64encode(data), exp)
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

