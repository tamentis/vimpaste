"""
Basic templates.
"""

welcome = """\
Welcome to vimpaste.com
=======================
This free service allows you to paste your vim buffer to this site and share
the raw text with a simple id and without any HTML crap around it.

All you need is curl and a small plugin that you can install with:

    mkdir ~/.vim/plugin/
    curl http://vimpaste.com/vimpaste.vim > ~/.vim/plugin/vimpaste.vim

You can then open the vimpastes with the following:

    vim vp:f71dD

If you save this buffer, it will automatically save it to vimpaste with a new
id. You just need to hit ^G to find out the id of this new vimpaste.

You can also access your vimpastes with a standard GET call on your browser:

    http://vimpaste.com/f71dD

vimpaste-%(version)s
"""

plugin = """
" vimpaste.vim: (global plugin) Handles file transfer with VimPaste
" Last Change:	2011-01-24 21:52:34
" Maintainer:	Bertrand Janin <tamentis@neopulsar.org>
" Version:	%(version)s
" License:	MIT
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
	let l:vpid = substitute(strpart(a:url, l:index + 1),'\\','/','g')
	return 'http://localhost:9000/' . l:vpid
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
	silent exe "!" . s:curl_exec . ' -o "' .b:vp_tempfile . '" "' . l:target_url . '"'
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
	exe "write! " . b:vp_outgoing_tempfile
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
			silent exe ':file ' . line
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
