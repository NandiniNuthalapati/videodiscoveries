$(function(){

  function loggedIn(result){
    $(".login").hide();
    $(".loggedIn").show();
  }

  function loginRequired(result){
    $(".login").show().click( function(){
      Backend.authenticate().then( loggedIn );
    });
  }

  Backend.authenticate({ immediate: true }).then( loggedIn, loginRequired );
});