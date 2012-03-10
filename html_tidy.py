import sublime, sublime_plugin, re, os

class HtmlTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('HtmlTidy: invoked on file: %s' % ( self.view.file_name() ) )

        # path to plugin - <sublime dir>/Packages/PhpTidy
        pluginpath = sublime.packages_path() + '/HtmlTidy'
        scriptpath = pluginpath + '/tidy.php'

        # path to temp file
        tmpfile = '/tmp/htmltidy-sublime-buffer.tmp'
        phppath = '/usr/bin/php'

        # set different paths for php and temp file on windows
        if sublime.platform() == 'windows':
            tmpfile = pluginpath + '/htmltidy-sublime-buffer.tmp'
            phppath = 'php.exe'
            retval = os.system( '%s -v' % ( phppath ) )
            if not retval == 0:
                sublime.error_message('HtmlTidy cannot find %s. Make sure it is available in your PATH.' % (phppath))
                return

        # check if tidy.php is found
        if not os.path.exists( scriptpath ):
            sublime.error_message('HtmlTidy cannot find the script at %s.' % (scriptpath))
            return

        # get current buffer content
        bufferLength  = sublime.Region(0, self.view.size())
        bufferContent = self.view.substr(bufferLength).encode('utf-8')

        # write tmpfile
        fileHandle = open ( tmpfile, 'w' ) 
        fileHandle.write ( bufferContent ) 
        fileHandle.close() 
        print('HtmlTidy: buffer written to tmpfile: %s' % (tmpfile))

        # get supported tidy options
        supported_options = self.get_supported_options()

        # apply settings    
        settings = sublime.load_settings('HtmlTidy.sublime-settings')    
        # settings = self.view.settings()
        # indent_spaces = int(settings.get('htmltidy-indent-spaces', 4))

        # build command line arguments
        # leaves out default values
        args = ''
        for option in supported_options:
            default_value = supported_options[option]
            if default_value == True : default_value = 1
            if default_value == False: default_value = 0
            custom_value = settings.get('htmltidy-'+option)
            if custom_value == True : custom_value = 1
            if custom_value == False: custom_value = 0
            if not custom_value == None and not custom_value == default_value:
                # print "HtmlTidy: setting ", option, ": ", default_value, "->", custom_value
                args = args + (" --%s=%s" % (option,custom_value))

        # call tidy.php on tmpfile
        print('HtmlTidy: calling script: %s "%s" "%s" %s' % ( phppath, scriptpath, tmpfile, args ) )
        retval = os.system( '%s "%s" "%s" %s' % ( phppath, scriptpath, tmpfile, args ) )
        if retval != 0:
            print('HtmlTidy: script returned: %s' % (retval))
            if retval == 32512:
                sublime.error_message('HtmlTidy cannot find php at %s.' % (phppath))
                return
            else:
                sublime.error_message('There was an error calling the script at %s. Return value: %s' % (scriptpath,retval))
                return

        # read tmpfile and delete
        fileHandle = open ( tmpfile, 'r' ) 
        newContent = fileHandle.read() 
        fileHandle.close() 
        os.remove( tmpfile )
        print('HtmlTidy: tmpfile was processed and removed')

        # write new content back to buffer
        self.view.replace(edit, bufferLength, self.fixup(newContent))


    # Fixup from external command
    def fixup(self, string):
        return re.sub(r'\r\n|\r', '\n', string.decode('utf-8'))

    # get supported options and default values
    def get_supported_options(self):
        return {
            'show-body-only' : False,
            'clean' : True,
            'char-encoding' : 'utf8',
            'add-xml-decl' : True,
            'add-xml-space' : False,
            'output-html' : True,
            'output-xml' : False,
            'output-xhtml' : False,
            'numeric-entities' : False,
            'ascii-chars' : False,
            'doctype' : 'strict',
            'bare' : True,
            'fix-uri' : True,
            'indent' : True,
            'indent-spaces' : 4,
            'tab-size' : 4,
            'wrap-attributes' : True,
            'wrap' : 0,
            'indent-attributes' : True,
            'join-classes' : False,
            'join-styles' : False,
            'enclose-block-text' : True,
            'fix-bad-comments' : True,
            'fix-backslash' : True,
            'replace-color' : False,
            'wrap-asp' : False,
            'wrap-jste' : False,
            'wrap-php' : False,
            'write-back' : True,
            'drop-proprietary-attributes' : False,
            'hide-comments' : False,
            'hide-endtags' : False,
            'literal-attributes' : False,
            'drop-empty-paras' : True,
            'enclose-text' : True,
            'quote-ampersand' : True,
            'quote-marks' : False,
            'quote-nbsp' : True,
            'vertical-space' : True,
            'wrap-script-literals' : False,
            'tidy-mark' : True,
            'merge-divs' : False,
            'repeated-attributes' : 'keep-last',
            'break-before-br' : True  
        }


