# HTML code formatter for Sublime Text 2
#### [Sublime Text 2](http://www.sublimetext.com/2)

## About
This is a Sublime Text 2 plugin allowing you to clean and tidy up your HTML code. 

It uses a version of `tidy`, which comes bundled with PHP 5.

Dedicated to Jeffrey Way @envatowebdev

## Usage
`ctrl + shift + P` and type `Tidy HTML`, or you can set up your own keybinding as shown below.

## Customize
You can customize a growing number of options in HtmlTidy.sublime-settings.

Open `Preferences -> Package Settings -> HtmlTidy -> Settings - Default` to see the available options.

Then open `Preferences -> Package Settings -> HtmlTidy -> Settings - User` (which will be empty on the first time), copy the default settings and start to modify them.

To set up a custom keybinding, you can insert the following line into your `Default.sublime-keymap`:

`{ "keys": ["ctrl+alt+t"], "command": "html_tidy"}`

## Known Issues

At this time, the plugin will only work on OS X and Linux since it depends on /usr/bin/php. This will be adapted for Windows shortly.

## Install

### Package Control (coming soon)

The easiest way to install this is with [Package Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text 2 before doing this next bit.
 * Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select HtmlTidy when the list appears.

Package Control will automatically keep HtmlTidy up to date with the latest version.

If you have some problems or improvements with it, contact me via GitHub.
