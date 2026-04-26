import pandas as pd
import os
from datetime import date

DATA_FILE = "data.csv"

def init_data():
    """Initialise le fichier de données s'il n'existe pas."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "ID", "Date", "Catégorie", "Sous_Catégorie", "Quantité", "Unité", "Notes"
        ])
        df.to_csv(DATA_FILE, index=False)

def load_data():
    """Charge les données depuis le fichier CSV."""
    init_data()
    return pd.read_csv(DATA_FILE)

def add_entry(date_entree, categorie, sous_cat, quantite, unite, notes):
    """Ajoute une nouvelle entrée dans le fichier CSV."""
    df = load_data()
    
    # Génération d'un ID basique
    new_id = 1 if df.empty else df["ID"].max() + 1
    
    new_row = {
        "ID": new_id,
        "Date": date_entree,
        "Catégorie": categorie,
        "Sous_Catégorie": sous_cat,
        "Quantité": quantite,
        "Unité": unite,
        "Notes": notes
    }
    
    # Utilisation de concat plutôt que append (déprécié dans pandas)
    df_new = pd.DataFrame([new_row])
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return True

def delete_entry(entry_id):
    """Supprime une entrée par son ID."""
    df = load_data()
    df = df[df["ID"] != entry_id]
    df.to_csv(DATA_FILE, index=False)
    return True

# Initialiser au chargement du module
init_data()
