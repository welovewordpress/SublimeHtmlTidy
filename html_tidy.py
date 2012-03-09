import sublime, sublime_plugin, re, os
import pprint

class HtmlTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('HtmlTidy: invoked on file: %s' % ( self.view.file_name() ) )

        # path to temp file
        tmpfile = '/tmp/htmltidy-sublime-buffer.php'
        phppath = '/usr/bin/php'

        # path to plugin - <sublime dir>/Packages/PhpTidy
        pluginpath = sublime.packages_path() + '/HtmlTidy'

        # set script and check if it exists
        scriptpath = pluginpath + '/tidy.php'
        if not os.path.exists( scriptpath ):
            sublime.error_message('HtmlTidy cannot find the script at %s.' % (scriptpath))
            return

        # get current buffer
        bufferLength  = sublime.Region(0, self.view.size())
        bufferContent = self.view.substr(bufferLength).encode('utf-8')

        # write tmpfile
        fileHandle = open ( tmpfile, 'w' ) 
        fileHandle.write ( bufferContent ) 
        fileHandle.close() 
        print('HtmlTidy: buffer written to tmpfile: %s' % (tmpfile))

        # supported tidy options
        supported_options = self.get_supported_options()
        # pprint.pprint(supported)

        # apply settings    
        settings = sublime.load_settings('HtmlTidy.sublime-settings')    
        # settings = self.view.settings()
        # indent_spaces = int(settings.get('htmltidy-indent-spaces', 4))

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
        print('HtmlTidy: calling script: %s "%s" %s' % ( phppath, scriptpath, args ) )
        retval = os.system( '%s "%s" %s' % ( phppath, scriptpath, args ) )
        if retval != 0:
            print('HtmlTidy: script returned: %s' % (retval))
            if retval == 32512:
                sublime.error_message('HtmlTidy cannot find php at %s.' % (phppath))
                return
            else:
                sublime.error_message('There was an error calling the script at %s. Return value: %s' % (scriptpath,retval))


        # read tmpfile and delete
        fileHandle = open ( tmpfile, 'r' ) 
        newContent = fileHandle.read() 
        fileHandle.close() 
        os.remove( tmpfile )
        print('HtmlTidy: tmpfile was processed and removed')

        # write new content back to buffer
        self.view.replace(edit, bufferLength, self.fixup(newContent))


        # reminder: different ways of logging errors in sublime
        #
        # sublime.status_message('opening file: %s' % (FILE))
        # sublime.error_message(tmpfile)
        # self.show_error_panel(self.fixup(tmpfile))


    # Error panel & fixup from external command
    # https://github.com/technocoreai/SublimeExternalCommand
    def show_error_panel(self, stderr):
        panel = self.view.window().get_output_panel("php_tidy_errors")
        panel.set_read_only(False)
        edit = panel.begin_edit()
        panel.erase(edit, sublime.Region(0, panel.size()))
        panel.insert(edit, panel.size(), stderr)
        panel.set_read_only(True)
        self.view.window().run_command("show_panel", {"panel": "output.php_tidy_errors"})
        panel.end_edit(edit)

    def fixup(self, string):
        return re.sub(r'\r\n|\r', '\n', string.decode('utf-8'))

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


