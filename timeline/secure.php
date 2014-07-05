<!DOCTYPE HTML>
<html lang="en-US">
<head>
     <link href='http://fonts.googleapis.com/css?family=Lato' rel='stylesheet' type='text/css'>

     <meta charset="UTF-8">
     <title>Timeline on the web</title>
     <link rel="stylesheet" href="style.css" />


</head>
<body data-hashtag="<?php if(isset($_GET['hashtag'])) {
   echo($_GET['hashtag']);
} ?>">

<div id="info">
        <div class="info-wrapper">
                <a href=""><b>Timeline on the web</b></a>
                <p id="desc">A report on progress of Cha and Greg across time and space.</p>
        </div>
</div>

<div id="jstwitter"></div>

</body>
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js" type="text/javascript"></script>
<script type="text/javascript" src="jquery.gridalicious.min.js"></script>
<script type="text/javascript" src="jquery.jstwitter.js"></script>
   <script type="text/javascript">
   $(function () {
      var d = new Date();
      var desc = ["A report on progress of Cha and Greg across time and space.",
             "A great story made of posts, one after another, by Cha and Greg.",
             "A timeline of my chérie and me.",
             "Life in posts by Cha and Greg. Open-source material."];
      $("p#desc").text(desc[d.getDate()%3]);
      // start jqtweet!
      JQTWEET.loadTweets($("body").data("hashtag"));
   });
</script>

</html>
