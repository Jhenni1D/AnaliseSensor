$(document).ready(function () {
  let progresso = document.querySelector("#progresso");
  let namespace = '';
  let host = location.protocol + '//' + document.domain + ':' + location.port + namespace;

  let eficience_percent = document.querySelector("#eficiencia");

  let m_images = {
    "M0": document.querySelector("#m0"),
    "M1": document.querySelector("#m1"),
    "M2": document.querySelector("#m2"),
    "M3": document.querySelector("#m3")
  }

  let t_images = {
    "T0": document.querySelector("#t0"),
    "T1": document.querySelector("#t1"),
    "T2": document.querySelector("#t2"),
    "T3": document.querySelector("#t3")
  }

  let termico_image = document.querySelector("#termico")

  console.log(dado)
  console.log(host)

  UpdateImages();

  function UpdateImages()
  {
      if (dado.length !== 0) {
        for (d of dado) {
          if (d["name"] in m_images) {
            m_images[d["name"]].src = `/static/image_test/${d["name"]}.png`;
            m_images[d["name"]].classList.remove('placeholder')
          }

           if (d["name"] in t_images) {
             t_images[d["name"]].src = `/static/image_test/${d["name"]}.png`;
             t_images[d["name"]].classList.remove('placeholder')
           }

           if (d["name"] == "TERMICO") {
             termico_image.src = `/static/image_test/${d["name"]}.png`;
             termico_image.classList.remove('placeholder')
           }
        }
      }
  }
  /*
      LÓGICA DO SOCKETIO ABAIXO.
  */

  let socket = io();

  socket.on('connect', function () {
    console.log('Connected!');
    socket.emit('progress_test');
  });


  socket.on('update_image', function (data_updated) {
    dado = data_updated;
    UpdateImages();
  });



  socket.on('progress_value', function (prog_value) {
    progresso.style["width"] = `${prog_value}%`;
    progresso.innerHTML = `${prog_value}%`;
  });

  socket.on('disconnect', function () {
    console.log('Disconnected!');
  });
});