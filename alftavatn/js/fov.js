
function fov_update(res){
      var fov = $.ajax({type:"POST", url:"", data: {'fov': 'True', 'player_name':player_id}, async:false} ).responseText;
      $("#fov").html(fov);
      if (res == undefined){
         f = JSON.parse(fov);
         for (var each in f){
            imobj = each;
            console.log(imobj);

            // Retrieves position from fov in json
            f = JSON.parse(fov);
            x = f[imobj]['x'];
            y = f[imobj]['y'];
            w = f[imobj]['w'];
            h = f[imobj]['h'];
            var imname = $.ajax({type:"POST", url:"", data: {'get_image_path': imobj}, async:false} ).responseText;
            var g_run2 = new Image();
            g_run2.src = imname ;
            g_GameObjectManager.applicationManager.sprites[imobj] = new VisualGameObject().startupVisualGameObject(imobj, g_run2, x, y, 1, w,h);
         }


      }
      else{
         diff = JSON.parse(res[1]);
         console.log(diff[0][player_id]);

         //First items that were added, then items deleted.

         for (var each in diff[1][player_id]){
            imobj = diff[1][player_id][each];
            if (imobj == g_GameObjectManager.selectedObject && diff[0][player_id].indexOf(imobj) == -1){
               g_GameObjectManager.unselectObject();
            }
            removeVisualGameObjectByName(imobj);
         }

         for (var each in diff[0][player_id]){
            imobj = diff[0][player_id][each];

            // Retrieves position from fov in json
            f = JSON.parse(fov);
            x = f[imobj]['x'];
            y = f[imobj]['y'];
            w = f[imobj]['w'];
            h = f[imobj]['h'];
            var imname = $.ajax({type:"POST", url:"", data: {'get_image_path': imobj}, async:false} ).responseText;
            var g_run2 = new Image();
            g_run2.src = imname ;
            g_GameObjectManager.applicationManager.sprites[imobj] = new VisualGameObject().startupVisualGameObject(imobj, g_run2, x, y, 1);
         }
      }
}
