import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import data_manager as dm

# Configuration de la page
st.set_page_config(
    page_title="EcoGarden Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction utilitaire pour appliquer des styles personnalisés avec CSS
def local_css():
    st.markdown("""
    <style>
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
        border-top: 5px solid #2e7d32;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2e7d32;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Titre de l'application
st.title("🌱 EcoGarden Tracker")
st.markdown("Suivi et Analyse pour votre Jardin Communautaire Urbain")

# Chargement des données
df = dm.load_data()

# Sidebar pour la navigation (ou on utilise des tabs)
# On va utiliser des tabs pour une interface plus fluide
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Tableau de Bord", "📝 Saisie de Données", "📊 Analyse", "📋 Données Brutes"])

# --- TAB 1: Tableau de Bord ---
with tab1:
    st.header("Vue d'ensemble")
    
    if df.empty:
        st.info("Aucune donnée enregistrée pour le moment. Allez dans l'onglet 'Saisie de Données' pour commencer !")
    else:
        # Calcul des métriques
        total_recoltes = df[df["Catégorie"] == "Récolte"]["Quantité"].sum()
        total_eau = df[df["Catégorie"] == "Eau"]["Quantité"].sum()
        total_benevolat = df[df["Catégorie"] == "Bénévolat"]["Quantité"].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total des Récoltes (kg)</div>
                <div class="metric-value">{total_recoltes:.1f} 🍅</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Eau Consommée (L)</div>
                <div class="metric-value">{total_eau:.1f} 💧</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Heures Bénévolat (h)</div>
                <div class="metric-value">{total_benevolat:.1f} 🧑‍🌾</div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Activité Récente")
        # Afficher les 5 dernières entrées
        st.dataframe(df.sort_values(by="Date", ascending=False).head(5), use_container_width=True)


# --- TAB 2: Saisie de Données ---
with tab2:
    st.header("Nouvelle Entrée")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date_entree = st.date_input("Date", datetime.today())
            categorie = st.selectbox("Catégorie", ["Récolte", "Eau", "Bénévolat", "Autre"])
            
            # Sous-catégorie dynamique basée sur la catégorie (Streamlit relance le script, 
            # mais dans un form, c'est mieux de faire un choix générique ou de ne pas utiliser st.form 
            # si on veut de la dynamicité en temps réel. Pour garder la robustesse, on garde simple.)
            if categorie == "Récolte":
                options_sous_cat = ["Tomates", "Carottes", "Salades", "Radis", "Herbes", "Autre"]
                unite_defaut = "kg"
            elif categorie == "Eau":
                options_sous_cat = ["Arrosage Manuel", "Goutte à goutte", "Pluie (Récupération)"]
                unite_defaut = "L"
            elif categorie == "Bénévolat":
                options_sous_cat = ["Entretien", "Plantation", "Récolte", "Animation"]
                unite_defaut = "h"
            else:
                options_sous_cat = ["Autre"]
                unite_defaut = "unité"
                
        with col2:
            # On demande à l'utilisateur de taper la sous-catégorie pour plus de flexibilité dans le form
            sous_cat = st.text_input("Sous-Catégorie / Détail (ex: Tomates Cerises, Jean Dupont)", placeholder="Détail...")
            
            col2a, col2b = st.columns([2, 1])
            with col2a:
                quantite = st.number_input("Quantité", min_value=0.0, format="%.2f")
            with col2b:
                unite = st.selectbox("Unité", ["kg", "L", "h", "unités", "g", "ml"])
                
        notes = st.text_area("Notes (Optionnel)")
        
        submit_button = st.form_submit_button(label="Ajouter l'entrée")
        
        if submit_button:
            if sous_cat.strip() == "":
                st.warning("Veuillez renseigner la Sous-Catégorie.")
            elif quantite <= 0:
                st.warning("La quantité doit être supérieure à 0.")
            else:
                dm.add_entry(date_entree, categorie, sous_cat, quantite, unite, notes)
                st.success("Entrée ajoutée avec succès ! 🎉")
                st.rerun() # Pour mettre à jour les autres onglets


# --- TAB 3: Analyse ---
with tab3:
    st.header("Analyse Descriptive")
    
    if df.empty:
        st.info("Ajoutez des données pour voir les analyses.")
    else:
        # Assurer que la date est au format datetime pour Plotly
        df['Date'] = pd.to_datetime(df['Date'])
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Répartition des Catégories")
            # Uniquement les quantités ne sont pas comparables (kg vs L vs h), on compte le nombre d'actions
            fig_pie = px.pie(df, names='Catégorie', title='Nombre d\'actions par catégorie', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            st.subheader("Évolution des Récoltes")
            df_recoltes = df[df["Catégorie"] == "Récolte"].groupby("Date")["Quantité"].sum().reset_index()
            if not df_recoltes.empty:
                fig_line = px.line(df_recoltes, x="Date", y="Quantité", markers=True, 
                                   title="Cumul des récoltes (kg) dans le temps",
                                   line_shape='spline')
                fig_line.update_traces(line_color="#2e7d32", marker_color="#1b5e20")
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.write("Pas de données de récolte à afficher.")

        st.subheader("Détail par Sous-Catégorie (Top 10)")
        cat_filter = st.selectbox("Filtrer par catégorie pour le détail:", df["Catégorie"].unique())
        df_filtered = df[df["Catégorie"] == cat_filter]
        
        df_grouped = df_filtered.groupby("Sous_Catégorie")["Quantité"].sum().reset_index().sort_values(by="Quantité", ascending=False).head(10)
        
        fig_bar = px.bar(df_grouped, x="Sous_Catégorie", y="Quantité", 
                         title=f"Total Quantité par Sous-Catégorie ({cat_filter})",
                         color="Sous_Catégorie", color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_bar, use_container_width=True)


# --- TAB 4: Données Brutes ---
with tab4:
    st.header("Exploration des Données")
    
    if df.empty:
         st.write("Le tableau est vide.")
    else:
        # Filtres
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cat_filter_raw = st.multiselect("Filtrer par Catégorie", df["Catégorie"].unique(), default=df["Catégorie"].unique())
        with col_f2:
            sort_by = st.selectbox("Trier par", df.columns)
            
        df_display = df[df["Catégorie"].isin(cat_filter_raw)].sort_values(by=sort_by)
        
        st.dataframe(df_display, use_container_width=True)
        
        # Option de suppression (basique)
        st.subheader("Zone de Danger")
        id_to_delete = st.number_input("Entrez l'ID de l'entrée à supprimer", min_value=1, step=1)
        if st.button("Supprimer l'entrée"):
            if id_to_delete in df["ID"].values:
                dm.delete_entry(id_to_delete)
                st.success(f"Entrée {id_to_delete} supprimée.")
                st.rerun()
            else:
                st.error("ID non trouvé.")

        # Bouton pour télécharger les données en CSV
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df)
        st.download_button(
            label="📥 Télécharger les données en CSV",
            data=csv,
            file_name='ecogarden_data.csv',
            mime='text/csv',
        )

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><small>EcoGarden Tracker - Construit avec Streamlit & Python 🐍</small></div>", unsafe_allow_html=True)
