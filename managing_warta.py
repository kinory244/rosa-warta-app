# === Gestione Rosa Warta EN A (Restylized UI) ===
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

CSV_LISTONE_PATH = os.path.abspath("listone_fvm.csv")
CSV_ROSA_PATH = os.path.abspath("rosa_warta.csv")
ROSA_DIMENSIONE = 30
COLORI_RUOLI = {
    "P": "#d0e1f9",
    "D": "#d0f9d9",
    "C": "#f9f1d0",
    "A": "#f9d0d0"
}

def convert_excel_to_csv(filepath):
    try:
        df = pd.read_excel(filepath, skiprows=1)
        df = df[["R", "RM", "Nome", "Squadra", "FVM"]]
        df.to_csv(CSV_LISTONE_PATH, index=False)
        return df
    except Exception as e:
        messagebox.showerror("Errore nella conversione", str(e))
        return None

def carica_listone():
    file_path = filedialog.askopenfilename(title="Seleziona il file Excel del listone")
    if file_path:
        df = convert_excel_to_csv(file_path)
        if df is not None:
            messagebox.showinfo("Successo", "File convertito e salvato come CSV.")

def aggiorna_fvmp():
    try:
        if not os.path.exists(CSV_LISTONE_PATH):
            messagebox.showerror("Errore", "Devi prima caricare e convertire il file Excel del listone.")
            return
        listone_df = pd.read_csv(CSV_LISTONE_PATH)
        for item_id in tabella.get_children():
            valori = tabella.item(item_id, 'values')
            nome = valori[2].strip().lower()
            risultato = listone_df[listone_df['Nome'].str.strip().str.lower() == nome]
            if not risultato.empty:
                fvmp = risultato.iloc[0]['FVM']
                nuovi_valori = list(valori)
                nuovi_valori[6] = fvmp
                tabella.item(item_id, values=nuovi_valori)
        salva_rosa()
    except Exception as e:
        messagebox.showerror("Errore", str(e))

def apri_editor_riga(event):
    selected_item = tabella.focus()
    if not selected_item:
        return
    valori = tabella.item(selected_item, 'values')
    editor = tk.Toplevel(root)
    editor.title("Modifica giocatore")

    labels = ["Ruolo", "Nome", "Prezzo", "Squadra", "Anni Contratto", "FVMp Prevista"]
    entries = []
    for i, label_text in enumerate(labels):
        tk.Label(editor, text=label_text).grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(editor)
        index_in_valori = i + 1 if i < 5 else 7
        entry.insert(0, valori[index_in_valori])
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def salva():
        nuovi_valori = [valori[0]] + [e.get() for e in entries[:5]] + [valori[6], entries[5].get()]
        tabella.item(selected_item, values=nuovi_valori)
        aggiorna_colori()
        salva_rosa()
        editor.destroy()

    def elimina():
        tabella.delete(selected_item)
        salva_rosa()
        editor.destroy()

    tk.Button(editor, text="Salva", command=salva).grid(row=len(labels), column=0, pady=10)
    tk.Button(editor, text="Elimina", command=elimina).grid(row=len(labels), column=1, pady=10)

def salva_rosa():
    dati = [tabella.item(i, 'values') for i in tabella.get_children()]
    df = pd.DataFrame(dati, columns=["#", "Ruolo", "Nome", "Prezzo", "Squadra", "Anni Contratto", "FVMp", "FVMp Prevista"])
    df.to_csv(CSV_ROSA_PATH, index=False)

def carica_rosa():
    if os.path.exists(CSV_ROSA_PATH):
        df = pd.read_csv(CSV_ROSA_PATH)
        if "FVMp Prevista" not in df.columns:
            df["FVMp Prevista"] = ""
        for _, row in df.iterrows():
            tabella.insert('', 'end', values=list(row))
        completa_fino_30()
        aggiorna_colori()

def importa_rosa_excel():
    file_path = filedialog.askopenfilename(title="Importa rosa da file Excel")
    if file_path:
        try:
            df = pd.read_excel(file_path, skiprows=2, usecols="A:D")
            df.columns = ["Ruolo", "Nome", "Squadra", "Prezzo"]
            df = df[["Ruolo", "Nome", "Prezzo", "Squadra"]]
            df["Anni Contratto"] = 3
            df["FVMp"] = ""
            df["FVMp Prevista"] = ""
            tabella.delete(*tabella.get_children())
            for i, row in df.iterrows():
                tabella.insert('', 'end', values=[str(i+1)] + list(row))
            completa_fino_30()
            salva_rosa()
            aggiorna_colori()
        except Exception as e:
            messagebox.showerror("Errore importazione", str(e))

def completa_fino_30():
    esistenti = len(tabella.get_children())
    for i in range(esistenti, ROSA_DIMENSIONE):
        tabella.insert('', 'end', values=[str(i+1), "", "", "", "", "", "", ""])

def aggiorna_colori():
    for item_id in tabella.get_children():
        ruolo = tabella.item(item_id, 'values')[1]
        colore = COLORI_RUOLI.get(ruolo, "white")
        tabella.tag_configure(ruolo, background=colore)
        tabella.item(item_id, tags=(ruolo,))

