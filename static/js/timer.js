String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    return hours+':'+minutes+':'+seconds;
}

    function updateTimer() {
    for (var i in timer){

        if (timer[i] <= 0){
document.location.reload();

        }

      var x = document.getElementById("time_left"+i);
      x.textContent = parseInt(timer[i]).toString().toHHMMSS();
      timer[i] -= 1;

    console.log(i);
    }
}
updateTimer();
setInterval(updateTimer, 1000);