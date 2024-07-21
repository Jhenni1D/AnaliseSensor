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

    let corrent_chart = new Chart(document.querySelector("#corrente"),
    {
        type: 'line',
        data: [],
        options:
        {
            scales: {
            }
        }
    });

  let graficos_images = {
    "SensorTensao": document.querySelector("#tensao"),
    "SensorTemp": document.querySelector("#temperatura"),
    "SensorRPM": document.querySelector("#rpm"),
    "eficiencia": document.querySelector("#eficiencia")
  }

  let charts_graphs = {
    "SensorTensao": CreateChart(graficos_images["SensorTensao"]),
    "SensorTemp": CreateChart(graficos_images["SensorTemp"]),
    "SensorRPM": CreateChart(graficos_images["SensorRPM"]),
    "eficiencia": CreateChart(graficos_images["eficiencia"])
  }

  let modal_img = document.querySelector("#modal_img")
  let modal_title = document.querySelector("#title_modal")

  console.log(dado)
  console.log(host)

  UpdateImages();
  RegisterActions();
  PlotGraphData();

  function CreateChart(canvas_element)
  {
    return new Chart(canvas_element,
                {
                    type: 'line',
                    data: [],
                    options:
                    {
                        scales: {
                        }
                    }
                });
  }

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
  }

  function ShowModalImage(event)
  {
    modal_img.src = event.srcElement.src;
    modal_title.innerHTML = event.srcElement.id.toUpperCase();
  }

  function PlotGraphData()
  {
    if(graph_data == undefined)
    {
        return;
    }

    let colors = ['blue', 'red', 'green', 'purple', 'orange']
    let index_color = 0;
    let corrent_graph_data =
    {
        datasets:
        [
        ]
    }
    try
    {
        for(graph in graph_data)
        {
            if(graph_data[graph].hasOwnProperty("values") && graficos_images.hasOwnProperty(graph))
            {
                let ctx = graficos_images[graph];
                let data =
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

                charts_graphs[graph].data = data;
                charts_graphs[graph].update('resize');
            }
        }
    }
    catch
    {
        console.log("Erro ao criar os gráficos gerais");
    }
  }

  function PlotCorrentGraph()
  {

    if(corrent_graph_data_server == null)
    {
        return;
    }

    let corrent_colors = ['blue', 'red', 'green']
    let index_color = 0;
    let index_corrent_color = 0;
    let corrent_graph_data =
    {
        datasets:
        [
            {
                    borderColor: corrent_colors[index_corrent_color++],
                    label: "SensorA / Tempo",
                    data: corrent_graph_data_server["SensorA"]
            },
            {
                    borderColor: corrent_colors[index_corrent_color++],
                    label: "SensorB / Tempo",
                    data: corrent_graph_data_server["SensorB"]
            },
            {
                    borderColor: corrent_colors[index_corrent_color++],
                    label: "SensorC / Tempo",
                    data: corrent_graph_data_server["SensorC"]
            }
        ],
        labels: corrent_graph_data_server["dates"]
    }
    if(corrent_chart.data.length === 0)
    {
        corrent_chart.data = corrent_graph_data;
    }
    corrent_chart.update();
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
            if(sensor == "SensorA" || sensor == "SensorB" || sensor == "SensorC")
            {
                continue;
            }
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

    function updateGraphs(handlerResult, link)
    {
      let xhttp = new XMLHttpRequest();
      xhttp.onload = handlerResult;
      xhttp.open("GET", link, true);
      xhttp.send();
    }

    function updateSingularGraphs()
    {
      handlerResult = function()
      {
        var sensors_data = JSON.parse(this.responseText);
        graph_data = FormatSensorsData(sensors_data);
        setTimeout(PlotGraphData, 1000);
        setTimeout(updateSingularGraphs, 2000);
      }

      updateGraphs(handlerResult, `https://simulacao-femm-default-rtdb.firebaseio.com/medicoes/Pastas/${folder_name}/Sensores/.json`);
    }

    function updateCorrentGraphs()
    {
        handlerResult = function()
      {
        corrent_graph_data_server = JSON.parse(this.responseText);
        setTimeout(PlotCorrentGraph, 1000);
        setTimeout(updateCorrentGraphs, 2000);
      }

      updateGraphs(handlerResult, `http://localhost:8080/get_corrent_values`);
    }

    updateSingularGraphs();
    //updateCorrentGraphs();

    // SOCKETIO LOGIC

  let socket = io();

  socket.on('connect', function () {
    console.log('Connected!');
    socket.emit('progress_test');
    socket.emit('corrent_data_updater')
  });


  socket.on('update_image', function (data_updated) {
    dado = data_updated;
    UpdateImages();
  });


  socket.on('progress_value', function (prog_value) {
    progresso.style["width"] = `${prog_value}%`;
    progresso.innerHTML = `${prog_value}%`;
  });


  socket.on('corrent_data_updater', function(data){

    if(corrent_graph_data_server === null)
    {
        corrent_graph_data_server = data;
        PlotCorrentGraph();
        return;
    }
    let need_update = corrent_graph_data_server['dates'].slice(-1)[0] !== data['dates'].slice(-1)[0]
    if(need_update)
    {
        for(key in data)
        {
            corrent_graph_data_server[key].push(data[key].slice(-1)[0]);
        }
        PlotCorrentGraph();
    }
  });


  socket.on('disconnect', function () {
    console.log('Disconnected!');
  });
});