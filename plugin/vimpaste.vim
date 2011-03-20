" vimpaste.vim: (global plugin) Handles file transfer with VimPaste
" Last Change:	2011-01-26 22:57:37
" Maintainer:	Bertrand Janin <tamentis@neopulsar.org>
" Version:	0.1.5
" License:	ISC (OpenSource, BSD/MIT compatible)
" =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

"
" Configuration
"
let s:curl_exec = 'curl'
let s:main_url = 'http://vimpaste.com/'
"let s:main_url = 'http://localhost:9000/'

"
" Create a full http address from a vp:id name.
"
function! <SID>VpUrl(url, suffix)
	let l:index = stridx(a:url, ':')
	let l:vpid = substitute(strpart(a:url, l:index + 1),'\','/','g')
	return s:main_url . l:vpid
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
