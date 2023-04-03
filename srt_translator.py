import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from googletrans import Translator
import googletrans
import os
import re
import srt
import threading


###################################### FUNCTIONS ######################################

def main_execute():
    if option.get() == 1:
        filepath = txt_file.get()
        translate(get_root_path(filepath), get_filename(filepath))
    elif option.get() == 2:
        folderpath = txt_folder.get()
        for _, _, file_names in os.walk(folderpath):
            for filename in file_names:
                translate(folderpath, filename)


def translate(root: str, filename: str):
    if filename.endswith(".srt"):
        update_log(f"[Translating...] {filename}")
        filename = filename.split(".srt")[0]

        convert_srt_to_txt(f"{root}/{filename}.srt")
        translate_txt(f"{root}/{filename}.txt")
        update_log(f"[Finished] {filename}.srt")
    else:
        update_log(f"[Error: not an SRT file] {filename}")


def convert_srt_to_txt(srtpath: str):
    with open(srtpath, "r", encoding="utf-8") as srtfile:
        buffer = open("buffer.txt", "w", encoding="utf-8")
        for sub in srt.parse(srtfile):
            line = sub.content
            line = line.replace("\n", " ")
            line = re.sub(r"\.[\s]", ".\n", line)
            line = re.sub(r"\.$", ".\n", line)
            line = line.replace("!", "!\n")
            line = line.replace("?", "?\n")
            line = line.replace("]", "]\n")
            buffer.write(line)
        buffer.close()


def translate_txt(dest_path: str):
    translator = Translator()
    with open("buffer.txt", "r", encoding="utf-8") as file:
        txt_file = open(dest_path, "w", encoding="utf-8")
        c = 1
        for line in file:
            update_progress(f"Translating line Nº{c}.")
            try:
                line = line.strip()
                trans_line = translator.translate(line, dest=get_selected_language()).text
                txt_file.write(line + '\n')
                txt_file.write(trans_line + '\n\n')
            except:
                txt_file.write(line + '\n')
                txt_file.write("[ERROR] It occurred an error while translating this line." + '\n\n')
                update_log(f"Translation error on line {c}")
                continue
            c += 1
        update_progress(f"All {c} lines translated.")
        txt_file.close()

    os.remove("buffer.txt")


def get_root_path(path: str):
    split_path = path.split("/")
    root = "".join(f"{s}/" for s in split_path[0:-1])
    return root


def get_filename(path: str):
    split_path = path.split("/")
    return split_path[-1]


def update_log(log: str):
    lbl_log.config(text=log)


def update_progress(log: str):
    lbl_progress.config(text=log)


def set_execution_mode():
    if option.get() == 1:
        txt_file.config(state="normal")
        btn_file_explorer.config(state="normal")
        txt_folder.delete(0, 'end')
        txt_folder.config(state="disabled")
        btn_folder_explorer.config(state="disabled")
    elif option.get() == 2:
        txt_file.delete(0, 'end')
        txt_file.config(state="disabled")
        btn_file_explorer.config(state="disabled")
        txt_folder.config(state="normal")
        btn_folder_explorer.config(state="normal")


def explore_file():
    txt_file.delete(0, 'end')
    tk.Tk().withdraw()
    filepath = askopenfilename()
    txt_file.insert(0, filepath)


def explore_folder():
    txt_folder.delete(0, 'end')
    tk.Tk().withdraw()
    dirpath = askdirectory()
    txt_folder.insert(0, dirpath)


def get_selected_language():
    languages = googletrans.LANGUAGES
    return list(languages.keys())[list(languages.values()).index(cmb_lang.get())]


def program_exit():
    window.quit()
    window.destroy()


###################################### USER INTERFACE ######################################
FONT = ("", "9", "bold")
LANG = [v for v in googletrans.LANGUAGES.values()]
KO_index = LANG.index("korean")


window = tk.Tk()
window.title("STR Translator")
window.resizable(False, False)

