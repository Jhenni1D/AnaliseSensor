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

  let grafico_corrent = document.querySelector("#corrente");

  let graficos_images = {
    "SensorTensao": document.querySelector("#tensao"),
    "SensorTemp": document.querySelector("#temperatura"),
    "SensorRPM": document.querySelector("#rpm"),
    "eficiencia": document.querySelector("#eficiencia")
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
    let corrent_colors = ['blue', 'red', 'green']
    let index_color = 0;
    let index_corrent_color = 0;
    let corrent_graph_data =
    {
        datasets:
        [
//            {
//                borderColor: "blue",
//                label: "SensorA / Tempo",
//                data: [{"x": "16/7/2024 23:18:39", y: 0.5}, {"x": "16/7/2024 23:49:39", y: 1.5}, {"x": "16/7/2024 23:50:01", y: 2.0}]
//            },
//            {
//                borderColor: "blue",
//                label: "SensorB / Tempo",
//                data: [{"x": "D", y: 1.5}, {"x": "E", y: 2.2}, {"x": "F", y: 2.8}]
//            },
        ]
    }

    for(graph in graph_data)
    {
        console.log(graph_data[graph])
        if(graph_data[graph].hasOwnProperty("values") && graficos_images.hasOwnProperty(graph))
        {
            let ctx = graficos_images[graph];
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
                    }
                }
            });
        }
        if(IsCorrentSensor(graph))
        {
            let data_set_item =
            {
                borderColor: corrent_colors[index_corrent_color++],
                label: `${graph.toLocaleUpperCase()} / Tempo`,
                data: graph_data[graph]['values']
            };
            corrent_graph_data.datasets.push(data_set_item);
        }
    }
    if(graph_data !== undefined)
    {
        let corrent_chart = new Chart(document.querySelector("#corrente"),
        {
            type: 'line',
            data: corrent_graph_data,
            options:
            {
                scales: {
                }
            }
        });
    }
  }

  function IsCorrentSensor(sensor)
  {
    return sensor == "SensorA" || sensor == "SensorB" || sensor == "SensorC";
  }
   // ATUALIZAÇÃO DOS GRÁFICOS
    function FormatSensorsData(sensors_data)
    {
        sensors_data_formatted = {}
        for(sensor in sensors_data)
        {
            sensors_data_formatted[sensor] = {"values": []}
            for(sensor_info of sensors_data[sensor])
            {
                graph_info = {"x": sensor_info["data"]+" "+sensor_info["hora"], "y": parseFloat(sensor_info["medicao"])}
                sensors_data_formatted[sensor]["values"].push(graph_info)
            }
        }

        return sensors_data_formatted;
    }

    function FormatCorrentSensorData(corrent_sensor_data)
    {
        let only_values = []
        for (data of corrent_sensor_data)
        {
            only_values.push(data["y"])
        }

        return only_values;
    }

    function loadDoc()
    {
      const xhttp = new XMLHttpRequest();
      xhttp.onload = function()
      {
        var sensors_data = JSON.parse(this.responseText);
        graph_data = FormatSensorsData(sensors_data);
        PlotGraphData();
        loadDoc();
      }

        xhttp.open("GET", "https://simulacao-femm-default-rtdb.firebaseio.com/medicoes/Pastas/16-07-2024_22-05-39-3528/Sensores/.json", true);
        xhttp.send();
    }

    loadDoc();

    // SOCKETIO LOGIC

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