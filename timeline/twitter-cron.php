<?php

$cache = dirname(__FILE__) . '/cache/twitter-json.txt';

//We use already made Twitter OAuth library
//https://github.com/mynetx/codebird-php
require_once ('codebird.php');

//Twitter OAuth Settings, enter your settings here:
$CONSUMER_KEY = '2rEbmYpUBOpR5gtcFcepqLH0C';
$CONSUMER_SECRET = 'K7MU6CQxRoG7VxKnHiS8alxifLxEEFjsp6TbfXIZalwK3VdNM8';
$ACCESS_TOKEN = '2593795213-nBvpQ2qp4lOBXdfjT78VhqTKkY50GGTWjeiP33K';
$ACCESS_TOKEN_SECRET = 'LsnEaKUTXGNfxUJypNCTm9lTxnG6Eb506Hyf1ToH0fzhp';

//Get authenticated
Codebird::setConsumerKey($CONSUMER_KEY, $CONSUMER_SECRET);
$cb = Codebird::getInstance();
$cb->setToken($ACCESS_TOKEN, $ACCESS_TOKEN_SECRET);


//retrieve posts
$q = 'eduwenca'; //$_POST['q'];
$count = 20; // $_POST['count'];
$api = 'statuses_mentionsTimeline'; //$_POST['api'];
$api = 'lists_statuses'; //$_POST['api'];

//https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
//https://dev.twitter.com/docs/api/1.1/get/search/tweets

//Make the REST call
$erreur = array(json_decode(file_get_contents('http://eduwenca.tk/twitter/cache/hashtagerror.txt'), true));

$data = array("all"=> array($cb->lists_statuses('slug=timeline&owner_screen_name=ewlftm')),
   "error"=> $erreur);

//Output result in JSON, getting it ready for jQuery to process
$data = json_encode($data);

$cachefile = fopen($cache, 'wb');
fwrite($cachefile,utf8_encode($data));
fclose($cachefile);

?>
