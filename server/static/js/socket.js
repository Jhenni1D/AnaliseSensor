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

  let graficos_images = {
    "TERMICO": document.querySelector("#termico"),
    "TENSAO": document.querySelector("#tensao"),
    "TEMPERATURA": document.querySelector("#temperatura"),
    "EFICIENCIA": document.querySelector("#eficiencia"),
    //"VELOCIDADE": document.querySelector("#velocidade"),
  }

  let modal_img = document.querySelector("#modal_img")
  let modal_title = document.querySelector("#title_modal")

  console.log(dado)
  console.log(host)

  UpdateImages();
  RegisterActions();
  PlotGraphData();

  function UpdateImages()
  {
      if (dado.length !== 0) {
        for (d of dado) {
          if (d["name"] in m_images) {
            m_images[d["name"]].src = d["img"];
            m_images[d["name"]].classList.remove('placeholder')
          }

           if (d["name"] in t_images) {
             t_images[d["name"]].src = d["img"];
             t_images[d["name"]].classList.remove('placeholder')
           }

//           if (d["name"] in graficos_images) {
//             graficos_images[d["name"]].src = d["img"];
//             graficos_images[d["name"]].classList.remove('placeholder')
//           }
        }
      }
  }
  function RegisterActions()
  {
      for (img in m_images)
      {
        m_images[img].addEventListener('click', ShowModalImage);
      }

      for (img in t_images)
      {
        t_images[img].addEventListener('click', ShowModalImage);
      }

//      for (img in graficos_images)
//      {
//        graficos_images[img].addEventListener('click', ShowModalImage);
//      }
  }

  function ShowModalImage(event)
  {
    modal_img.src = event.srcElement.src;
    modal_title.innerHTML = event.srcElement.id.toUpperCase();
  }

  function PlotGraphData()
  {
    console.log(graph_data)
    let colors = ['blue', 'red', 'green', 'purple', 'orange']
    let index_color = 0
    for(graph in graph_data)
    {
        console.log(graph_data[graph])
        if(graph_data[graph].hasOwnProperty("values"))
        {
            let ctx = document.getElementById(graph);
            let data = {}
            data =
            {
                datasets:
                [
                    {
                        borderColor: colors[index_color++],
                        label: `${graph.toLocaleUpperCase()} / Tempo`,
                        data: graph_data[graph]['values']
                    }
                ]
            }
            let chart = new Chart(ctx,
            {
                type: 'line',
                data: data,
                options:
                {
                    scales: {
//                         x:
//                         {
//                            ticks: {
//                              autoSkip: false,
//                              maxRotation: 360,
//                              minRotation: 10
//                            }
//                         }
                    }
                }
            });
        }
    }
  }


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