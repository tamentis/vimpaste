"""
Basic templates.
"""

welcome = r"""
Welcome to vimpaste
===================

vimpaste lets you paste your vim buffers online and share them as raw text
snippets with a simple unique identifier. All you need is our tiny vim plugin
to support the vp: syntax.

Requirements
------------
 - vim 6 or newer
 - curl

Installation/Upgrade
--------------------
You can use this anytime to install or upgrade the vimpaste plugin to the
most up to date version::

    mkdir -p ~/.vim/plugin/
    curl https://github.com/tamentis/vimpaste/raw/master/plugin/vimpaste.vim > ~/.vim/plugin/vimpaste.vim

Write something to vimpaste
---------------------------
From any vim buffer, just type (in normal mode, after Esc)::

    :w vp:

vimpaste will print an identifier at the bottom of your vim window, you can
give that identifier to anyone.

Open a vimpaste from an identifier
----------------------------------
You were given a code such as "vp:q1w2e3", here is how to read it::

    vim vp:q1w2e3

If vim is already opened, you can also do::

    :e vp:q1w2e3

You can also access your vimpaste from your browser::

    http://vimpaste/q1w2e3

Keep on saving!
---------------
If you created a vimpaste from a blank buffer or if you opened a vimpaste from
an identifier, you can use :w to save the paste as many times as you want.
Every save will create a new paste with its own identifier.

Expiration
----------
You can specify how long you want your snippet to be kept by adding the time
after vp: such as::

    :w vp:+2months

You can use hours, days, weeks, months and years.  Single letter shortcuts and
singular/plural forms are accepted, the following examples are valid::

    :w vp:+10d
    :w vp:+1day

The default without any value will be two weeks.

Limitations
-----------
 - 64kB per snippet
 - 10 years maximum expiration

Tell me how it works
--------------------
 - Heroku
 - Cloudant's CouchDB
 - http://github.com/tamentis/vimpaste/

vimpaste-%(version)s
"""


status = """Version: %(version)s
Allocated Slots: %(count)d
Cache Size: %(cache)d
Last Id: %(last_id)s
"""
