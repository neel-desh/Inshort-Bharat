

// https://codepen.io/gapgag55/pen/ZBENwJ/?editors=0010

(function ($) {
  $(document).ready(function () {
    
    uploadImage()
    
    function uploadImage() {
      var button = $('.upload-images .pic')
      var uploader = $('<input type="file" accept="image/*" />')
      var images = $('.upload-images')
      
      button.on('click', function () {
        uploader.click()
      })
      
      uploader.on('change', function () {
          var reader = new FileReader()
          reader.onload = function(event) {
            images.prepend('<div class="img" style="background-image: url(\'' + event.target.result + '\');" rel="'+ event.target.result  +'"><span class="ti-close"></span></div>')
          }
          reader.readAsDataURL(uploader[0].files[0])
  
       })
      
      images.on('click', '.img', function () {
        $(this).remove()
      })
    
    }
    

  })
})(jQuery)

