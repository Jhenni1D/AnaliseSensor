folder_name = ""

def set_folder_log(folder):
    global folder_name
    folder_name = folder


def write_log(msg, folder="", create=False):
    global folder_name
    if folder != "":
        folder_name = folder
    if create:
        folder_name=folder
        with open(f"./log-simulacao_{folder_name}.txt", "w", encoding="utf-8") as file:
            file.write(msg+"\n")
        return
    with open(f"./log-simulacao_{folder_name}.txt", "a", encoding="utf-8") as file:
        file.write(msg+"\n")