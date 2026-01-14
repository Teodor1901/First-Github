import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import re
import os

FISIER = "taskuri.txt"

# Data minimă permisă
DATA_MINIMA = datetime(2026, 1, 1)

# 1. Permitem cifre și simboluri la tastare
def valideaza_caractere_data(char):
    return re.match(r'[0-9\.,\-/]', char) is not None

# 2. Verifică data, uniformizează formatul și verifică pragul de 2026
def proceseaza_si_valideaza_data(data_text):
    if data_text in ["Data", ""]: 
        return False, data_text, "Te rugăm să introduci o dată."
    
    # Uniformizăm separatorii
    data_uniformizata = data_text.replace('/', '.').replace(',', '.').replace('-', '.')
    
    try:
        data_obiect = datetime.strptime(data_uniformizata, '%d.%m.%Y')
        
        # VERIFICARE: Să nu fie înainte de 01.01.2026
        if data_obiect < DATA_MINIMA:
            return False, data_text, "Anul este prea vechi! Introdu o dată începând cu 01.01.2026."
            
        return True, data_uniformizata, ""
    except ValueError:
        return False, data_text, "Format invalid! Folosește Zi.Lună.An (ex: 15.01.2026)."

#  LOGICĂ PLACEHOLDERS
def setup_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg='grey')
    
    def on_click(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg='black')
            
    def on_out(event):
        if entry.get() == '':
            entry.insert(0, text)
            entry.config(fg='grey')
            
    entry.bind('<FocusIn>', on_click)
    entry.bind('<FocusOut>', on_out)

#  FUNCTII APLICAȚIE

def adauga_task():
    task = entry_task.get()
    categorie = entry_categorie.get()
    data_limita = entry_data.get()
    prioritate = prioritate_var.get()

    if task in ["", "Task"] or categorie in ["", "Categorie"] or data_limita in ["", "Data"]:
        messagebox.showwarning("Eroare", "Te rugăm să completezi toate câmpurile!")
        return

    # Validare extinsă (format + prag 2026)
    este_ok, data_finala, mesaj_eroare = proceseaza_si_valideaza_data(data_limita)
    
    if not este_ok:
        messagebox.showerror("Dată Invalidă", mesaj_eroare)
        return

    text_task = f"[{categorie}] {task} (până la {data_finala}) - Prioritate: {prioritate}"
    lista_taskuri.insert(tk.END, text_task)
    coloreaza_task(prioritate, lista_taskuri.size() - 1)

    # Resetare câmpuri
    for ent, txt in [(entry_task, "Task"), (entry_categorie, "Categorie"), (entry_data, "Data")]:
        ent.delete(0, tk.END)
        ent.insert(0, txt)
        ent.config(fg='grey')
    
    root.focus() 
    salveaza_taskuri()

def coloreaza_task(prioritate, index):
    if "Mare" in prioritate:
        lista_taskuri.itemconfig(index, fg="red")
    elif "Medie" in prioritate:
        lista_taskuri.itemconfig(index, fg="orange")
    elif "Mică" in prioritate:
        lista_taskuri.itemconfig(index, fg="green")
    
    if "✔" in lista_taskuri.get(index):
        lista_taskuri.itemconfig(index, fg="gray")

def sterge_task():
    try:
        index = lista_taskuri.curselection()[0]
        if messagebox.askyesno("Confirmare", "Ești sigur că vrei să ștergi acest task?"):
            lista_taskuri.delete(index)
            salveaza_taskuri()
    except:
        messagebox.showwarning("Eroare", "Selectează un task!")

def sterge_toate_taskurile():
    if messagebox.askyesno("Confirmare", "Ești sigur că vrei să ștergi TOATE task-urile?"):
        lista_taskuri.delete(0, tk.END)
        salveaza_taskuri()

