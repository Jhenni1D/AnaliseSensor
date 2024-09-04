$(document).ready(function () {
  var last_reset_status = false;
  let progress_simulation_element = document.querySelector("#progress");
  let confirm_reset_button = document.querySelector("#confirm-reset");
  let continue_simulation_button = document.querySelector("#continue-simulation");
  let status_reset_simulation_timeout = null;
  let status_vm_timeout = null;
  let status_vm_element = document.getElementById("status-vm");
  const getId = id => document.getElementById(id);

  badgeButtons = {
    "emm": { "button": getId("emm"), "badge": getId("emm").getElementsByTagName("span")[0] },
    "ms": { "button": getId("ms"), "badge": getId("ms").getElementsByTagName("span")[0] },
    "ts": { "button": getId("ts"), "badge": getId("ts").getElementsByTagName("span")[0] },
  }

  for (item in badgeButtons) {
    badgeButtons[item]["button"].addEventListener("click", ResetBadge);
  }

  getId("log-button").addEventListener("click", evt => {
    SetShowLogBadge(false);
  });

  continue_simulation_button.addEventListener("click", DisableCancelButton);

  confirm_reset_button.addEventListener('click', SendCancelRequest);

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
            max: maxSliderValue,
            title: {
              display: true,
              text: 'DATETIME' // Your y-axis title
            }
          },
          y:
          {
            title: {
              display: true,
              text: 'CURRENT' // Your y-axis title
            }
          }
        }
      }
    });

  slider.noUiSlider.on('update', function (value) {
    corrent_chart.options.scales.x.min = parseInt(value[0]);
    corrent_chart.options.scales.x.max = parseInt(value[1]);
    corrent_chart.update();
    for (graph in graph_data) {
      if (graph.includes("Sensor") === false || graph.includes("SensorA") || graph.includes("SensorB") || graph.includes("SensorC")) {
        continue;
      }

      if (charts_graphs[graph].data.length !== 0) {
        charts_graphs[graph].options.scales.x.min = currentMinSliderValue;
        charts_graphs[graph].options.scales.x.max = currentMaxSliderValue;
        charts_graphs[graph].update();
        continue;
      }
    }
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

  let graph_title = {
    "SensorTensao": "Tension",
    "SensorTemp": "Temperature",
    "SensorRPM": "RPM",
    "eficiencia": "Efficiency"
  }

  let modal_img = document.querySelector("#modal_img")
  let modal_title = document.querySelector("#title_modal")

  UpdateImages();
  RegisterActions();
  PlotGraphData();

  function ResetBadge(evt) {
    if (IsAccordionCollapsed(evt.target.id) == false) {
      span_element = evt.target.getElementsByTagName("span")[0];
      span_element.classList.remove("show");
      span_element.classList.add("hide");
      span_element.innerHTML = "0";
    }
  }

  function IsAccordionCollapsed(key) {
    return badgeButtons[key]["button"].getAttribute("aria-expanded") === "false";
  }

  function UpdateBadge(key) {
    let isCollapsed = IsAccordionCollapsed(key);
    if (isCollapsed) {
      badgeButtons[key]["badge"].innerHTML = parseInt(badgeButtons[key]["badge"].innerHTML) + 1;
      badgeButtons[key]["badge"].classList.remove("hide");
      badgeButtons[key]["badge"].classList.add("show");
    }
  }

  function SetShowLogBadge(show) {
    if (show) {
      getId("log-button").getElementsByTagName("span")[0].classList.remove("hide");
      getId("log-button").getElementsByTagName("span")[0].classList.add("show");
      return;
    }
    getId("log-button").getElementsByTagName("span")[0].classList.remove("show");
    getId("log-button").getElementsByTagName("span")[0].classList.add("hide");
  }

  function CreateChart(canvas_element) {
    return new Chart(canvas_element,
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
  }

  function UpdateImages() {
    if (dado.length !== 0) {
      for (d of dado) {
        let img_name = d["name"];
        let src_img = d["img"]
        let img_element = img_name in m_images ? m_images[img_name] : img_name in t_images ? t_images[img_name] : null;
        let key = img_name in m_images ? "ms" : img_name in t_images ? "ts" : null;
        if (img_element !== null && img_element.src.includes(src_img) == false) {
          img_element.src = src_img;
          img_element.classList.remove('placeholder');
          if (key !== null) {
            UpdateBadge(key);
            IsAccordionCollapsed(key);
          }
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
          charts_graphs[graph].options.scales.x.min = currentMinSliderValue;
          charts_graphs[graph].options.scales.x.max = (currentMaxSliderValue == (maxSliderValue - 1)) ? maxSliderValue : currentMaxSliderValue;;
          charts_graphs[graph].update();
          continue;
        }

        let data =
        {
          datasets:
            [
              {
                borderColor: colors[index_color++],
                label: `${graph_title[graph].toLocaleUpperCase()} / DATETIME`,
                data: graph_data[graph]
              }
            ],
          labels: graph_data["data_hora"]
        }
        charts_graphs[graph].data = data;
        charts_graphs[graph].update();
        charts_graphs[graph].options.scales.y.title = {
          display: true,
          text: graph_title[graph].toLocaleUpperCase()
        }
        charts_graphs[graph].options.scales.x.title = {
          display: true,
          text: "DATETIME"
        }
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
      corrent_chart.options.scales.x.max = (currentMaxSliderValue == (maxSliderValue - 1)) ? maxSliderValue : currentMaxSliderValue;;
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
            label: "CURRENT A / DATETIME",
            data: graph_data["SensorA"]
          },
          {
            borderColor: corrent_colors[index_corrent_color++],
            label: "CURRENT B / DATETIME",
            data: graph_data["SensorB"]
          },
          {
            borderColor: corrent_colors[index_corrent_color++],
            label: "CURRENT C / DATETIME",
            data: graph_data["SensorC"]
          }
        ],
      labels: graph_data["data_hora"]
    }
    corrent_chart.data = corrent_graph_data;
    corrent_chart.update();
  }

  function SendCancelRequest() {
    SetDefaultStatusResetSimulation();
    last_reset_status = false;
    status_reset_simulation_timeout = setTimeout(SetStatusResetSimulation, 6000);
    socket.emit("cancel_simulation_response", true);
  }

  function EnableCancelButton() {
      getId("error-container").classList.remove("visually-hidden");
  }

  function DisableCancelButton() {
    last_reset_status = false;
    status_reset_simulation_timeout = setTimeout(SetStatusContinueSimulation, 6000);
    socket.emit("cancel_simulation_response", false);
    //getId("error-container").classList.add("visually-hidden"); aa
  }

  function SetStatusVM() {
    status_vm_element.classList.remove("text-success");
    status_vm_element.classList.add("text-danger");
  }

  function SetStatusResetSimulation() {
    let statusMessage = `${(last_reset_status ? "success" : "fail")}-message`;
    let statusMessage2 = `${(last_reset_status ? "success" : "fail")}-continue-message`;
    HiddenElement(getId("loading-icon"));
    HiddenElement(getId("loading-cancel-continue-icon"));
    ShowElement(getId(statusMessage));
    ShowElement(getId(statusMessage2));

    getId("modal-reset-confirm-title").innerHTML = "RESET STATUS"
    getId("modal-reset-confirm-button-ok").removeAttribute("disabled");
    getId("modal-cancel-continue-confirm-button-ok").removeAttribute("disabled");

    if (last_reset_status) {
      progress_simulation_element.classList.remove("bg-danger");
    }
  }

  function SetStatusContinueSimulation() {
    let statusMessage = `${(last_reset_status ? "success" : "fail")}-continue-message`;
    HiddenElement(getId("loading-cancel-continue-icon"));
    ShowElement(getId(statusMessage));

    getId("modal-reset-confirm-title").innerHTML = "CONTINUE SIMULATION STATUS"
    getId("modal-cancel-continue-confirm-button-ok").removeAttribute("disabled");

    if (last_reset_status) {
      progress_simulation_element.classList.remove("bg-danger");
    }
  }


  function SetDefaultStatusResetSimulation() {
    ShowElement(getId("loading-icon"));
    HiddenElement(getId("success-message"));
    HiddenElement(getId("fail-message"));

    getId("modal-reset-confirm-title").innerHTML = "RESETING..."
    getId("modal-reset-confirm-button-ok").setAttribute("disabled", "");
  }

  function ShowElement(element) {
    if (element === null) {
      console.log("ShowElement - Element is null!");
      return;
    }
    element.classList.remove("visually-hidden");
    element.classList.add("show");
  }

  function HiddenElement(element) {
    if (element === null) {
      console.log("HiddenElement - Element is null!");
      return;
    }
    element.classList.add("visually-hidden");
    element.classList.remove("show");
  }


  let socket = io();

  socket.on('connect', function () {
    console.log('Connected!');
    //socket.emit('progress_test');
    socket.emit('corrent_data_updater', folder_name)
  });

  socket.on('request_status_vm', () => {
    clearTimeout(status_vm_timeout);
    status_vm_element.classList.remove("text-danger");
    status_vm_element.classList.add("text-success");
    status_vm_timeout = setTimeout(SetStatusVM, 4000);
  });

  socket.on('update_image', function (data_updated) {
    dado = data_updated;
    UpdateImages();
  });

  socket.on('progress_value', function (prog_value) {
    progress_simulation_element.style["width"] = `${prog_value}% `;
    progress_simulation_element.innerHTML = `${prog_value}% `;
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

    if (need_update) {
      for (key in data) {
        graph_data[key].push(data[key].slice(-1)[0]);
      }
      PlotCorrentGraph();
      PlotGraphData();
      maxSliderValue = graph_data_cache['data_hora'].length - 1;
      UpdateSlider();
      UpdateBadge("emm");
    }
  });

  socket.on('log_simulation', log_text => {
    if (getId("log-text").innerHTML !== log_text && getId("log-button").getAttribute("aria-expanded") === "false") {
      SetShowLogBadge(true);
    }
    getId("log-text").innerHTML = log_text;
  });

  socket.on('enable_cancel_button', () => {
    EnableCancelButton();
  });

  getId("modal-reset-confirm-button-ok").addEventListener('click', () => {
    if (last_reset_status) {
      setTimeout(() => {
        getId("error-container").classList.add('visually-hidden');
      }, 1000);
    }
  });

  getId("modal-cancel-continue-confirm-button-ok").addEventListener('click', () => {
    if (last_reset_status) {
      setTimeout(() => {
        getId("error-container").classList.add('visually-hidden');
      }, 1000);
    }
  });

  socket.on('cancel_simulation_received_response', () => {
    clearTimeout(status_reset_simulation_timeout);
    last_reset_status = true;
    SetStatusResetSimulation();
    SetStatusContinueSimulation();
  });

  socket.on('completed_simulation', () => {
    console.log("Simulação foi completada!");
    window.location.reload(true);
  });

  socket.on('disconnect', function () {
    console.log('Disconnected!');
  });
});