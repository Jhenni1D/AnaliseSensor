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

  if (dado.length !== 0) {
    for (d of dado) {
      if (d["name"] in m_images) {
        m_images[d["name"]].src = `/static/image_test/${d["name"]}.png`;
      }

      // if (d["name"] in t_images) {
      //   m_images[d["name"]].src = img_source.replace("img_name", d["img"])
      // }

      // if (d["name"] == "TERMICO") {
      //   termico_image.src = img_source.replace("img_name", d["img"])
      // }
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


  socket.on('plot_image', function (image_data) {
    // TODO: inserir lógica de por imagens aqui
  });



  socket.on('progress_value', function (prog_value) {
    progresso.style["width"] = `${prog_value}%`;
    progresso.innerHTML = `${prog_value}%`;
  });

  socket.on('disconnect', function () {
    console.log('Disconnected!');
  });
});