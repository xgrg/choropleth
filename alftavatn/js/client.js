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
