function deepEquals(o1, o2){
     var k1 = Object.keys(o1).sort();
     var k2 = Object.keys(o2).sort();
     if (k1.length != k2.length) return false;
     for (i=0 ; i < k1.length ; i++){
          if(typeof o1[k1[i]] == typeof o2[k2[i]] == "object"){
            return deepEquals(o1[k1[i]], o2[k2[i]])
          } else {
            return o1[k1[i]] == o2[k2[i]];
          }
     }
}

function json_diff(oldversion, newversion){
   oldv = JSON.parse(oldversion)['player'];
   newv = JSON.parse(newversion)['player'];
   added = [];
   removed = [];
   for ( var key in newv ) {
      if (!(oldv.hasOwnProperty(key))){
         added.push(key);
      }
      else{
         if (!(deepEquals(newv[key], oldv[key]))){
             removed.push(key);
             added.push(key);
         }
      }
   }
   for ( var key in oldv ) {
      if (!(newv.hasOwnProperty(key))){
         removed.push(key);
      }
   }
   return [added, removed];
}
