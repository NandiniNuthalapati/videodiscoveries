$(function(){

  var unwatchedVideosCont = $(".unwatchedVideos");
  var videoTag = $("video");
  var videoPlayerTitle = $(".videoPlayer .title");
  var videoPreviewPromise = Backend.getTemplate("videoPreview.mst");
  var similarVideos = $(".similarVideos");
  var noContent = $(".noContent");
  var videoPlayer = $(".videoPlayer");
  var videoPreview;

  function displayVideoSuggestions( videoResponse ){

    videos = videoResponse.items;
    unwatchedVideosCont.empty();

    if ( videos ) {

      moreVideos();
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
      noMoreVideos( true );
    }
  }

  function displayFirstVideo( videoResponse ){
    if ( videoResponse.items ) {
      videoPlayer.show();
      moreVideos();
      queueVideo( videoResponse.items.shift() );
    }
    else {
      videoPlayer.hide();
      noMoreVideos();
    }
  }

  function moreVideos(){
    similarVideos.show();
    noContent.hide();
    noContent.removeClass("noContentRight")
  }

  function noMoreVideos( onRight ){
    similarVideos.hide();
    noContent.show();
    if (onRight) {
      noContent.addClass( "noContentRight" );
    }
  }

  function queueVideo( video ){
    Backend.getVideos( video.id ).done( displayVideoSuggestions );
    $.data( videoTag[0], "video", video);
    videoPlayerTitle.text( video.title );
    $(".videoPlayer .description").text( video.description );
    videoTag.attr({
      "poster": video.screenshotUri,
      "src": video.videoUri
    });
  }

  function playVideo( video ){
    queueVideo( video );
    videoTag[0].play();
  }

  $.when( videoPreviewPromise ).done( function( videoPreviewTemplate ){
    videoPreview = videoPreviewTemplate;
  });

  videoTag.bind("ended", function(){
    var video = $.data(this, "video");
    Backend.addViewedVideo( video.id );
    videoPlayerTitle.show();
  });

  videoTag.bind("pause", function(){
    videoPlayerTitle.show() 
  });

  videoTag.bind("playing", function(){
    videoPlayerTitle.hide();
  });

  $(".reset").click( function(){
    $.when( Backend.resetViewedVideos() ).then( Backend.getVideos ).done( displayFirstVideo );
  });

  $.when( Backend.login(), videoPreviewPromise ).then( Backend.getVideos ).done( displayFirstVideo );
});
