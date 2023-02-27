$(document).ready(function(){
  let div_teste = document.querySelector("#teste-div");
  let button_teste = document.querySelector("#teste-button");
  let namespace = '';
  let host = location.protocol + '//' + document.domain + ':' + location.port + namespace
  console.log(host)
  let socket = io();

  button_teste.onclick = function () {
    console.log("CLICOU EM MIM!");
    div_teste.innerHTML = "FOI CLICADOOOOOO!";
    socket.emit("testando", "vai")
    //socket.emit('open_measurement', takeShot());

    //button_finish_shut.removeAttribute('hidden');
    //button_finish_open.setAttribute('hidden', 'hidden')
  };

  socket.on('connect', function() {
    console.log('Connected!');

  });

  socket.on('plot_image', function(image) {
    div_teste.innerHTML = "Imagem: "+ image;
  });

  socket.on('disconnect', function() {
    console.log('Disconnected!');
  });
});