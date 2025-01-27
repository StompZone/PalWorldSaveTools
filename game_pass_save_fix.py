from internal_libs.import_libs import *
saves = []
save_extractor_done = threading.Event()
save_converter_done = threading.Event()
def get_save_game_pass(button):
    if os.path.exists("./saves"): shutil.rmtree("./saves")
    print("Fetching save from Game Pass...")
    button.destroy()
    progressbar = customtkinter.CTkProgressBar(master=window)
    progressbar.place(relx=0.5, rely=0.65, anchor="center")
    progressbar.set(0.0)
    threading.Thread(target=check_for_zip_files, daemon=True).start()
    threading.Thread(target=check_progress, args=(progressbar,), daemon=True).start()
def check_progress(progressbar):
    if save_extractor_done.is_set():
        progressbar.set(0.5)
        print("Attempting to convert the save files...")
        threading.Thread(target=convert_save_files, args=(progressbar,), daemon=True).start()
    else:
        window.after(1000, check_progress, progressbar)
def check_for_zip_files():
    if not find_zip_files("./"):
        print("Fetching zip files from local directory...")
        threading.Thread(target=run_save_extractor, daemon=True).start()
    else: process_zip_files()
def process_zip_files():
    if is_folder_empty("./saves"):
        zip_files = find_zip_files("./")
        print(zip_files)
        if (zip_files):
            unzip_file(zip_files[0], "./saves")
            save_extractor_done.set()
        else:
            print("No save files found on XGP please reinstall the game on XGP and try again")
            window.quit()
def convert_save_files(progressbar):
    saveFolders = list_folders_in_directory("./saves")
    if not saveFolders:
        print("No save files found")        
        return
    saveList = []
    for index, saveName in enumerate(saveFolders):        
        name = convert_sav_JSON(saveName)        
        if name: saveList.append(name)        
    update_combobox(saveList)
    progressbar.destroy()
    print("Choose a save to convert:")
def update_combobox(saveList):
    global saves
    saves = saveList
    if saves:
        combobox = customtkinter.CTkComboBox(master=window, values=saves, width=320, font=("Arial", 14))
        combobox.place(relx=0.5, rely=0.5, anchor="center")
        combobox.set("Choose a save to convert:")
        button = customtkinter.CTkButton(window, width=200, text="Convert Save", command=lambda: convert_JSON_sav(combobox.get()))
        button.place(relx=0.5, rely=0.8, anchor="center")
