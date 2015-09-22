
// Graph

function Chart(params){
   this.name = params.name;
   text = params.text;
   this.sensevar = params.sensevar;
   this.websocket = params.websocket;
   this.updateInterval = params.updateInterval || 100;
   this.dataLength = params.dataLength || 500;

   this.data = [];
   for (var i in params.sensevar){
      this.data.push({
         type:'spline',
         showInLegend: true,
         xVal:0,
         legendText: params.sensevar[i],
         dataPoints: []
      });
   }


   this.chart = new CanvasJS.Chart(this.name, {
      title :{
         animationEnabled: true,

         text: text
      },
      data: this.data,
      legend: {
         cursor: "pointer",
         itemclick: function (e) {
            if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
               e.dataSeries.visible = false;
            } else {
               e.dataSeries.visible = true;
         }
         chart.render();
         }
      }
   });
   this.render = this.chart.render;


   this.updateChart = function () {

      // Checks if connection is alive first
      if (this.websocket.readyState >1){
         console.log('closed connection');
         clearInterval(this.intervalId);
         return;
      }

      for (var i in this.sensevar){
         this.websocket.send("SENSE@" + this.name + '@' + this.sensevar[i]);
      }
      if (this.data.length > this.dataLength)
      {
         this.data.shift();
      }
      this.render();

   };
   this.push = function(val, dataset) {
      if (dataset === undefined && this.data.length != 1) {
         console.log('dataset should be precised if this.data.length is > 1');
         return;
      }
      for (var i in this.data){
         if (this.data[i].legendText == dataset || dataset === undefined) {
            this.data[i].dataPoints.push({
                  x:this.data[i].xVal++,
                  y:val
                  });

         }

      }
   }
   this.start = function() {
      // update chart after specified time.
      this.intervalId = setInterval((function(self)
               { return function() {self.updateChart();}
               })(this), this.updateInterval);
   }
}

