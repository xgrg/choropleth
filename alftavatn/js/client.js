/**
 * AJAX long-polling
 *
 * 1. sends a request to the server (without a timestamp parameter)
 * 2. waits for an answer from server.php (which can take forever)
 * 3. if server.php responds (whenever), put data_from_file into #response
 * 4. and call the function again
 *
 * @param timestamp
 */

function get_canvas_cards(fov){
      if (typeof(fov) === 'string') {
         var j= fov.split(',');
         var output1 = '';
         for (var i in j){
            var k = j[i].split('.');
            var item = '<b>' + k[0] + '</b><br>';
            item = item + '<img src="' + k[1] +'.png" /><br>';
            output1 = output1 + '<div class="item"><div class="tweet-wrapper"><span class="text">' + item + '</span></div></div>';
         }
         return output1;
      }
      return '';
}

function get_model_cards(model){
      if (typeof(model) === 'string') {
         var j= JSON.parse(model);
         var output1 = '';
         for (var key in j){
            var item = '<b>' + key + '</b><br>';
            for (var propname in j[key]){
               if (['geometry', 'position'].indexOf(propname) == -1){
                  item = item + ' &nbsp;&nbsp;&nbsp;' + propname + ' = ' + j[key][propname] + '<br>';
               }
            }
            output1 = output1 + '<div class="item"><div class="tweet-wrapper"><span class="text">' + item + '</span></div></div>';
         }
         return output1;
      }
}

function getContent(timestamp)
{
    var queryString = {'timestamp' : timestamp};

    $.ajax(
        {
            type: 'POST',
            url: 'poll',
            data: queryString,
            success: function(data){
               if (data != ''){
                // put result data into "obj"
                var obj = jQuery.parseJSON(data);
                // put the data_from_file into #response
                $('#response').html(obj.data_from_file);
                $('#fov').html(obj.visible_from_file);
                // call the function again, this time with the timestamp we just got from server.php
//$('#refreshcanvas').click();
                getContent(obj.timestamp);
               }
               else{
                  getContent();
               }
            }
        }
    );
}

// initialize jQuery
$(function() {
    getContent();
});
