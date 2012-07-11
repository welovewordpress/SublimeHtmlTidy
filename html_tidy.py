import sublime
import sublime_plugin

import re
import os
import subprocess
from collections import defaultdict

############### CONSTANTS ###############

supported_options = [
    'add-xml-decl',
    'add-xml-space',
    'alt-text',
    'anchor-as-name',
    'assume-xml-procins',
    'bare',
    'clean',
    'css-prefix',
    'decorate-inferred-ul',
    'doctype DocType auto',
    'drop-empty-paras',
    'drop-font-tags',
    'drop-proprietary-attributes',
    'enclose-block-text',
    'enclose-text',
    'escape-cdata',
    'fix-backslash',
    'fix-bad-comments',
    'fix-uri',
    'hide-comments',
    'hide-endtags',
    'indent-cdata',
    'input-xml',
    'join-classes',
    'join-styles',
    'literal-attributes',
    'logical-emphasis',
    'lower-literals',
    'merge-divs',
    'merge-spans',
    'ncr',
    'new-blocklevel-tags',
    'new-empty-tags',
    'new-inline-tags',
    'new-pre-tags',
    'numeric-entities',
    'output-html',
    'output-xhtml',
    'output-xml',
    'preserve-entities',
    'quote-ampersand',
    'quote-marks',
    'quote-nbsp',
    'repeated-attributes',
    'replace-color',
    'show-body-only',
    'uppercase-attributes',
    'uppercase-tags',
    'word-2000',
    'break-before-br',
    'indent',
    'indent-attributes',
    'indent-spaces',
    'markup',
    'punctuation-wrap',
    'sort-attributes',
    'split',
    'tab-size',
    'vertical-space',
    'wrap',
    'wrap-asp',
    'wrap-attributes',
    'wrap-jste',
    'wrap-php',
    'wrap-script-literals',
    'wrap-sections',
    'ascii-chars',
    'char-encoding',
    'input-encoding',
    'language',
    'newline',
    'output-bom',
    'output-encoding',
    'error-file',
    'force-output',
    'gnu-emacs',
    'gnu-emacs-file',
    'keep-time',
    'output-file',
    'tidy-mark',
    'write-back'
]

re_ID = re.compile(r"""<[^>]*?id\s*=\s*("|')(.*?)("|')[^>]*?>""", re.DOTALL | re.MULTILINE)

############### FUNCTIONS ###############


def tidy_string(input_string, script, args, shell):
    print 'HtmlTidy: '
    print args
    command = [script] + args

    p = subprocess.Popen(
        command,
        bufsize=-1,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=shell
    )

    return p.communicate(input_string.encode('utf8'))


def remove_duplicate_ids(html):
    'Removes duplicated IDs in the parsed markup. Adapted from the Sublime Text 1 webdevelopment package.'
    idsn = defaultdict(int)
    matches = []

    for m in re_ID.finditer(html):
        id = m.group(2)
        idsn[id] += 1
        matches.append(m)

    for match in reversed(matches):
        id = match.group(2)

        n = idsn[id]
        idsn[id] -= 1

        if n > 1:
            start, end = match.span(2)
            html = "%s%s%s%s" % (html[:start], id, str(n), html[end:])

    return html

############### CLASS ###############


class HtmlTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('HtmlTidy: invoked on file: %s' % (self.view.file_name()))

        # path to plugin - <sublime dir>/Packages/PhpTidy
        pluginpath = sublime.packages_path() + '/HtmlTidy'
        scriptpath = pluginpath + '/tidy.php'

        # path to temp file
        phppath = '/usr/bin/php'
        tidypath = '/usr/bin/tidy'

        # set different paths for php and temp file on windows
        if sublime.platform() == 'windows':
            tidypath = pluginpath + '/win/tidy.exe'
            tidy_exists = os.system(tidypath + ' -v')
            if tidy_exists:
                use_tidyexe = 1

            else:
                phppath = 'php.exe'
                retval = os.system('%s -v' % (phppath))
                if not retval == 0:
                    # try to find php.exe at predefined locations
                    phppath = self.find_phppath()

        # get current buffer content
        bufferLength = sublime.Region(0, self.view.size())
        bufferContent = self.view.substr(bufferLength).encode('utf-8')

        args = self.get_args()

        # check if native tidy is found
        if (os.path.exists(tidypath) or use_tidyexe):
            # call /usr/bin/tidy on tmpfile
            script = tidypath
            shell = False

        else:
            script = 'php "{0}"'.format(scriptpath)
            shell = True

        tidied, err = tidy_string(bufferContent, script, args, shell)

        # convert spaces to tabs if view settings say so
        if (not self.view.settings().get('translate_tabs_to_spaces')):
            tidied = self.entab(tidied)

        # write new content back to buffer
        self.view.replace(edit, bufferLength, self.fixup(tidied))

    def fixup(self, string):
        'Fixup from external command'
        return re.sub(r'\r\n|\r', '\n', string.decode('utf-8'))

    def get_args(self):
        'Builds command line arguments.'
        args = []

        # load HtmlTidy settings
        settings = sublime.load_settings('HtmlTidy.sublime-settings')

        # load view settings for indentation
        tab_size = int(self.view.settings().get('tab_size', 4))
        print('HtmlTidy: tab_size: %s' % (tab_size))

        args.extend(['--tab-size', str(tab_size)])

        # leave out default values
        for option in supported_options:
            custom_value = settings.get(option)

            # If custom value isn't set, ignore that setting.
            if custom_value is None:
                continue

            if custom_value == True:
                custom_value = '1'
            if custom_value == False:
                custom_value = '0'

            # print "HtmlTidy: setting " + option + ": " + custom_value
            args.extend(["--" + option, custom_value])

        return args

    # convert spaces to tabs
    # http://code.activestate.com/recipes/66433-change-tabsspaces-with-regular-expressions/
    def entab(self, temp, tab_width=4, all=0):

        # if all is true, every time tab_width number of spaces are found next
        # to each other, they are converted to a tab.  If false, only those at
        # the beginning of the line are converted.  Default is false.

        if all:
            temp = re.sub(r" {" + repr(tab_width) + r"}", r"\t", temp)
        else:
            patt = re.compile(r"^ {" + repr(tab_width) + r"}", re.M)
            temp, count = patt.subn(r"\t", temp)
            i = 1
            while count > 0:
                 # this only loops a few times, at most six or seven times on
                 # heavily indented code
                subpatt = re.compile(r"^\t{" + repr(i) + r"} {" + repr(tab_width) + r"}", re.M)
                temp, count = subpatt.subn("\t" * (i + 1), temp)
                i += 1
        return temp

    # get a list of possible locations for php.exe on windows
    def find_phppath(self):
        # get list of locations
        locations = self.get_possible_php_locations()
        # loop through locations
        for loc in locations:
            # check if file exists at location
            if os.path.exists(loc):
                print('HtmlTidy: found php.exe at: %s' % (loc))
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
