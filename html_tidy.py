import sublime, sublime_plugin, re, os, subprocess

class HtmlTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('HtmlTidy: invoked on file: %s' % ( self.view.file_name() ) )

        # path to plugin - <sublime dir>/Packages/PhpTidy
        pluginpath = sublime.packages_path() + '/HtmlTidy'
        scriptpath = pluginpath + '/tidy.php'

        # path to temp file
        tmpfile    = '/tmp/htmltidy-sublime-buffer.tmp'
        tidyerrors = '/tmp/htmltidy-error-log.tmp'
        phppath    = '/usr/bin/php'
        tidypath   = '/usr/bin/tidy'
        isWindows  = False

        # set different paths for php and temp file on windows
        if sublime.platform() == 'windows':
            tmpfile    = pluginpath + '/htmltidy-sublime-buffer.tmp'
            tidyerrors = pluginpath + '/htmltidy-error-log.tmp'
            tidypath   = pluginpath + '/win/tidy.exe'
            isWindows  = True
            # check if php.exe is in PATH
            phppath = 'php.exe'
            retval = os.system( '%s -v' % ( phppath ) )
            if not retval == 0:
                # try to find php.exe at predefined locations
                phppath = self.find_phppath()

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

        # load HtmlTidy settings    
        settings = sublime.load_settings('HtmlTidy.sublime-settings')    
        
        # load view settings for indentation
        use_tabs = not self.view.settings().get('translate_tabs_to_spaces')
        tab_size = int(self.view.settings().get('tab_size', 4))
        print('HtmlTidy: use_tabs: %s' % (use_tabs))
        print('HtmlTidy: tab_size: %s' % (tab_size))

        # build command line arguments
        args = '--indent-spaces=%s ' % (tab_size)
        arg2 = '--indent-spaces %s ' % (tab_size)
        if (use_tabs):
            args = '--tab-size=%s ' % (tab_size)
            arg2 = '--indent-spaces 4 --tab-size %s ' % (tab_size)

        # leave out default values
        for option in supported_options:
            default_value = supported_options[option]
            if default_value == True : default_value = 1
            if default_value == False: default_value = 0
            custom_value = settings.get(option)
            if custom_value == True : custom_value = 1
            if custom_value == False: custom_value = 0
            if not custom_value == None and not custom_value == default_value:
                #print "HtmlTidy: setting ", option, ": ", default_value, "->", custom_value
                args = args + (" --%s=%s" % (option,custom_value))
                arg2 = arg2 + (" --%s %s" % (option,custom_value))


        # check if native tidy is found
        if os.path.exists( tidypath ):
            # call /usr/bin/tidy on tmpfile
            arg2 += ' --indent 1 --tidy-mark 0 '
            print('HtmlTidy: calling tidy: "%s" %s -q -m -f "%s" "%s" ' % ( tidypath, arg2, tidyerrors, tmpfile ) )
            #     retval = os.system( '"%s" %s -q -m -f "%s" "%s" ' % ( tidypath, arg2, tidyerrors, tmpfile ) )
            retval = subprocess.call( '"%s" %s -q -m -f "%s" "%s"' % ( tidypath, arg2, tidyerrors, tmpfile ), shell = not isWindows )

            if retval != 0:
                print('HtmlTidy: tidy returned error code: %s' % (retval))

            # read error log and delete
            if os.path.exists( tidyerrors ):
                fileHandle = open ( tidyerrors, 'r' ) 
                errors = fileHandle.read() 
                fileHandle.close() 
                os.remove( tidyerrors )
                print('HtmlTidy: error log contained: \n\n%s' % (errors))

        else:
            # check if php is at phppath
            retval = subprocess.call( '%s -v' % ( phppath ), shell = not isWindows )
            if not retval == 0:
                sublime.error_message('HtmlTidy cannot find php.exe. Make sure it is available in your PATH.')
                return

            # check if tidy.php is found - this has become obsolete since it's bundled
            if not os.path.exists( scriptpath ):
                sublime.error_message('HtmlTidy cannot find the script at %s.' % (scriptpath))
                return

            # call tidy.php on tmpfile
            print('HtmlTidy: calling script: "%s" "%s" "%s" %s' % ( phppath, scriptpath, tmpfile, args ) )
            retval = subprocess.call( '"%s" "%s" "%s" %s' % ( phppath, scriptpath, tmpfile, args ), shell = not isWindows )
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

        # convert spaces to tabs if view settings say so
        if (use_tabs):
            newContent = self.entab( newContent )

        # write new content back to buffer
        self.view.replace(edit, bufferLength, self.fixup(newContent))
        

    # Fixup from external command
    def fixup(self, string):
        return re.sub(r'\r\n|\r', '\n', string.decode('utf-8'))

    # convert spaces to tabs
    # http://code.activestate.com/recipes/66433-change-tabsspaces-with-regular-expressions/
    def entab(self, temp, tab_width=4, all=0):

        # if all is true, every time tab_width number of spaces are found next
        # to each other, they are converted to a tab.  If false, only those at
        # the beginning of the line are converted.  Default is false.

        if all:
            temp = re.sub(r" {" + `tab_width` + r"}", r"\t", temp)
        else:
            patt = re.compile(r"^ {" + `tab_width` + r"}", re.M)
            temp, count = patt.subn(r"\t", temp)
            i = 1
            while count > 0:
                #this only loops a few times, at most six or seven times on
                #heavily indented code
                subpatt = re.compile(r"^\t{" + `i` + r"} {" + `tab_width` + r"}", re.M)
                temp, count = subpatt.subn("\t"*(i+1), temp)
                i += 1
        return temp


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
            #'indent-spaces' : 4,
            #'tab-size' : 4,
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
            'break-before-br' : True,
            'new-blocklevel-tags' : '',
            'new-pre-tags' : '',
            'new-inline-tags' : ''
        }

    # get a list of possible locations for php.exe on windows
    def find_phppath(self):
        # get list of locations
        locations = self.get_possible_php_locations()
        # loop through locations
        for loc in locations:
            # check if file exists at location
            if os.path.exists( loc ):
                print('HtmlTidy: found php.exe at: %s' % ( loc ) )
                return loc

    # get a list of possible locations for php.exe on windows
    def get_possible_php_locations(self):
        return (
            r'c:\php\php.exe',
            r'c:\php5\php.exe',
            r'c:\windows\php.exe',
            r'c:\program files\php\php.exe',
            r'c:\xampp\php\php.exe',
            r'c:\wamp\bin\php\php5\php.exe',
            r'c:\wamp\bin\php\php\php.exe',
            r'C:\wamp\bin\php\php5.3.9\php.exe',
            r'C:\wamp\bin\php\php5.3.10\php.exe',
            r'C:\Program Files\wamp\php\php.exe',
            r'D:\Program Files\wamp\php\php.exe',
            r'/usr/bin/php'
        )


