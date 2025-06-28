import os, tkinter as tk, datetime, shutil, time
from datetime import datetime as dt
from os import system
from tkinter import messagebox, PhotoImage

root = tk.Tk()
min_dimensions = root.minsize(150, 150)
root.configure(bg='black')

root.title('LothianGaming Save Backup Tool')
root.geometry(min_dimensions)
year = dt.now().year
month = dt.now().month
day = dt.now().day
main_dir = os.path.expanduser("~")
copy_to_dir = f'{main_dir}\AppData\LocalLow\semiwork\Repo\LothianGaming SaveBackup Tool'

def repo_backup():
    delete_previous_backup = shutil.rmtree(copy_to_dir)
    parent_save_dir = f'{main_dir}\AppData\LocalLow\semiwork\Repo\saves'
    for dir in parent_save_dir:
        try:
            delete_previous_backup
            shutil.copytree(parent_save_dir, copy_to_dir)
        except:
            if dir == None:
                pass

labelone = tk.Label(root, text = f"All saves created on {year}/0{month}/{day} have been backed up successfully. You will find them in {copy_to_dir}. You may close this window when ready.", font=("Arial Bold", 12))

repo_backup()
labelone.pack()
root.mainloop()