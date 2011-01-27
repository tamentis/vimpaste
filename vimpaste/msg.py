"""
Basic templates.
"""

welcome = """\
=======================
Welcome to vimpaste.com
=======================

VimPaste allows you to paste your vim buffers online and share them in raw text
with a simple identifier. Our tiny vim plugin adds support for our vp: syntax.

Requirements
------------
 - vim 6 or newer
 - curl

Installation/Upgrade
--------------------
You can use the same two lines to upgrade the plugin later on::

    mkdir -p ~/.vim/plugin/
    curl http://vimpaste.com/vimpaste.vim > ~/.vim/plugin/vimpaste.vim

Create a new VimPaste
---------------------
From vim, simply type:

    :w vp:

VimPastes will give you the identifier at the bottom of your terminal.

Open a VimPaste from an identifier
----------------------------------
You were given a code such as "vp:q1w2e3", here is how to read it::

    vim vp:q1w2e3

Keep on saving!
---------------
If you created a VimPaste from a blank buffer or if you opened a VimPaste from
an identifier, you can use :w to save the paste as many times as you want.
Every save will create a new paste with its own identifier.

Expiration
----------
You can specify how long you want VimPaste to keep your snippet by adding the
time after vp: such as::

    :w vp:+2months

You can use hours, days, weeks, months and years.  Single letter shortcuts and
singular/plural forms are accepted, the following examples are valid::

    :w vp:+10d
    :w vp:+1day

The default without any value will be two weeks.

Limitations
-----------
 - We limit to 16kB per paste. If you feel this is too short, let us know.
   Bigger pastes will just be cropped.
 - The maximum expiration is 10 years.

Tell me how it works
--------------------
 - Linux on EC2 (Ubuntu)
 - Apache + mod_wsgi + python2.6
 - CouchDB

You can see the code there:

    http://github.com/tamentis/vimpaste/

vimpaste-%(version)s
"""

plugin = """
" vimpaste.vim: (global plugin) Handles file transfer with VimPaste
" Last Change:	2011-01-26 22:57:37
" Maintainer:	Bertrand Janin <tamentis@neopulsar.org>
" Version:	%(version)s
" License:	ISC (OpenSource, BSD/MIT compatible)
" =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

"
" Configuration
"
let s:curl_exec = 'curl'

"
" Create a full http address from a vp:id name.
"
function! <SID>VpUrl(url, suffix)
	let l:index = stridx(a:url, ':')
	let l:vpid = substitute(strpart(a:url, l:index + 1),'\','/','g')
	return 'http://vimpaste.com/' . l:vpid
endfunction

"
" Read url content
"
function! <SID>VpGet(url)
	" 1. Create a tempfile if required
	if !exists('b:vp_tempfile')
		let b:vp_tempfile = tempname()
	endif
	" 2. Compute target URL
	let l:target_url = <SID>VpUrl(a:url, '')
	" 3. Run GET command
	silent exe "!" . s:curl_exec . ' -s -o "' .b:vp_tempfile . '" "' . l:target_url . '"'
	" 4. Insert the tempfile
	exe "0read " . b:vp_tempfile
	" 5. Fixup last blank line
	$delete
endfunction
" }}}

"
" Write url content
"
function! <SID>VpPut(url)
	" Save current buffer to temp file
	if !exists('b:vp_outgoing_tempfile')
		let b:vp_outgoing_tempfile = tempname()
	endif
	silent exe "write! " . b:vp_outgoing_tempfile
	set nomodified

	" Create temp file for return file with vp:id.
	if !exists('b:vp_incoming_tempfile')
		let b:vp_incoming_tempfile = tempname()
	endif
	" Compute target URL
	let l:target_url = <SID>VpUrl(a:url, '')
	" Run PUT command
	silent exe "!" . s:curl_exec . ' -s -o "' .b:vp_incoming_tempfile . '" --data-binary "@' . b:vp_outgoing_tempfile. '" "' . l:target_url . '"'
	for line in readfile(b:vp_incoming_tempfile, 'b', 1)
		if line =~ '^vp:'
			if bufname("%") == "" || stridx(bufname("%"), "vp:") == 0
				silent exe ':file ' . line
			endif
			echo 'VimPasted as ' . line
		endif
	endfor
endfunction

"
" Vp Commands
"
command! -nargs=1 VpGet call <SID>VpGet(<f-args>)
command! -nargs=1 VpPut call <SID>VpPut(<f-args>)

"
" Auto commands for vp:id format.
"
if version >= 600
	augroup Zope
	au!
	au BufReadCmd vp:* exe "doau BufReadPre ".expand("<afile>")|exe "VpGet ".expand("<afile>")|exe "doau BufReadPost ".expand("<afile>")
	au FileReadCmd vp:* exe "doau BufReadPre ".expand("<afile>")|exe "VpGet ".expand("<afile>")|exe "doau BufReadPost ".expand("<afile>")
	au BufWriteCmd vp:* exe "VpPut ".expand("<afile>")
endif
"""
