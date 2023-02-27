$(document).ready(function(){
  let folders_div = document.querySelector("#folders");
  let namespace = '';
  let host = location.protocol + '//' + document.domain + ':' + location.port + namespace
  console.log(host)
  let socket = io();

  socket.on('connect', function() {
    console.log('Connected!');

  });

  function create_folder(value)
  {
    let div = document.createElement('div');
    let br = document.createElement('br');
    let a = document.createElement('a');
    a.innerHTML = value
    a.href = "/visualizar/"+value
    div.append(a);
    div.append(br);
    return div
  }
  
  socket.on('create_folder', function(data) {
    folders_div.innerHTML = ""
    for(folder of data)
    {
      folders_div.append(create_folder(folder))
    }
  });

  socket.on('disconnect', function() {
    console.log('Disconnected!');
  });
});