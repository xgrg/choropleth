
         function tokenformat(item){
            return "<li>" + "<img src='" + item.image + "' title='" + item.name + "' height='25px' width='25px' style='display:inline-block; vertical-align:top;' />" + "<div style='display: inline-block; padding-left: 5px; vertical-align:top; line-height:25px; height:25px'>" + item.name + "</div></li>";
         }

function get_objects(){

     var res = $.ajax({type:"POST", url:"", data: {'get_objects': 'True'}, async:false} ).responseText;
     res = res.split(',');
     var html = '';
     for (each in res){
       html = html + '<span style="border:solid black 1px;" class="object" data-object="'+res[each]+'">'+res[each]+'</span> '
     }
     return html;
}

function click_action(clickedaction){
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

function refresh_model(res){
      //var res = $.ajax({type:"POST", url:"php/get_model.php", data: {}, async:false} ).responseText;
      var output1 = get_model_cards(res);
      return output1;
}

function click_item(clickeditem){
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
