
  $(document).ready(function() {


  if ($("#view-chart").length > 0) {
    var ctx = document.getElementById("view-chart").getContext('2d');
    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [{
          label: '# of Votes',
          data: [12, 19, 3, 5, 2, 3],
          backgroundColor: [
            'rgba(36, 109, 248, .2)'
          ],
          borderColor: [
            'rgba(36, 109, 248, 1 )'
          ],
          borderWidth: 1
        }]
      },
      options: {
        title: {
          display: false
        },
        gridLines: {
          display: false
        },
        legend: {
          display: false
        },
        tooltips: {
          mode: 'index',
          intersect: true
        },
        responsive: true,
        scales: {
          xAxes: [{
            stacked: true,
          }],
          yAxes: [{
            stacked: true,
          }]
        }
      }
    });
  }

	/*---------------------------------------------
		Dashboard
	---------------------------------------------*/

	$('.upload-profile-photo .file-input').change(function(){
	    var curElement = $(this).parent().parent().find('.image');
	    var reader = new FileReader();

	    reader.onload = function (e) {
	        // get loaded data and render thumbnail.
	        curElement.attr('src', e.target.result);
	    };

	    // read the image file as a data URL.
	    reader.readAsDataURL(this.files[0]);
	});

	$('.send-file .file-input').change(function(){
	    var curElement = $(this).parent().parent().find('.image');
	    var reader = new FileReader();

	    reader.onload = function (e) {
	        // get loaded data and render thumbnail.
	        curElement.attr('src', e.target.result);
	    };

	    // read the image file as a data URL.
	    reader.readAsDataURL(this.files[0]);
	});


  /*-------------------------------------
    tooltip
  -------------------------------------*/

  $('.user-number i').tooltip();

})

