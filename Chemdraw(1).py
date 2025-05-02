import requests
from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- Theme Setup ---
theme_mode = "dark"

themes = {
    "dark": {
        "bg": "#1e1e2f",
        "fg": "white",
        "button_bg": "#3c3f58",
        "active_bg": "#50557a",
        "entry_bg": "#2a2a3d"
    },
    "light": {
        "bg": "#f0f0f0",
        "fg": "black",
        "button_bg": "#e0e0e0",
        "active_bg": "#d0d0d0",
        "entry_bg": "white"
    }
}

# --- Backend Functions ---
def iupac_to_smiles(iupac_name):
    url = f"https://opsin.ch.cam.ac.uk/opsin/{iupac_name}.smi"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
    except requests.RequestException as e:
        print(f"Network error: {e}")
    return None

def smiles_to_structure(smiles, image_path="structure.png"):
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        Draw.MolToFile(mol, image_path, size=(400, 400))
        return image_path
    else:
        return None

# --- App Functions ---
def generate_structure():
    global current_image_path
    iupac_name = entry.get().strip()
    if not iupac_name:
        messagebox.showwarning("Input Error", "Please enter an IUPAC name.")
        return

    smiles = iupac_to_smiles(iupac_name)
    if smiles:
        image_path = smiles_to_structure(smiles)
        if image_path:
            img = Image.open(image_path)
            img = img.resize((350, 350))
            img = ImageTk.PhotoImage(img)

            image_label.config(image=img)
            image_label.image = img
            smiles_var.set(smiles)
            current_image_path = image_path
            save_button.config(state=tk.NORMAL)
            copy_smiles_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "Failed to generate structure from SMILES.")
            clear_output()
    else:
        messagebox.showerror("Error", "Conversion failed. Please check the IUPAC name.")
        clear_output()

def clear_output():
    image_label.config(image='')
    image_label.image = None
    smiles_var.set("")
    save_button.config(state=tk.DISABLED)
    copy_smiles_button.config(state=tk.DISABLED)

def save_structure():
    if current_image_path:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            img = Image.open(current_image_path)
            img.save(file_path)
            messagebox.showinfo("Saved", f"Structure saved at:\n{file_path}")

def copy_smiles():
    root.clipboard_clear()
    root.clipboard_append(smiles_var.get())
    messagebox.showinfo("Copied", "SMILES string copied to clipboard!")

def toggle_theme():
    global theme_mode
    theme_mode = "light" if theme_mode == "dark" else "dark"
    t = themes[theme_mode]

    root.configure(bg=t["bg"])
    canvas.configure(bg=t["bg"])
    scrollable_frame.configure(bg=t["bg"])
    frame.configure(bg=t["bg"])
    title.configure(bg=t["bg"], fg=t["fg"])
    image_label.configure(bg=t["bg"])
    smiles_label.configure(readonlybackground=t["entry_bg"], fg=t["fg"])
    entry.configure(bg=t["entry_bg"], fg=t["fg"], insertbackground=t["fg"])

    buttons = [convert_button, save_button, copy_smiles_button, toggle_theme_button]
    for btn in buttons:
        btn.configure(bg=t["button_bg"], fg=t["fg"], activebackground=t["active_bg"])

# --- Main App ---
root = tk.Tk()
root.title("IUPAC to Structure Converter")
root.geometry("520x750")
root.configure(bg=themes[theme_mode]["bg"])
root.resizable(True, True)

# --- Style ---
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 12), padding=8)
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TEntry", font=("Segoe UI", 12))

# --- Scrollable Canvas Setup ---
container = tk.Frame(root)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, bg=themes[theme_mode]["bg"])
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg=themes[theme_mode]["bg"])

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --- UI Layout Inside Scrollable Frame ---
frame = tk.Frame(scrollable_frame, bg=themes[theme_mode]["bg"])
frame.pack(pady=20, padx=50)  # Center with padding

title = tk.Label(frame, text="IUPAC Name to Structure", font=("Segoe UI", 20, "bold"),
                 bg=themes[theme_mode]["bg"], fg=themes[theme_mode]["fg"])
title.grid(row=0, column=0, columnspan=2, pady=10)

entry = tk.Entry(frame, width=35, font=("Segoe UI", 14),
                 bg=themes[theme_mode]["entry_bg"], fg=themes[theme_mode]["fg"],
                 insertbackground=themes[theme_mode]["fg"])
entry.grid(row=1, column=0, padx=10, pady=10)

convert_button = tk.Button(frame, text="Generate Structure", command=generate_structure,
                           bg=themes[theme_mode]["button_bg"], fg=themes[theme_mode]["fg"],
                           font=("Segoe UI", 12), activebackground=themes[theme_mode]["active_bg"])
convert_button.grid(row=1, column=1, padx=10)

image_label = tk.Label(scrollable_frame, bg=themes[theme_mode]["bg"])
image_label.pack(pady=20)

smiles_var = tk.StringVar()
smiles_label = tk.Entry(scrollable_frame, textvariable=smiles_var, font=("Segoe UI", 12), width=50,
                        state="readonly", justify='center', readonlybackground=themes[theme_mode]["entry_bg"],
                        fg=themes[theme_mode]["fg"])
smiles_label.pack(pady=10)

copy_smiles_button = tk.Button(scrollable_frame, text="Copy SMILES", command=copy_smiles,
                               font=("Segoe UI", 12), bg=themes[theme_mode]["button_bg"],
                               fg=themes[theme_mode]["fg"], activebackground=themes[theme_mode]["active_bg"])
copy_smiles_button.pack(pady=10)
copy_smiles_button.config(state=tk.DISABLED)

save_button = tk.Button(scrollable_frame, text="Save Structure", command=save_structure,
                        font=("Segoe UI", 12), bg=themes[theme_mode]["button_bg"],
                        fg=themes[theme_mode]["fg"], activebackground=themes[theme_mode]["active_bg"])
save_button.pack(pady=10)
save_button.config(state=tk.DISABLED)

toggle_theme_button = tk.Button(scrollable_frame, text="Toggle Dark/Light Mode", command=toggle_theme,
                                font=("Segoe UI", 12), bg=themes[theme_mode]["button_bg"],
                                fg=themes[theme_mode]["fg"], activebackground=themes[theme_mode]["active_bg"])
toggle_theme_button.pack(pady=10)

# --- State Variables ---
current_image_path = None

# --- Run App ---
root.mainloop()
