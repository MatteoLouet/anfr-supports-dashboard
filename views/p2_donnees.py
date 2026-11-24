import pandas as pd
import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
df = an.appliquer(an.load_supports(), f)
q = an.load_qualite()

ch.head("Les données", f.libelle(), q["export_reference"])
st.title("Les données")
st.markdown(
    "<p class='lead'>Un registre administratif exhaustif : toute installation radio de plus de 5 W "
    "doit être déclarée à l'Agence nationale des fréquences.</p>",
    unsafe_allow_html=True,
)

c1, c2 = st.columns([3, 2], gap="large")
with c1:
    st.header("Source")
    st.markdown(
        """
| | |
|---|---|
| Jeu de données | [Installations radioélectriques de plus de 5 watts](https://www.data.gouv.fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1) |
| Portail | data.gouv.fr |
| Producteur | ANFR, Licence Ouverte Etalab |
| Mise à jour | Mensuelle |
| Instantanés retenus | L'export d'octobre de chaque année, 2018 à 2026 |
| Tables | Supports, stations, émetteurs, référentiels propriétaires, exploitants et natures |
"""
    )
    st.header("Traitement")
    st.markdown(
        """
1. **Ingestion.** `src/download.py` interroge l'API data.gouv.fr et télécharge l'export d'octobre de chaque année.
2. **Périmètre mobile.** Sont retenues les stations qui portent un émetteur GSM, UMTS, LTE ou 5G NR.
   Le GSM-R ferroviaire et les réseaux LTE privés sont exclus.
3. **Jointures.** Émetteur, puis station (opérateur), puis support (propriétaire, localisation).
4. **Agrégation.** Une ligne par support physique : propriétaire, opérateurs hébergés, technologies, commune.
5. **Enrichissement.** Coordonnées converties en degrés décimaux, code INSEE rattaché au département
   et à la région, propriétaire classé en cinq catégories.
6. **Historique.** Le même traitement sur les neuf instantanés, agrégé par département et propriétaire.
"""
    )
with c2:
    st.header("Contrôle qualité")
    rows = [
        ("Lignes supports brutes", q["lignes_supports_brutes"]),
        ("Lignes stations brutes", q["lignes_stations_brutes"]),
        ("Lignes émetteurs brutes", q["lignes_emetteurs_brutes"]),
        ("Doublons exacts supprimés", q["doublons_supports_exacts"]),
        ("Émetteurs mobiles retenus", q["emetteurs_mobiles"]),
        ("dont sans date de mise en service", q["emetteurs_mobiles_sans_date"]),
        ("Stations mobiles", q["stations_mobiles"]),
        ("Supports mobiles analysés", q["supports_mobiles"]),
        ("Supports sans propriétaire", q["supports_sans_proprietaire"]),
        ("Supports sans commune", q["supports_sans_insee"]),
        ("Supports sans coordonnées", q["supports_sans_coordonnees"]),
        ("Hauteurs hors plage (≤ 0 ou > 350 m), vidées", q["supports_hauteur_aberrante"]),
    ]
    st.dataframe(
        pd.DataFrame(rows, columns=["Contrôle", "Valeur"]).assign(Valeur=lambda d: d["Valeur"].map(an.nombre)),
        hide_index=True, width="stretch", height=458,
    )

st.header("Hypothèses et limites")
a, b = st.columns(2, gap="large")
with a:
    st.markdown(
        """
**Hypothèses**

- Le propriétaire déclaré d'un support en contrôle l'accès.
- Les libellés génériques (copropriétés, HLM, particuliers, communes) regroupent des milliers
  de propriétaires distincts. Ils sont exclus du calcul de concentration.
- Une commune est captive si elle compte au moins deux supports, tous détenus par la même entreprise.
- L'année d'implantation d'un support est celle de sa plus ancienne station.
"""
    )
with b:
    st.markdown(
        """
**Limites**

- L'ANFR exclut les installations de la Défense, de l'Intérieur et de l'Aviation civile.
- Les liens capitalistiques entre TowerCos et opérateurs ne figurent pas dans le registre :
  chaque TowerCo est traitée comme une entité indépendante.
- L'export 2018 ne contient pas les dates de mise en service des émetteurs.
- Loyers et contrats ne sont pas publics. La dépendance se mesure ici par la structure de propriété, pas par les prix.
"""
    )

st.header("Les supports de la sélection")
cols = ["sup_id", "dep_nom", "insee", "proprietaire", "categorie", "nature", "hauteur_m",
        "n_operateurs", "op_orange", "op_sfr", "op_bouygues", "op_free", "tech_5g", "annee_implantation", "lat", "lon"]
st.caption(f"{an.nombre(len(df))} supports. Les 500 premiers sont affichés ; le fichier complet est téléchargeable.")
st.dataframe(df[cols].head(500), hide_index=True, width="stretch", height=320)
st.download_button("Télécharger la sélection en CSV", df[cols].to_csv(index=False).encode("utf-8"),
                   file_name="supports_mobiles_selection.csv", mime="text/csv")
