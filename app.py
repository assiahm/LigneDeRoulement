import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io

# Chargement des données depuis le fichier Excel
file_path = "Listeevosbase.xlsx"  # Remplacez par le chemin de votre fichier
data = pd.read_excel(file_path)

# Interface utilisateur Streamlit
st.title("Lignes de Roulement des Trains")

# Sélection de plusieurs jours
jours_disponibles = data['Jour'].unique()
jours_selectionnes = st.multiselect("Sélectionnez les jours :", jours_disponibles)

# Filtrage des données en fonction des jours sélectionnés
if jours_selectionnes:
    data_filtre = data[data['Jour'].isin(jours_selectionnes)]

    # Sélection de plusieurs lignes
    lignes_disponibles = data_filtre['Ligne Jour'].unique()
    lignes_selectionnees = st.multiselect("Sélectionnez les lignes :", lignes_disponibles)

    # Filtrage des données en fonction des lignes sélectionnées
    if lignes_selectionnees:
        data_finale = data_filtre[data_filtre['Ligne Jour'].isin(lignes_selectionnees)]

        # Affichage des données sous forme de tableau
        st.subheader(f"Lignes de roulement pour les jours {', '.join(jours_selectionnes)} et les lignes {', '.join(lignes_selectionnees)}")
        st.dataframe(data_finale)

        # Création des schémas de roulement pour chaque combinaison jour/ligne
        if not data_finale.empty:
            st.subheader("Schémas des Lignes de Roulement")
            
            # Charger l'icône de train
            train_icon_path = "train_icon.png"  # Assurez-vous que ce fichier est dans le même dossier
            train_icon = mpimg.imread(train_icon_path)

            for jour in jours_selectionnes:
                for ligne in lignes_selectionnees:
                    # Filtrer les données pour une combinaison spécifique jour/ligne
                    data_combinaison = data_finale[(data_finale['Jour'] == jour) & (data_finale['Ligne Jour'] == ligne)]
                    
                    if not data_combinaison.empty:
                        # Préparer les données pour le schéma
                        trains = []
                        heures_depart = []
                        heures_arrivee = []
                        types = []

                        for index, row in data_combinaison.iterrows():
                            trains.append(row["TrainA"])
                            # Correction de la conversion des heures
                            heures_depart.append(pd.to_datetime(row["HeureA"], format="%H:%M:%S", errors="coerce"))
                            heures_arrivee.append(pd.to_datetime(row["HeureD"], format="%H:%M:%S", errors="coerce"))
                            types.append(row["TypeTrainA"])  # Commercial ou Évolution

                        # Création du schéma horizontal
                        fig, ax = plt.subplots(figsize=(12, 4))
                        x_positions = range(len(trains))  # Position des éléments sur l'axe X
                        y_position = 0  # Fixe la position Y pour tous les éléments (schéma horizontal)

                        # Ajouter le titre au schéma (jour et numéro de ligne)
                        ax.text(-0.8, 1.2, f"Jour : {jour}\nLigne_de_roulement num : {ligne}", 
                                ha="left", va="top", fontsize=12, color="darkblue", weight="bold")

                        for i, (train, heure_d, heure_a, type_train) in enumerate(zip(trains, heures_depart, heures_arrivee, types)):
                            # Déterminer la couleur de fond en fonction du type de train
                            if type_train == "Commercial":
                                color = "green"
                            elif type_train == "Évolution":
                                color = "orange"
                            else:
                                color = "gray"  # Couleur par défaut

                            # Dessiner un rectangle pour chaque train avec uniquement le numéro du train
                            ax.text(i, y_position, f"{train}", 
                                    ha="center", va="center", fontsize=10, bbox=dict(facecolor=color, edgecolor="black", boxstyle="round,pad=0.5"))

                            # Ajouter l'icône aux extrémités de la ligne de roulement
                            if i == 0:  # Première position
                                ax.imshow(train_icon, aspect="auto", extent=(i - 0.5, i, y_position - 0.8, y_position + 0.8))
                            elif i == len(trains) - 1:  # Dernière position
                                ax.imshow(train_icon, aspect="auto", extent=(i, i + 0.5, y_position - 0.8, y_position + 0.8))

                            # Ajouter les heures en annotations
                            if pd.notna(heure_d) and pd.notna(heure_a):  # Vérifier que les heures sont valides
                                ax.text(i, y_position - 0.4, f"{heure_d.strftime('%H:%M')} -> {heure_a.strftime('%H:%M')}", ha="center", va="top", fontsize=8, color="darkblue")

                            # Dessiner une flèche vers le prochain train
                            if i < len(trains) - 1 and pd.notna(heures_depart[i + 1]) and pd.notna(heures_arrivee[i]):
                                # Calculer la durée entre l'heure D du train actuel et l'heure A du suivant
                                duration = (heures_depart[i + 1] - heures_arrivee[i]).total_seconds() / 60  # Durée en minutes
                                ax.annotate("", xy=(i + 0.8, y_position), xytext=(i + 0.2, y_position),
                                            arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
                                # Ajouter la durée au-dessus de la flèche
                                ax.text(i + 0.5, y_position + 0.2, f"{int(duration)} min", ha="center", va="bottom", fontsize=8, color="darkred")

                        # Configuration de l'axe
                        ax.set_xlim(-1, len(trains))
                        ax.set_ylim(-1, 1.5)  # Ajuster la hauteur pour le titre
                        ax.axis("off")  # Masquer les axes pour une meilleure lisibilité

                        # Afficher le schéma dans Streamlit
                        st.pyplot(fig)
    else:
        st.warning("Veuillez sélectionner au moins une ligne.")
else:
    st.warning("Veuillez sélectionner au moins un jour.")

# Téléchargement des données filtrées
if jours_selectionnes and lignes_selectionnees and not data_finale.empty:
    st.subheader("Télécharger les données filtrées")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        data_finale.to_excel(writer, index=False, sheet_name="Lignes de Roulement")
        writer.close()

    st.download_button(
        label="Télécharger au format Excel",
        data=buffer,
        file_name=f"Lignes_Roulement_{'_'.join(jours_selectionnes)}.xlsx",
        mime="application/vnd.ms-excel",
    )

    st.download_button(
        label="Télécharger au format CSV",
        data=data_finale.to_csv(index=False),
        file_name=f"Lignes_Roulement_{'_'.join(jours_selectionnes)}.csv",
        mime="text/csv",
    )
