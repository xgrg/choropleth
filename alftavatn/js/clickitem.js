
function tokenformat(item){

    return "<li>" + "<img src='" + item.image + "' title='" + item.name +
        "' height='25px' width='25px' style='display:inline-block; vertical-align:top;' />"
        + "<div style='display: inline-block; padding-left: 5px; vertical-align:top;"
        + "line-height:25px; height:25px'>" + item.name + "</div></li>";
}

function get_objects(){
// A Javascript proxy to query the server on existing objects
// Returns an HTML string to be displayed (the objects are clickable)

    var res = $.ajax({type:"POST", url:"", data: {'get_objects': 'True'}, async:false} ).responseText;
    res = res.split(',');
    var html = '';
    for (each in res){
        html = html + '<span style="border:solid black 1px;" class="object" data-object="'+res[each]+'">'+res[each]+'</span> '
    }
    return html;
}

function click_action(clickedaction){
// A Javascript proxy to send an action once an object and an action
// have been clicked.
// It then resets the objects and the actions and calls the function click_item

    var obj = clickedaction.data('object');
    var action = clickedaction.data('action');
    var res = $.ajax({type:"POST", url:"", data: {'dialog': obj + ',' + action}, async:false} ).responseText;
    var res = $.ajax({type:"POST", url:"", data: {'send_action': 'True', 'action':action, 'object': obj}, async:false} ).responseText;
    var html = get_objects();
    $('#objects').html(html);
    $("#actions").html('');
    $('span.object').click(function(){
        click_item($(this));
    });
}


function click_item(clickeditem){
// Once an object was clicked, it fetches a list of possible actions
// and lets the user click on one of them.

    var obj = clickeditem.data('object');
    $("span.object").css("background-color", "white");
    clickeditem.css("background-color", "darksalmon");
    var res = $.ajax({type:"POST", url:"", data: {'get_actions': 'True', 'object':obj}, async:false} ).responseText;
    res = res.split(',');
    var html = '';
    for (each in res){
        html = html + '<span style="border:solid black 1px;" class="action" data-object="'+ obj +'" data-action="'+res[each]+'">'+res[each]+'</span> '
    }
    $("#actions").html(html);

    $("span.action").click(function(){
         click_action($(this));
    });
}
