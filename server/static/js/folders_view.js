
console.log(all_folders)

let items_names_elements = []
let content_folders = {}
let last_item_name = null;
for (i in all_folders) {
    items_names_elements.push(document.getElementById("item-name-" + i));
    items_names_elements[i].addEventListener("click", evt => {
        if (last_item_name !== null) {
            last_item_name.classList.remove("active");
            content_folders[last_item_name.innerHTML].setAttribute("style", "display: none;");
        }
        evt.target.classList.add("active");
        content_folders[evt.target.innerHTML].removeAttribute("style");
        last_item_name = evt.target;
    });
    if (i == 0) {
        last_item_name = items_names_elements[i];
    }
    content_folders[items_names_elements[i].innerHTML] = document.getElementById("folder-info-root-" + i)
}
console.log(content_folders);