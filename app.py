"""Qui contrôle l'infrastructure mobile française ? Tableau de bord décisionnel.

Lancer :  streamlit run app.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

import analytics as an  # noqa: E402
import charts as ch  # noqa: E402

st.set_page_config(page_title="Qui contrôle les antennes ?", page_icon=":material/cell_tower:", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(ch.CSS, unsafe_allow_html=True)

if not an.data_ready():
    st.error("Les données préparées sont absentes. Lancez d'abord le téléchargement puis la préparation :")
    st.code("python src/download.py\npython src/prepare.py", language="bash")
    st.stop()

nav = st.navigation([
    st.Page("views/p1_probleme.py", title="1. Le problème", default=True),
    st.Page("views/p2_donnees.py", title="2. Les données"),
    st.Page("views/p3_kpis.py", title="3. Indicateurs"),
    st.Page("views/p4_controle.py", title="4. Qui contrôle ?"),
    st.Page("views/p5_dependances.py", title="5. Dépendances"),
    st.Page("views/p6_territoires.py", title="6. Territoires"),
    st.Page("views/p7_recommandations.py", title="7. Recommandations"),
])

df_all = an.load_supports()
with st.sidebar:
    st.markdown("#### Périmètre")
    zone = st.radio("Zone", ["Métropole", "Outre-mer", "Tout"], horizontal=True, key="f_zone",
                    label_visibility="collapsed")
    base = df_all if zone == "Tout" else df_all[df_all["zone"] == zone]
    regions = st.multiselect("Région", sorted(base["region"].dropna().unique()), key="f_regions",
                             placeholder="Toutes les régions")
    if regions:
        base = base[base["region"].isin(regions)]
    deps = st.multiselect("Département", sorted(base["dep_nom"].dropna().unique()), key="f_deps",
                          placeholder="Tous les départements")
    operateurs = st.multiselect("Opérateur présent sur le support", list(an.OP_COLS), key="f_ops",
                                placeholder="Tous les opérateurs")
    techno = st.selectbox("Technologie présente", ["Toutes"] + an.TECHS, key="f_tech")
    st.session_state["filtres"] = an.Filtres(zone, regions, deps, operateurs, techno)
    st.caption("Les filtres s'appliquent à toutes les pages. L'historique 2018-2026 ne suit que les filtres géographiques.")

nav.run()
