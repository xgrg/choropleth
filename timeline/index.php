<?php
$username = "admin";
$password = "admin";
$nonsense = "supercalifragilisticexpialidocious";

if (isset($_GET['hashtag']) && str_replace(array('"', "'"), '', $_GET['hashtag']) != ''){
   include("secure.php");
}
else {

if (isset($_COOKIE['PrivatePageLogin'])) {
   if ($_COOKIE['PrivatePageLogin'] == md5($password.$nonsense)) {
?>

    <!-- LOGGED IN CONTENT HERE -->
<?php    include("secure.php"); ?>

<?php
      exit;
   } else {
      echo "Bad Cookie.";
      exit;
   }
}

if (isset($_GET['p']) && $_GET['p'] == "login") {
   if ($_POST['user'] != $username) {
      echo "Sorry, that username does not match.";
      exit;
   } else if ($_POST['keypass'] != $password) {
      echo "Sorry, that password does not match.";
      exit;
   } else if ($_POST['user'] == $username && $_POST['keypass'] == $password) {
      setcookie('PrivatePageLogin', md5($_POST['keypass'].$nonsense));
      header("Location: $_SERVER[PHP_SELF]");
   } else {
      echo "Sorry, you could not be logged in at this time.";
   }
}
?>
And the login form on the page...

<form action="<?php echo $_SERVER['PHP_SELF']; ?>?p=login" method="post">
<label><input type="text" name="user" id="user" /> Name</label><br />
<label><input type="password" name="keypass" id="keypass" /> Password</label><br />
<input type="submit" id="submit" value="Login" />
</form>
<?php
}
?>
