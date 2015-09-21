
// Graph

function Chart(params){
   this.name = params.name;
   text = params.text;
   this.sensevar = params.sensevar;
   this.websocket = params.websocket;
   this.updateInterval = params.updateInterval || 100;
   this.dataLength = params.dataLength || 500;

   this.data = [];

   this.chart = new CanvasJS.Chart(this.name, {
      title :{
         text: text
      },
      data: [{
         type: "line",
         dataPoints: this.data
      }]
   });
   this.render = this.chart.render;

   this.xVal = 0;

   this.updateChart = function () {

      // Checks if connection is alive first
      if (this.websocket.readyState >1){
         console.log('closed connection');
         clearInterval(this.intervalId);
         return;
      }

      this.websocket.send("SENSE@" + this.name + '@' + this.sensevar);
      if (this.data.length > this.dataLength)
      {
         this.data.shift();
      }
      this.render();

   };
   this.push = function(val) {
      this.data.push({
            x:this.xVal,
            y:val
            });
      this.xVal++;
   }
   this.start = function() {
      // update chart after specified time.
      this.intervalId = setInterval((function(self)
               { return function() {self.updateChart();}
               })(this), this.updateInterval);
   }
}

