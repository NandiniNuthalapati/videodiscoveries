$(function(){

  function loggedIn(result){
    console.log(result)
    $(".login").hide();
    $(".loggedIn").css("display", "block");
  }

  function loginRequired(result){
    $(".login").css("display", "block").click( function(){
      Backend.authenticate().then( loggedIn );
    });
  }

  Backend.authenticate({ immediate: true }).then( loggedIn, loginRequired );
});