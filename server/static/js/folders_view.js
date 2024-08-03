
console.log(all_folders)
let default_action = "/download/folder_name/start/end"

let modal_status_button_ok = document.getElementById("modal-delete-status-button-ok");
let items_names_elements = []
let content_folders = {}
let last_item_name = null;
let start_date_values = []
let end_date_values = []
let current_folder = "";

modal_status_button_ok.addEventListener("click", () => {
    window.location.reload(true);
});

for (i in all_folders) {
    items_names_elements.push(document.getElementById("item-name-" + i));
    let folder_name = items_names_elements[i].innerHTML;
    items_names_elements[i].addEventListener("click", ChangeFolder);

    document.getElementById("download-form-" + folder_name).onsubmit = evt => {
        let start_date_index = document.getElementById("start-date-" + current_folder).selectedIndex;
        let end_date_index = document.getElementById("end-date-" + current_folder).selectedIndex;
        let route = default_action
            .replace("folder_name", folder_name)
            .replace("start", start_date_index)
            .replace("end", end_date_index);
        evt.target.setAttribute("action", route);
        console.log(`Atualizou a rota para ${route}`);
        return true;
    };

    document.getElementById("start-date-" + folder_name).addEventListener('change', evt => {
        FilterSelectionItems(document.getElementById("end-date-" + folder_name), value => value > evt.target.selectedIndex)
    });

    document.getElementById("end-date-" + folder_name).addEventListener('change', evt => {
        FilterSelectionItems(document.getElementById("start-date-" + folder_name), value => value < evt.target.selectedIndex);
    });

    if (i == 0) {
        last_item_name = items_names_elements[i];
        current_folder = folder_name;
        end_date = document.getElementById("end-date-" + folder_name);
        start_date = document.getElementById("start-date-" + folder_name);
        FilterSelectionItems(end_date, value => value > start_date.selectedIndex);
        FilterSelectionItems(start_date, value => value < end_date.selectedIndex);
    }

    content_folders[items_names_elements[i].innerHTML] = { "element": document.getElementById("folder-info-root-" + i) };
}

function ChangeFolder(evt) {
    if (last_item_name !== null) {
        last_item_name.classList.remove("active");
        content_folders[last_item_name.innerHTML]["element"].setAttribute("style", "display: none;");
    }
    evt.target.classList.add("active");
    content_folders[evt.target.innerHTML]["element"].removeAttribute("style");
    last_item_name = evt.target;
    current_folder = evt.target.innerHTML;
}

function FilterSelectionItems(selectionToDisable, filterCondition) {
    let index_for = 0;
    for (opt of selectionToDisable) {
        opt.disabled = true;
        if (filterCondition(index_for++)) {
            opt.disabled = false;
        }
    }
}