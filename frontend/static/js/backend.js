// All backend calls return jQuery promises
var Backend = (function(){

  var apiRoot = "/_ah/api/videodiscovery/v1/";
  var deferredLogin = $.Deferred();
  var deferredLoadScript = $.Deferred();

  return {

    addViewedVideo: function( videoId ){
      return $.ajax({
        url: apiRoot + "user/viewedVideoIds",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ viewedVideoIds : [ videoId ] })
      });
    },

    authenticate: function(config){

      var deferred = $.Deferred();

      var authorizationComplete = function() {
        var auth = gapi.auth.getToken();
        if ( auth && auth.access_token ) {
          $.ajaxSetup({ headers: { 'Authorization': auth.token_type + " " + auth.access_token } });
          deferred.resolve();
          deferredLogin.resolve();
        }
        else {
          deferred.reject();
        }
      };

      Backend.loadAuthScripts().then( function(){
        config = config || {};
        config.client_id = '337666371549-tur26e822fdqtim89majsuo4n8mvvefh.apps.googleusercontent.com';
        config.scope = 'https://www.googleapis.com/auth/userinfo.email';
        gapi.auth.authorize( config, authorizationComplete );
      });

      return deferred.promise();
    },

    getVideos: function(referenceId){
      var data = referenceId ? { "referenceId" : referenceId } : undefined;
      return $.ajax({
        url: apiRoot + "videos",
        data: data
      });
    },

    getUploadUrl: function(){
      return $.ajax( apiRoot + "upload" );
    },

    getTemplate: function(templateName){
      var templatePath = "/static/templates/" + templateName
      return $.ajax( templatePath );
    },

    loadAuthScripts: function(){
      if (deferredLoadScript.state() != "resolved") {
        window.gapiReady = function(){ deferredLoadScript.resolve(); };
        var script = document.createElement('script');
        script.src = "https://apis.google.com/js/client.js?onload=gapiReady";
        document.head.appendChild(script);
      }
      return deferredLoadScript.promise();
    },

    login : function(){
      return deferredLogin.promise();
    },

    resetViewedVideos: function(){
      return $.ajax({
        url: apiRoot + "user/viewedVideoIds",
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify({ viewedVideoIds : [] })
      });
    },

    uploadVideo: function(form, url, progress){
      return $.ajax({
        url: url,
        contentType: false,
        processData: false,
        type: "POST",
        data: form,
        xhr: function() {
          myXhr = $.ajaxSettings.xhr();
          if(myXhr.upload){
            myXhr.upload.addEventListener('progress', progress, false);
          }
          return myXhr;
        }
      });
    }
  };

})();