def calcola_stipendi_attuale():
    totale_attuale = 0
    dettagli = []
    for item_id in tabella.get_children():
        valori = tabella.item(item_id, 'values')
        try:
            nome = valori[2]
            fvmp = pd.to_numeric(valori[6], errors='coerce')
            if pd.notna(fvmp):
                totale_attuale += fvmp
                dettagli.append(f"{nome}: {fvmp} Mln")
        except:
            continue

    msg = "Tranche settembre (10% della somma FVMp):\n" + "\n".join(dettagli)
    msg += f"\n\nTotale FVMp: {totale_attuale:.2f} Mln\nStipendi: {totale_attuale * 0.10:.2f} Mln"
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, msg)

def calcola_stipendi_previsti():
    totale_previsto = 0
    dettagli = []
    for item_id in tabella.get_children():
        valori = tabella.item(item_id, 'values')
        try:
            nome = valori[2]
            fvmp_prevista = pd.to_numeric(valori[7], errors='coerce')
            if pd.notna(fvmp_prevista):
                totale_previsto += fvmp_prevista
                dettagli.append(f"{nome}: {fvmp_prevista} Mln")
        except:
            continue

    msg = "Stipendi su base FVMp Prevista:\n" + "\n".join(dettagli)
    msg += f"\n\nTotale FVMp Prevista: {totale_previsto:.2f} Mln\nStipendi: {totale_previsto * 0.10:.2f} Mln"
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, msg)

def applica_incremento_fvmp(percentuale):
    for item_id in tabella.get_children():
        valori = tabella.item(item_id, 'values')
        try:
            fvmp = pd.to_numeric(valori[6], errors='coerce')
            if pd.notna(fvmp):
                incremento = fvmp * (percentuale / 100)
                fvmp_prevista = round(fvmp + incremento, 2)
            else:
                fvmp_prevista = ""
        except:
            fvmp_prevista = ""
        nuovi_valori = list(valori)
        nuovi_valori[7] = fvmp_prevista
        tabella.item(item_id, values=nuovi_valori)
    salva_rosa()

# === GUI ===
root = tk.Tk()
root.title("Gestione Rosa Warta EN A")
root.geometry("1200x900")
root.option_add("*Font", "SegoeUI 10")

tk.Label(root, text="Gestione Rosa Warta EN A", font=("SegoeUI", 16, "bold")).pack(pady=10)

frame_file = tk.LabelFrame(root, text="📁 Importazione Dati")
frame_file.pack(pady=10, padx=20, fill="x")

tk.Button(frame_file, text="1. Carica file Excel del listone", width=30, command=carica_listone).grid(row=0, column=0, padx=10, pady=5)
tk.Button(frame_file, text="2. Importa rosa da Excel", width=30, command=importa_rosa_excel).grid(row=0, column=1, padx=10, pady=5)
tk.Button(frame_file, text="3. Aggiorna FVMp", width=30, command=aggiorna_fvmp).grid(row=0, column=2, padx=10, pady=5)

frame_tabella = tk.LabelFrame(root, text="📋 Rosa")
frame_tabella.pack(pady=10, padx=20, fill="both", expand=True)

cols = ["#", "Ruolo", "Nome", "Prezzo", "Squadra", "Anni Contratto", "FVMp", "FVMp Prevista"]
tabella = ttk.Treeview(frame_tabella, columns=cols, show='headings', height=20)
for col in cols:
    tabella.heading(col, text=col)
    tabella.column(col, width=100)
scroll_y = ttk.Scrollbar(frame_tabella, orient="vertical", command=tabella.yview)
tabella.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
tabella.pack(fill="both", expand=True)
tabella.bind("<Double-1>", apri_editor_riga)
carica_rosa()

frame_fvmp = tk.LabelFrame(root, text="📈 Simulazione FVMp Prevista")
frame_fvmp.pack(pady=10, padx=20, fill="x")

tk.Label(frame_fvmp, text="Variazione:").grid(row=0, column=0, padx=5)
for i, perc in enumerate([-15, -10, -5, 5, 10, 15]):
    tk.Button(frame_fvmp, text=f"{perc:+}%", width=8, command=lambda p=perc: applica_incremento_fvmp(p)).grid(row=0, column=i+1, padx=5)
tk.Button(frame_fvmp, text="Calcola stipendi (FVMp Prevista)", width=30, command=calcola_stipendi_previsti).grid(row=0, column=7, padx=10)

frame_stipendi = tk.LabelFrame(root, text="💰 Stipendi Attuali")
frame_stipendi.pack(pady=10, padx=20, fill="x")
tk.Button(frame_stipendi, text="Calcola stipendi Settembre (FVMp)", command=calcola_stipendi_attuale).pack(pady=5)

frame_output = tk.LabelFrame(root, text="📝 Dettagli")
frame_output.pack(pady=10, padx=20, fill="both", expand=True)
output_box = tk.Text(frame_output, height=10, font=("Consolas", 10))
output_box.pack(fill="both", expand=True)

root.mainloop()