def editeaza_task():
    try:
        index = lista_taskuri.curselection()[0]
        task_nou = entry_task.get()
        categorie = entry_categorie.get()
        data_limita = entry_data.get()
        prioritate = prioritate_var.get()

        este_ok, data_finala, mesaj_eroare = proceseaza_si_valideaza_data(data_limita)
        if not este_ok:
            messagebox.showerror("Dată Invalidă", mesaj_eroare)
            return

        text_nou = f"[{categorie}] {task_nou} (până la {data_finala}) - Prioritate: {prioritate}"
        lista_taskuri.delete(index)
        lista_taskuri.insert(index, text_nou)
        coloreaza_task(prioritate, index)
        salveaza_taskuri()
    except:
        messagebox.showwarning("Eroare", "Selectează un task!")

def task_terminat():
    try:
        index = lista_taskuri.curselection()[0]
        task = lista_taskuri.get(index)
        if "✔" not in task:
            lista_taskuri.delete(index)
            lista_taskuri.insert(index, task + " ✔")
            lista_taskuri.itemconfig(index, fg="gray")
            salveaza_taskuri()
    except:
        messagebox.showwarning("Eroare", "Selectează un task!")

def salveaza_taskuri():
    with open(FISIER, "w", encoding="utf-8") as f:
        for i in range(lista_taskuri.size()):
            f.write(lista_taskuri.get(i) + "\n")

def incarca_taskuri():
    if os.path.exists(FISIER):
        try:
            with open(FISIER, "r", encoding="utf-8") as f:
                for linie in f:
                    linie = linie.strip()
                    if linie:
                        lista_taskuri.insert(tk.END, linie)
                        idx = lista_taskuri.size() - 1
                        if "Prioritate: Mare" in linie: coloreaza_task("Mare", idx)
                        elif "Prioritate: Medie" in linie: coloreaza_task("Medie", idx)
                        elif "Prioritate: Mică" in linie: coloreaza_task("Mică", idx)
        except Exception as e:
            print(f"Eroare: {e}")

def confirmare_iesire():
    if messagebox.askyesno("Ieșire", "Ești sigur că vrei să ieși?"):
        root.destroy()

#  INTERFATA
root = tk.Tk()
root.title("To-Do List")
root.geometry("650x700")
root.configure(bg="lightgray")

vcmd = (root.register(valideaza_caractere_data), '%S')
root.protocol("WM_DELETE_WINDOW", confirmare_iesire)

FONT_ENTRY = ("Arial", 12)
FONT_BUTTON = ("Arial", 10, "bold")
FONT_LISTA = ("Arial", 11)

tk.Label(root, text="TO-DO LIST", font=("Arial", 18, "bold"), bg="lightgray").pack(pady=10)

entry_task = tk.Entry(root, width=45, font=FONT_ENTRY)
entry_task.pack(pady=5)
setup_placeholder(entry_task, "Task")

entry_categorie = tk.Entry(root, width=45, font=FONT_ENTRY)
entry_categorie.pack(pady=5)
setup_placeholder(entry_categorie, "Categorie")

entry_data = tk.Entry(root, width=45, font=FONT_ENTRY, validate="key", validatecommand=vcmd)
entry_data.pack(pady=5)
setup_placeholder(entry_data, "Data")

prioritate_var = tk.StringVar(value="Medie")
tk.OptionMenu(root, prioritate_var, "Mică", "Medie", "Mare").pack(pady=5)

lista_taskuri = tk.Listbox(root, width=75, height=15, font=FONT_LISTA, bg="white")
lista_taskuri.pack(pady=10)

tk.Button(root, text="Adaugă", font=FONT_BUTTON, bg="green", fg="white", width=25, command=adauga_task).pack(pady=3)
tk.Button(root, text="Editează", font=FONT_BUTTON, bg="cyan", width=25, command=editeaza_task).pack(pady=3)
tk.Button(root, text="Task terminat", font=FONT_BUTTON, bg="lightblue", width=25, command=task_terminat).pack(pady=3)
tk.Button(root, text="Șterge task", font=FONT_BUTTON, bg="red", fg="white", width=25, command=sterge_task).pack(pady=3)
tk.Button(root, text="Șterge toate task-urile", font=FONT_BUTTON, bg="darkred", fg="white", width=25, command=sterge_toate_taskurile).pack(pady=5)

incarca_taskuri()
root.focus_set()
root.mainloop()