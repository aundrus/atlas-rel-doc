<!DOCTYPE html>
<html>

<style>
body {
  color: black;
  link: navy;
  vlink: maroon;
  alink: tomato;
  background: floralwhite;
  font-family: Arial, sans-serif;
  font-size: 10pt;
}
</style>

<head>
<title>Dynamic Directory List</title>
</head>

<body>

  <H3>ATLAS CI and Nightly Documentation</H3>
  <H4>Dynamic Directory List</H4>

<?php
function title() {
    $url = substr( $_SERVER['REQUEST_URI'], 1 );
    if ( empty( $url ) ) $url = '/';
    return dirname($url);
}

$cwdir=dirname(__FILE__);
#print "<h4>" . str_replace( '/', ' <span>/</span> ', title() ) . "</h4>";
print "<h4>" . $cwdir . "</h4>";

$files = scandir('.');
$exclude = array( '.', '..');
$exclude_match = array ( '/^index.*$/i', '/^\..*$/');
foreach ( $exclude as $exc ) {
    if ( ( $key = array_search( $exc, $files ) ) !== false ) {
        unset( $files[$key] );
    }
}
$exclude_matching_files = array();
foreach ( $exclude_match as $ep ) {
    foreach($files as $file) {
        if (preg_match($ep, $file) == 1) {
            $exclude_matching_files[] = $file;
        }
    }
}
$good_files = array_diff($files, $exclude_matching_files);
sort($good_files);
foreach ($good_files as $file) {
  if ($file != '.' && $file != '..') {
    echo '<li><a href="' . $file . '">' . $file . '</a></li>';
  }
}
echo '</ul>';
?>

</body></html>
