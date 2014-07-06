<?

//retrieve posts
$q = $_POST['q'];
$count = $_POST['count'];
$api = $_POST['api'];
$hashtag = $_POST['hashtag'];

$params = array(
	'screen_name' => $q,
	'q' => $q,
	'count' => $count
);

if ($q == "cache"){
   $data = file_get_contents('cache/twitter-json.txt');
   $decode_data = json_decode($data, true);
   echo json_encode(json_encode($decode_data['all']['0']));
}

?>
