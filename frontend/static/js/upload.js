$(function(){

  var progressBar = $("#progressBar");
  var progress = $("#progress");
  var fileForm = document.getElementById("fileForm");
  var screenshotSelector = $("#screenshotSelector video");

  function uploadVideo(getUrlResult){
    var screenShot = getScreenshot();
    var form = new FormData( fileForm );
    form.append("screenshot", dataURItoBlob(screenShot), "screenshot.jpg");
    $("#select").hide();
    progress.show().find("img")[0].src = screenShot;
    return Backend.uploadVideo( form, getUrlResult.uploadUrl, uploadProgress );
  }

  function getScreenshot(){
    var videoElement = screenshotSelector[0];
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg");
  }

  function dataURItoBlob(dataURI) {
    var splitData = dataURI.split(',');
    var byteString = atob(splitData[1]);
    var mimeString = splitData[0].split(':')[1].split(';')[0];
    var intArray = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
      intArray[i] = byteString.charCodeAt(i);
    }
    return new Blob([intArray], {type:mimeString});
  }

  function uploadProgress(evt){
    if (evt.lengthComputable) {
      progressBar.attr({
        "max" : evt.total,
        "value" : evt.loaded 
      });
    }
  }

  function uploadComplete(){
    progress.hide();
    $("#complete").show();
  }

  $("#video").bind("change", function(){
    var videoFile = this.files[0];
    screenshotSelector.attr( "src", URL.createObjectURL(videoFile) )
    $("#screenshotSelector").show();
  });

  $(fileForm).submit( function(evt){
    $("#submit").attr("disabled", true).addClass("pure-button-disabled");
    evt.preventDefault();
    Backend.getUploadUrl().then( uploadVideo ).then( uploadComplete );
  });

});