def run_save_extractor():
    python_exe = os.path.join("venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join("venv", "bin", "python")
    command = [python_exe, "./xgp_save_extract.py", "./"]
    try:
        subprocess.run(command, check=True)
        print("Command executed successfully")
        process_zip_files()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
def list_folders_in_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory {directory} created.")
        all_items = os.listdir(directory)
        return [item for item in all_items if os.path.isdir(os.path.join(directory, item))]
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return []
    except PermissionError:
        print(f"You don't have permission to access {directory}.")
        return []  
def find_key_in_json(file_path, target_key):
        print("Now loading the json...")
        try:
            with open(file_path, 'r') as f:
                parser = ijson.parse(f)
                value = None
                for prefix, event, val in parser:
                    if event == 'map_key' and val == target_key:
                        prefix, event, value = next(parser)
                        return value
                return value
        except FileNotFoundError:
            print(f"Error: File not found at path: {file_path}")
            return False
        except ijson.common.IncompleteJSONError:
            print(f"Error: Incomplete or invalid JSON in file: {file_path}")
            return False
        return False
def is_folder_empty(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory {directory} created.")
        all_items = os.listdir(directory)
        return len(all_items) == 0
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return False
    except PermissionError:
        print(f"You don't have permission to access {directory}.")
        return False
def find_zip_files(directory):
    zip_files = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".zip") and filename.startswith("palworld_"):
                zip_file_path = os.path.join(directory, filename)
                if is_valid_zip(zip_file_path):
                    zip_files.append(filename)
    else: print(f"Directory {directory} does not exist.")
    return zip_files
def is_valid_zip(zip_file_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref: zip_ref.testzip()
        return True
    except zipfile.BadZipFile: return False
def unzip_file(zip_file_path, extract_to_folder):
    print(f"Unzipping {zip_file_path} to {extract_to_folder}...")
    os.makedirs(extract_to_folder, exist_ok=True)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)
        print(f"Extracted all files to {extract_to_folder}")
def convert_sav_JSON(saveName):
    save_path = f"./saves/{saveName}/Level/01.sav"
    if not os.path.exists(save_path): return None
    python_exe = os.path.join("venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join("venv", "bin", "python")
    command = [python_exe, "./convert.py", save_path]
    try:
        subprocess.run(command, check=True)
        json_file_path = f"./saves/{saveName}/Level/01.sav.json"
        key_found = find_key_in_json(json_file_path, "player_name")
        return f"{key_found} - {saveName}"
    except subprocess.CalledProcessError:
        return None
def convert_JSON_sav(saveName):
    saveName = saveName[saveName.find("-") + 2:]
    print(saveName)
    print(f"Converting JSON file to .sav: {saveName}")
    python_exe = os.path.join("venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join("venv", "bin", "python")
    command = [python_exe, "./convert.py", f"./saves/{saveName}/Level/01.sav.json", "--output", f"./saves/{saveName}/Level.sav"]
    try:
        subprocess.run(command, check=True)
        print("Command executed successfully")
        os.remove(f"./saves/{saveName}/Level/01.sav.json")
        print(f"Deleted JSON file: ./saves/{saveName}/Level/01.sav.json")
        move_save_steam(saveName)
    except subprocess.CalledProcessError as e: print(f"Error executing command: {e}")
def move_save_steam(saveName):
    print("Moving save file to Steam and GamePassSave...")
    local_app_data_path = os.path.expandvars(r"%localappdata%\Pal\Saved\SaveGames")
    try:
        if not os.path.exists(local_app_data_path): raise FileNotFoundError(f"SaveGames directory does not exist at {local_app_data_path}")
        subdirs = [d for d in os.listdir(local_app_data_path) if os.path.isdir(os.path.join(local_app_data_path, d))]
        if not subdirs: raise FileNotFoundError(f"No subdirectories found in {local_app_data_path}")
        target_folder = os.path.join(local_app_data_path, subdirs[0])
        print(f"Detected Steam target folder: {target_folder}")
        source_folder = os.path.join("./saves", saveName)
        shutil.copytree(source_folder, target_folder + "/" + saveName, dirs_exist_ok=True)
        print(f"Save folder copied to Steam at {target_folder}")
        game_pass_save_path = os.path.join(os.getcwd(), "GamePassSave")
        if not os.path.exists(game_pass_save_path): os.makedirs(game_pass_save_path)
        shutil.copytree(source_folder, os.path.join(game_pass_save_path, saveName), dirs_exist_ok=True)
        print(f"Save folder copied to GamePassSave at {game_pass_save_path}")
        messagebox.showinfo("Success", "Your save is migrated to Steam and GamePassSave. Launch your game through your preferred platform.")
    except Exception as e:
        print(f"Error copying save folder: {e}")
        messagebox.showerror("Error", f"Failed to copy the save folder: {e}")
window = customtkinter.CTk()
window.title("PalWorld Save Converter")
window.iconbitmap("./internal_libs/pal.ico")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
app_width = 400
app_height = 200
x = (screen_width // 2) - (app_width // 2)
y = (screen_height // 2) - (app_height // 2)
window.geometry(f"{app_width}x{app_height}+{x}+{y}")
overlay_frame = customtkinter.CTkFrame(window, fg_color="transparent")
overlay_frame.place(relx=0.5, rely=0.1, anchor="n")
xgp = customtkinter.CTkImage(dark_image=Image.open("./internal_libs/xgp.png"), size=(80,40)) 
steam = customtkinter.CTkImage(dark_image=Image.open("./internal_libs/steam.png"), size=(30,30))
label = customtkinter.CTkLabel(overlay_frame , image=xgp, text="")
label.pack(side="left", padx=10)
label = customtkinter.CTkLabel(overlay_frame , image=steam, text="")
label.pack(side="left", padx=10)
buttonGetSaves = customtkinter.CTkButton(master=window, width=200, text="Get Saves", command=lambda: get_save_game_pass(buttonGetSaves))
buttonGetSaves.place(relx=0.5, rely=0.65, anchor="center")
window.mainloop()