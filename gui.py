import tkinter as tk
from tkinter import scrolledtext
import subprocess

def run_install():
    output_text.delete(1.0, tk.END)
    proc = subprocess.Popen(
        ["pro-drivers", "--list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in proc.stdout:
        output_text.insert(tk.END, line)
        output_text.see(tk.END)
    proc.wait()

root = tk.Tk()
root.title("MSI Driver Installer GUI")

btn_run = tk.Button(root, text="List Drivers", command=run_install)
btn_run.pack(pady=10)

output_text = scrolledtext.ScrolledText(root, width=80, height=20)
output_text.pack()

root.mainloop()
