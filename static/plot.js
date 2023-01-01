
function plot(canvas, title, data) {
    var chart = new Chart(canvas, {
	    // The type of chart we want to create
	    type: 'line', // also try bar or other graph types

	    // The data for our dataset
	    data: data,

	    // Configuration options
	    options: {
        layout: {
            padding: 10,
        },
		legend: {
			position: 'bottom',
		},
		title: {
			display: false,
			text: title
		},
		scales: {
			yAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'Close Price'
				}
			}],
			xAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'Date'
				}
			}]
		}
	}
});


}


function updateChart() {
  var symbol = document.getElementById("symbol-select").value;
  var timeframe = document.getElementById("timeframe-select").value;

  $.ajax({
      url: "/chart",
      type: "get",
      data: {"symbol": symbol, "timeframe":timeframe},
      success: function(response) {
        $("#chart-wrapper").html(response);
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
}


function buttonClick(symbol){
console.log(symbol)
$.ajax({
      url: "/remove",
      type: "POST",
      data: {"symbol": symbol},
      success: function(response) {
        console.log("remove done")
        location.reload();
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
}

function gotoAdd(){
window.location.href = '/add';
}