<?php

$cache = dirname(__FILE__) . '/cache/twitter-json.txt';

//We use already made Twitter OAuth library
//https://github.com/mynetx/codebird-php
require_once ('codebird.php');

//Twitter OAuth Settings, enter your settings here:
$credentials = explode("\n", file_get_contents('cache/credentials.txt'));
$CONSUMER_KEY = $credentials[0];
$CONSUMER_SECRET = $credentials[1];
$ACCESS_TOKEN = $credentials[2];
$ACCESS_TOKEN_SECRET = $credentials[3];

//Get authenticated
Codebird::setConsumerKey($CONSUMER_KEY, $CONSUMER_SECRET);
$cb = Codebird::getInstance();
$cb->setToken($ACCESS_TOKEN, $ACCESS_TOKEN_SECRET);


//retrieve posts
$q = 'eduwenca'; //$_POST['q'];
$count = 800; // $_POST['count'];
$api = 'statuses_mentionsTimeline'; //$_POST['api'];
$api = 'lists_statuses'; //$_POST['api'];

//https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
//https://dev.twitter.com/docs/api/1.1/get/search/tweets

//Make the REST call
$erreur = array(json_decode(file_get_contents('cache/hashtagerror.txt'), true));

$data = array("all"=> array($cb->lists_statuses('slug=timeline&owner_screen_name=ewlftm&count=800')),
   "error"=> $erreur);

//Output result in JSON, getting it ready for jQuery to process
$data = json_encode($data);

$cachefile = fopen($cache, 'wb');
fwrite($cachefile,utf8_encode($data));
fclose($cachefile);

?>
