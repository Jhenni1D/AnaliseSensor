$(document).ready(function(){
  let m_container = document.querySelector("#m_container");
  let t_container = document.querySelector("#t_container");
  let termico_container = document.querySelector("#termico");
  let progresso = document.querySelector("#progresso");
  let namespace = '';
  let host = location.protocol + '//' + document.domain + ':' + location.port + namespace
  console.log(dado)
  console.log(host)
  if(dado.length !== 0)
  {
    for(d of dado)
      {
        check_data_type_and_create(d);
      }
  }
  let socket = io();

  socket.on('connect', function() {
    console.log('Connected!');

  });

  function create_img(name, img_src)
  {
    let h3 = document.createElement('h3');
    h3.innerHTML = name
	  let img = document.createElement('img');
    img.src = img_src
    let div = document.createElement('div');
    div.append(h3);
    div.append(img)
    return div
  }

  function check_data_type_and_create(data){
    if(data["type"] === "M")
    {
      m_container.append(create_img(data["name"], data["img"]))
    }
    else if(data["type"] === "T")
    {
      t_container.append(create_img(data["name"], data["img"]))
    }
    else
    {
                termico_container.append(create_img(data["name"], data["img"]))
    }
  }
  
  socket.on('plot_image', function(image_data) {
    check_data_type_and_create(image_data)
  });

  

  socket.on('progress_value', function(prog_value) {
    progresso.innerHTML = "Progresso: "+prog_value+"%"
  });

  socket.on('disconnect', function() {
    console.log('Disconnected!');
  });
});