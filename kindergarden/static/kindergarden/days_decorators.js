  if ( django.jQuery("#id_wednesday")) {
    var days = ["monday", "tuesday", "wednesday", "thursday", "friday"];
    var today = new Date();
    for (var i = 0; i < days.length; i++) {
      var day_name = days[i];
      console.log(day_name);
      django.jQuery.get(
        "/dayofweek/" + String(today.getFullYear()) +"/"+ String(today.getMonth()+1)+"/" + day_name + "/",
        null,
        function(data) {
          django.jQuery("#"+data.day_of_week+"-check").text("Počet rezervací pro následující den: " + String(data.day_reservations));
        },
        "json");
    }
  }
