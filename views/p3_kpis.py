import pandas as pd
import plotly.express as px
import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
sup = an.load_supports()
df = an.appliquer(sup, f)
k = an.kpis(df)
hist = an.kpis_historiques(an.appliquer_historique(an.load_historique(), f))
ref_f = an.Filtres(zone=f.zone, operateurs=f.operateurs, techno=f.techno)
ref = an.kpis(an.appliquer(sup, ref_f))

ch.head("Indicateurs", f.libelle(), an.load_qualite()["export_reference"])
st.title("Indicateurs")
if not k:
    st.warning("Aucun support ne correspond à ces filtres. Élargissez le périmètre dans le panneau de gauche.")
    st.stop()

DEFS = [
    ("part_towerco", "Part des TowerCos", "pct", "Part des supports détenus par une société d'infrastructures.",
     "En hausse : l'accès aux points hauts passe par un intermédiaire."),
    ("part_operateur", "Détention par les opérateurs", "pct", "Part des supports détenus par un opérateur télécom.",
     "En baisse : les opérateurs perdent la maîtrise de leur foncier."),
    ("top1_part", "Poids du premier propriétaire", "pct", "Part des supports du premier propriétaire identifié.",
     "Au-delà de 25 %, l'acteur devient incontournable."),
    ("cr4", "Part des 4 premiers (CR4)", "pct", "Part cumulée des quatre premiers propriétaires identifiés.",
     "Au-delà de 50 %, le marché est un oligopole."),
    ("hhi", "Indice HHI", "num", "Somme des carrés des parts de marché des propriétaires identifiés (0 à 10 000).",
     "Moins de 1 000 : peu concentré. 1 000 à 1 800 : modéré. Plus de 1 800 : très concentré."),
    ("mutualisation", "Supports mutualisés", "pct", "Part des supports qui hébergent au moins deux opérateurs.",
     "En hausse : moins de pylônes, chacun plus partagé."),
    ("quatre_ops", "Supports à 4 opérateurs", "pct", "Part des supports qui hébergent les quatre opérateurs.",
     "En hausse : plus de points dont dépendent tous les réseaux."),
    ("communes_mono", "Communes captives", "pct",
     "Communes d'au moins deux supports, tous détenus par la même entreprise.", "En hausse : aucune alternative locale."),
]


def fmt(kind, v):
    return an.pct(v) if kind == "pct" else an.nombre(v)


def ecart(key, kind):
    if key in hist.columns and len(hist) > 1:
        d = hist[key].iloc[-1] - hist[key].iloc[0]
        return (f"{d * 100:+.1f} pts" if kind == "pct" else f"{d:+.0f}") + f" depuis {hist.annee.iloc[0]}"
    if not f.est_national():
        d = k[key] - ref[key]
        return (f"{d * 100:+.1f} pts" if kind == "pct" else f"{d:+.0f}") + f" vs {ref_f.libelle()}"
    return None


ch.kpis([(lab, fmt(kind, k[key]), ecart(key, kind), False) for key, lab, kind, *_ in DEFS[:4]])
ch.kpis([(lab, fmt(kind, k[key]), ecart(key, kind), False) for key, lab, kind, *_ in DEFS[4:]])
st.caption(
    f"Premier propriétaire : {k['top1_nom']}. Concentration : {an.niveau_hhi(k['hhi'])}. "
    f"{an.nombre(k['n_quatre_ops'])} supports hébergent les quatre opérateurs, sur {an.nombre(k['n_communes'])} communes équipées."
)

with st.expander("Définitions et lecture des indicateurs"):
    st.dataframe(
        pd.DataFrame([(lab, d, lec) for _, lab, _, d, lec in DEFS], columns=["Indicateur", "Définition", "Lecture"]),
        hide_index=True, width="stretch",
    )

if not f.est_national():
    st.header("Comparaison avec la référence")
    rows = []
    for key, lab, kind, *_ in DEFS:
        d = k[key] - ref[key]
        rows.append({
            "Indicateur": lab,
            "Sélection": fmt(kind, k[key]),
            ref_f.libelle(): fmt(kind, ref[key]),
            "Écart": f"{d * 100:+.1f} pts" if kind == "pct" else f"{d:+.0f}",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

st.header("Évolution 2018-2026")
SERIES = {
    "part_towerco": ("Part des TowerCos", ch.BLUE),
    "part_operateur": ("Détention par les opérateurs", ch.ACCENT),
    "mutualisation": ("Supports mutualisés", ch.GREEN),
    "quatre_ops": ("Supports à 4 opérateurs", ch.OCHRE),
    "top1_part": ("Poids du premier propriétaire", ch.INK_2),
}
long = hist.melt(id_vars="annee", value_vars=list(SERIES))
long["Indicateur"] = long["variable"].map(lambda v: SERIES[v][0])
long["value"] *= 100
ch.figure("3.1", "Le basculement de la propriété, année par année")
fig = px.line(long, x="annee", y="value", color="Indicateur", markers=True,
              color_discrete_map={v[0]: v[1] for v in SERIES.values()},
              category_orders={"Indicateur": [v[0] for v in SERIES.values()]},
              labels={"annee": "", "value": "% des supports"})
fig.update_traces(line_width=2, marker_size=8, hovertemplate="%{y:.1f} %<extra>%{fullData.name}</extra>")
fig.add_vrect(x0=2019.5, x1=2022.5, fillcolor=ch.RULE, opacity=0.35, line_width=0)
fig.add_annotation(x=2021, y=0.03, yref="paper", text="cessions des pylônes", showarrow=False,
                   font=dict(size=11, color=ch.INK_2), yanchor="bottom")
ch.plot(fig, 420)
ch.note(f"<b>À remarquer.</b> Les courbes bleue et rouge se croisent entre 2020 et 2022 : "
        f"les TowerCos passent de {an.pct(hist.part_towerco.iloc[0], 0)} à {an.pct(hist.part_towerco.iloc[-1], 0)} des supports.")

c1, c2 = st.columns(2, gap="large")
with c1:
    ch.figure("3.2", "Concentration des propriétaires identifiés (HHI)")
    fig = px.line(hist, x="annee", y="hhi", markers=True, labels={"annee": "", "hhi": "HHI"})
    fig.update_traces(line_color=ch.BLUE, line_width=2, marker_size=8, hovertemplate="HHI %{y:.0f}<extra></extra>")
    fig.add_hline(y=1000, line_dash="dot", line_color=ch.INK_2, annotation_text="seuil de concentration modérée",
                  annotation_font=dict(size=11, color=ch.INK_2))
    ch.plot(fig, 300, legend=False)
    ch.note("<b>À remarquer.</b> Au niveau national, le marché reste peu concentré. La dépendance se joue localement (page 6).")
with c2:
    ch.figure("3.3", "Nombre de supports mobiles")
    fig = px.bar(hist, x="annee", y="n_supports", labels={"annee": "", "n_supports": "Supports"})
    fig.update_traces(marker_color=ch.BLUE, hovertemplate="%{y:,.0f} supports<extra></extra>")
    ch.plot(fig, 300, legend=False)
    ch.note(f"<b>À remarquer.</b> Le parc passe de {an.nombre(hist.n_supports.iloc[0])} à "
            f"{an.nombre(hist.n_supports.iloc[-1])} supports, porté par la 4G puis la 5G.")
if f.operateurs or f.techno != "Toutes":
    st.caption("L'historique ne suit que les filtres géographiques.")
