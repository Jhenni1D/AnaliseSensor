$(document).ready(function () {
  let progress_simulation_element = document.querySelector("#progress");

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

  let corrent_chart = new Chart(document.querySelector("#corrente"),
    {
      type: 'line',
      data: [],
      options:
      {
        scales: {
          x: {
            min: minSliderValue,
            max: maxSliderValue
          }
        }
      }
    });

  slider.noUiSlider.on('update', function (value) {
    corrent_chart.options.scales.x.min = parseInt(value[0]);
    corrent_chart.options.scales.x.max = parseInt(value[1]);
    corrent_chart.update();
  });

  let elements_graph = {
    "SensorTensao": document.querySelector("#tensao"),
    "SensorTemp": document.querySelector("#temperatura"),
    "SensorRPM": document.querySelector("#rpm"),
    "eficiencia": document.querySelector("#eficiencia")
  }

  let charts_graphs = {
    "SensorTensao": CreateChart(elements_graph["SensorTensao"]),
    "SensorTemp": CreateChart(elements_graph["SensorTemp"]),
    "SensorRPM": CreateChart(elements_graph["SensorRPM"]),
    "eficiencia": CreateChart(elements_graph["eficiencia"])
  }

  let modal_img = document.querySelector("#modal_img")
  let modal_title = document.querySelector("#title_modal")

  UpdateImages();
  RegisterActions();
  PlotGraphData();

  function CreateChart(canvas_element) {
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

  function UpdateImages() {
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

  function RegisterActions() {
    for (img in m_images) {
      m_images[img].addEventListener('click', ShowModalImage);
    }

    for (img in t_images) {
      t_images[img].addEventListener('click', ShowModalImage);
    }
  }

  function ShowModalImage(event) {
    modal_img.src = event.srcElement.src;
    modal_title.innerHTML = event.srcElement.id.toUpperCase();
  }

  function PlotGraphData() {
    if (graph_data == undefined) {
      return;
    }

    let colors = ['blue', 'red', 'green', 'purple', 'orange']
    let index_color = 0;
    try {
      for (graph in graph_data) {

        if (graph.includes("Sensor") === false || graph.includes("SensorA") || graph.includes("SensorB") || graph.includes("SensorC")) {
          continue;
        }

        if (charts_graphs[graph].data.length !== 0) {
          charts_graphs[graph].update();
          continue;
        }

        let data =
        {
          datasets:
            [
              {
                borderColor: colors[index_color++],
                label: `${graph.toLocaleUpperCase()} / Tempo`,
                data: graph_data[graph]
              }
            ],
          labels: graph_data["data_hora"]
        }

        if (charts_graphs[graph].data.length === 0) {
          charts_graphs[graph].data = data;
        }
        charts_graphs[graph].update();
      }
    }
    catch (err) {
      console.log("Erro ao criar os gráficos gerais");
      console.log(err);
    }
  }

  function PlotCorrentGraph() {

    if (graph_data == null) {
      return;
    }

    if (corrent_chart.data.length !== 0) {
      corrent_chart.options.scales.x.min = currentMinSliderValue;
      corrent_chart.options.scales.x.max = currentMaxSliderValue;
      corrent_chart.update();
      return;
    }

    let corrent_colors = ['blue', 'red', 'green']
    let index_corrent_color = 0;
    let corrent_graph_data =
    {
      datasets:
        [
          {
            borderColor: corrent_colors[index_corrent_color++],
            label: "SensorA / Tempo",
            data: graph_data["SensorA"]
          },
          {
            borderColor: corrent_colors[index_corrent_color++],
            label: "SensorB / Tempo",
            data: graph_data["SensorB"]
          },
          {
            borderColor: corrent_colors[index_corrent_color++],
            label: "SensorC / Tempo",
            data: graph_data["SensorC"]
          }
        ],
      labels: graph_data["data_hora"]
    }
    corrent_chart.data = corrent_graph_data;
    corrent_chart.update();
  }


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
    progress_simulation_element.style["width"] = `${prog_value}%`;
    progress_simulation_element.innerHTML = `${prog_value}%`;
  });


  socket.on('corrent_data_updater', function (data) {
    graph_data_cache = data;
    if (graph_data === null) {
      graph_data = data;
      PlotCorrentGraph();
      PlotGraphData();
      maxSliderValue = data['data_hora'].length - 1;
      UpdateSlider();
      return;
    }

    let need_update = graph_data['data_hora'].slice(-1)[0] !== data['data_hora'].slice(-1)[0]
    //console.log(graph_data['data_hora']);

    if (need_update) {
      for (key in data) {
        graph_data[key].push(data[key].slice(-1)[0]);
      }
      PlotCorrentGraph();
      PlotGraphData();
      maxSliderValue = graph_data_cache['data_hora'].length - 1;
      UpdateSlider();
    }
  });


  socket.on('disconnect', function () {
    console.log('Disconnected!');
  });
});