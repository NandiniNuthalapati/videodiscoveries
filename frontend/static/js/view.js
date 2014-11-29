$(function(){

  var unwatchedVideosCont = $(".unwatchedVideos");
  var videoPlayer = $("video");
  var videoPreviewPromise = Backend.getTemplate("videoPreview.mst");
  var videoPreview;

  function displayVideoSuggestions( videoResponse ){

    videos = videoResponse.items;
    unwatchedVideosCont.empty();

    if ( videos ) {

      numVideos = videos.length;

      _.each( videos, function(video){
        videoTemplate = $( Mustache.render( videoPreview, video ) );
        unwatchedVideosCont.append( videoTemplate );
        $.data( videoTemplate[0], "video", video);
      });

      $(".videoPreview").click( function(){
        playVideo( $.data( this, "video") );
        $(this).remove();
      });
    }

    else  {
      $(".noContent").clone( true ).appendTo( unwatchedVideosCont ).show();
    }
  }

  function displayFirstVideo( videoResponse ){
    if ( videoResponse.items ) {
      moreVideos();
      queueVideo( videoResponse.items.shift() );
    }
    else {
      noMoreVideos();
    }
  }

  function moreVideos(){
    $(".loggedIn").show();
    $(".noContent").hide();
  }

  function noMoreVideos(){
    $(".loggedIn").hide();
    $(".noContent").show();
  }

  function queueVideo( video ){
    Backend.getVideos( video.id ).done( displayVideoSuggestions );
    $.data( videoPlayer[0], "video", video);
    $(".videoPlayer .title").text( video.title );
    $(".videoPlayer .description").text( video.description );
    videoPlayer.attr({
      "poster": video.screenshotUri,
      "src": video.videoUri
    });
  }

  function playVideo( video ){
    queueVideo( video );
    videoPlayer[0].play();
  }

  $.when( videoPreviewPromise ).done( function( videoPreviewTemplate ){
    videoPreview = videoPreviewTemplate;
  });

  videoPlayer.bind("ended", function(){
    var video = $.data(this, "video");
    Backend.addViewedVideo( video.id );
  });

  videoPlayer.bind("playing", function(){
    $(".videoPlayer .title").hide();
  });

  $(".reset").click( function(){
    $.when( Backend.resetViewedVideos() ).then( Backend.getVideos ).done( displayFirstVideo );
  });

  $.when( Backend.login(), videoPreviewPromise ).then( Backend.getVideos ).done( displayFirstVideo );
});