if os.name == "nt":
    window.geometry("300x380")
    try:
        window.iconbitmap("icon.ico")
    except tk.TclError:
        pass
else:
    window.geometry("360x430")


### FRAME 1 - MODE SELECTION ###
frame1 = tk.Frame(window)
frame1.grid(row=0, column=0)

lbl_rdobtn = tk.Label(frame1, text="Execution mode: ")
lbl_rdobtn.grid(row=0, column=0, padx=10, pady=10)

option = tk.IntVar()
rdo_file = tk.Radiobutton(frame1, text="File", variable=option, value=1, command=set_execution_mode)
rdo_folder = tk.Radiobutton(frame1, text="Folder", variable=option, value=2, command=set_execution_mode)
rdo_file.grid(row=0, column=1, padx=10, pady=10)
rdo_folder.grid(row=0, column=2, padx=10, pady=10)
rdo_file.select()


### FRAME 2 - FILE SELECTION ###
frame2 = tk.Frame(window)
frame2.grid(row=1, column=0)

lbl_section2 = tk.Label(frame2, text="File/s selection", font=FONT)
lbl_section2.grid(row=0, columnspan=2, padx=5, pady=(10, 0))

lbl_file = tk.Label(frame2, text="File path: ")
lbl_file.grid(row=1, column=0, padx=5, pady=5, sticky="e")
txt_file = tk.Entry(frame2, width=25, state="normal")
txt_file.grid(row=1, column=1, padx=5, pady=5)

lbl_folder = tk.Label(frame2, text="Folder path: ")
lbl_folder.grid(row=2, column=0, padx=5, pady=5, sticky="e")
txt_folder = tk.Entry(frame2, width=25, state="disabled")
txt_folder.grid(row=2, column=1, padx=5, pady=5)

#· EXPLORER BTN IMG ·#
message = ""
try:
    img_explorer = PhotoImage(file='explorer.png')
except tk.TclError:
    img_explorer = None
    message = "File missing: explorer.png"

img_label = tk.Label(image=img_explorer)
btn_file_explorer = tk.Button(frame2, image=img_explorer, command=explore_file, borderwidth=0, state="normal")
btn_file_explorer.grid(row=1, column=3, padx=5, pady=5)

btn_folder_explorer = tk.Button(frame2, image=img_explorer, command=explore_folder, borderwidth=0, state="disabled")
btn_folder_explorer.grid(row=2, column=3, padx=5, pady=5)


### FRAME 3 - LANGUAGE ###
frame3 = tk.Frame(window)
frame3.grid(row=2, column=0)

lbl_section3 = tk.Label(frame3, text="Language selection", font=FONT)
lbl_section3.grid(row=0, columnspan=2, padx=5, pady=(15, 0))
lbl_lang = tk.Label(frame3, text="Destination: ", width=12)
lbl_lang.grid(row=1, column=0, padx=5, pady=5)
cmb_lang = ttk.Combobox(frame3, values=LANG, width=20)
cmb_lang.current(KO_index)
cmb_lang.grid(row=1, column=1, padx=5, pady=5)


### SECTION 4 - LOGGER ###
lbl_section3 = tk.Label(window, text="Progress Log", font=FONT)
lbl_section3.grid(row=4, columnspan=2, padx=5, pady=(20, 5))
lbl_log = tk.Label(window, text="", width=35, bg="#FFFFFF", anchor="w")
lbl_log.grid(row=5, column=0, padx=10, pady=(0, 5))
lbl_progress = tk.Label(window, text="", width=35, bg="#FFFFFF", anchor="w")
lbl_progress.grid(row=6, column=0, padx=10, pady=(0, 5))


### SECTION 5 - SUBMIT ###
btn_submit = tk.Button(window, text="TRANSLATE", width=35, bg="#FFFFFF", command= lambda : threading.Thread(target=main_execute).start() )
btn_submit.grid(row=7, columnspan=2, padx=10, pady=25)

update_log(message)

## MAIN LOOP ##
window.protocol("WM_DELETE_WINDOW", program_exit)
window.mainloop()
