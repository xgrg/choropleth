function getData(charts){
   data = [];
   i = 0
   for (key in charts) {
      obj = charts[key].data;
      for (var j in obj){
         data.push([]);
         for (k in obj[j].dataPoints) {
            data[i].push(obj[j].dataPoints[k].y);
         }
         i++;
      }
   };
   return data;
}

function normalize(data){
    var min = 100000.0, max = -10000.0;
    res = [];
    data.forEach(function (row, row_index) {
      row.forEach(function (entry, column_index) {
         if (entry < min){ min = entry; }
         if (entry > max){ max = entry; }
      });
    });
    var i=0;
    data.forEach(function (row, row_index) {
      res.push([]);
      row.forEach(function (entry, column_index) {
         res[i].push((entry - min)/(max - min));
      });
      i++;
    });
    return res;
}

function normalize_per_chart(data){
    res = [];
    var i=0;
    data.forEach(function (row, row_index) {
      res.push([]);
      var min = 100000.0, max = -10000.0;
      row.forEach(function (entry, column_index) {
         if (entry < min){ min = entry; }
         if (entry > max){ max = entry; }
      });
      row.forEach(function (entry, column_index) {
         res[i].push((entry - min)/(max - min));
      });
      i++;
    });
    return res;
}


function drawCanvas(charts) {
    var the_color = "rgba(0,0,255,alpha_token)";
    // ask for the json and register the following
    // function (second argument to getJSON) to be called
    // once it is delivered:
    data = normalize_per_chart(getData(charts));
    //data = $.parseJSON(jsonstring); //, function(data) {
    console.log(data);
    // no more jquery for now
    var canvas = document.getElementById("circles");
    // you declare these to avoid them being global variables:
    var h, w, column_width, column_height, x_pos, y_pos, radius;
    margin_width = 100;
    h = canvas.height;
    w = canvas.width - margin_width;
    column_width = w / data[0].length;
    column_height = h / data.length;
    // we're working in 2 dimensions:
    var context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.font = "8px Arial";
    radius = column_width / 2;
    labels = [];
    for (var i in charts){
        for (var j in charts[i].data){
           labels.push(charts[i].data[j].legendText);
        }
    }
    data.forEach(function (row, row_index) {
      y_pos = row_index * 2*radius + radius;
      context.strokeStyle = "rgb(0,0,0)";
      context.strokeText(labels[row_index],0,y_pos+2);
      row.forEach(function (entry, column_index) {
        x_pos = column_index * column_width + radius + margin_width;
        context.moveTo(x_pos, y_pos);
        context.beginPath();
        context.arc(x_pos, y_pos, radius, 0, Math.PI*2)
        context.fillStyle = the_color.replace(/alpha_token/, entry);
        context.strokeStyle = the_color.replace(/alpha_token/, entry);
        context.fill();
        context.stroke();
        context.closePath();
      });
    });
}
