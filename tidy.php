#!/usr/bin/php
<?php
/**
 * tidy.php
 *
 * See README for more information.
 *
 */


//////////////// DEFAULT CONFIGURATION ///////////////////

// some overwrites to make this useful as a plugin
/* moved to sublime settings file 
$custom_options = array(
	"indent" => true,
	"indent-spaces" => 4, 
	"wrap" => 100, 		
	"clean" => false,
	"show-body-only" => false,
    'indent-attributes' => false,
    'wrap-attributes' => false,
    'break-before-br' => false,
);  */

// some, but not all options for tidy
// found on http://www.php.net/manual/en/tidy.examples.basic.php
$default_options = array(
    'show-body-only' => false,
    'clean' => true,
    'char-encoding' => 'utf8',
    'add-xml-decl' => true,
    'add-xml-space' => false,
    'output-html' => true,
    'output-xml' => false,
    'output-xhtml' => false,
    'numeric-entities' => false,
    'ascii-chars' => false,
    'doctype' => 'strict',
    'bare' => true,
    'fix-uri' => true,
    'indent' => true,
    'indent-spaces' => 4,
    'tab-size' => 4,
    'wrap-attributes' => true,
    'wrap' => 0,
    'indent-attributes' => true,
    'join-classes' => false,
    'join-styles' => false,
    'enclose-block-text' => true,
    'fix-bad-comments' => true,
    'fix-backslash' => true,
    'replace-color' => false,
    'wrap-asp' => false,
    'wrap-jste' => false,
    'wrap-php' => false,
    'write-back' => true,
    'drop-proprietary-attributes' => false,
    'hide-comments' => false,
    'hide-endtags' => false,
    'literal-attributes' => false,
    'drop-empty-paras' => true,
    'enclose-text' => true,
    'quote-ampersand' => true,
    'quote-marks' => false,
    'quote-nbsp' => true,
    'vertical-space' => true,
    'wrap-script-literals' => false,
    'tidy-mark' => true,
    'merge-divs' => false,
    'repeated-attributes' => 'keep-last',
    'break-before-br' => true,
);

// this is the file we will tidy up - hardcoded for now
$tmpfile = '/tmp/htmltidy-sublime-buffer.php';

// merge default options with command line arguments
$config = parseArguments($default_options);

///////////// END OF DEFAULT CONFIGURATION ////////////////

error_reporting( E_ALL );

if ( !version_compare( phpversion(), "5.0", ">=" ) ) {
	echo "Error: tidy.php requires PHP 5 or newer.\n";
	exit( 1 );
}

//// main() ////

$tidy = new Tidy();

// let tidy do the work
#$tidy->parseString($html, $options);
$tidy->parseFile($tmpfile, $config, 'utf8');
// $tidy->cleanRepair();
// echo $tidy;

// write buffer back to tmofile
if ( !file_put_contents( $tmpfile, (string)$tidy ) ) {
	echo "Error: The file '".$tmpfile."' could not be overwritten.\n";
	exit( 1 );
}




/**
 * parseArguments: parse command line arguments and modify $defaults array
 * @param  array $defaults tidy config array to be modified
 * @return array modified config array
 */
function parseArguments($defaults) {

	// arguments starting with '--' will be $options
	// arguments without will be $files
	$files = array();
	$options = array();
	foreach ( $_SERVER['argv'] as $key => $value ) {
		if ( $key==0 ) continue;
		if ( substr( $value, 0, 2 )=="--" ) {
			$options[] = $value;
		} else {
			$files[] = $value;
		}
	}

	// loop trough options and overwrite default setting if found in array
	foreach ( $options as $option ) {
		
		list($key,$val) = split('=', $option);
		$key = str_replace('--', '', $key);

		if (array_key_exists($key, $defaults)) {
			$defaults[$key] = $val;
		} else {
			echo "Unknown option: '".$option."'\n";
			exit( 1 );			
		}

	}

	return $defaults;
}
