import math

import plotly.express as px
import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
sup = an.load_supports()
df = an.appliquer(sup, f)
ch.head("Territoires", f.libelle(), an.load_qualite()["export_reference"])
st.title("Où la dépendance est‑elle la plus forte ?")
if df.empty:
    st.warning("Aucun support ne correspond à ces filtres. Élargissez le périmètre dans le panneau de gauche.")
    st.stop()

with st.expander("Composition de l'indice de dépendance"):
    st.markdown(
        "L'indice va de 0 à 100. Il combine quatre composantes, chacune ramenée entre le département le moins "
        "exposé (0) et le plus exposé (1). Les poids sont réglables."
    )
    cols = st.columns(4)
    poids = {key: cols[i].slider(lab, 0, 5, 1, key=f"w_{key}") for i, (key, lab) in enumerate(an.COMPOSANTES.items())}

sc = an.scorecard_departements(df, poids)
if sc.empty:
    st.info("Le périmètre choisi ne contient aucun département d'au moins 20 supports : l'indice n'est pas calculable.")
    st.stop()
top = sc.iloc[0]
st.markdown(
    f"<p class='lead'>Les départements ruraux et de montagne sont les plus dépendants. En tête : "
    f"{', '.join(sc['Département'].head(3))}, où {top['top1_nom']} détient {an.pct(top['top1_part'], 0)} des supports.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ carte + classement
c1, c2 = st.columns([3, 2], gap="large")
with c1:
    ch.figure("6.1", "Indice de dépendance par département")
    fig = px.scatter_map(
        sc, lat="lat", lon="lon", size="Supports", color="Indice de dépendance",
        color_continuous_scale=ch.SEQ, range_color=(0, 100), size_max=26, zoom=4.6 if f.zone == "Métropole" and f.est_national() else (6 if not f.est_national() else 1),
        center=dict(lat=float(sc["lat"].median()), lon=float(sc["lon"].median())),
        hover_name="Département",
        hover_data={"lat": False, "lon": False, "Supports": ":,", "Indice de dépendance": ":.0f", "top1_nom": True},
        labels={"top1_nom": "Premier propriétaire"}, map_style="carto-positron",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Indice", thickness=10, outlinewidth=0))
    ch.plot(fig, 560, legend=False)
    ch.note("Un cercle par département : taille selon le nombre de supports, teinte selon l'indice.")
with c2:
    ch.figure("6.2", "Les 15 départements les plus dépendants")
    show = sc.head(15)[["Rang", "Département", "Indice de dépendance", "top1_nom", "top1_part", "communes_mono"]]
    st.dataframe(
        show, hide_index=True, width="stretch", height=560,
        column_config={
            "Indice de dépendance": st.column_config.ProgressColumn("Indice", min_value=0, max_value=100, format="%.0f",
                                                                    color="#315C9B"),
            "top1_nom": "Premier propriétaire",
            "top1_part": st.column_config.NumberColumn("Sa part", format="percent"),
            "communes_mono": st.column_config.NumberColumn("Communes captives", format="percent"),
        },
    )

# ------------------------------------------------------------------ relation
st.header("Moins de supports, plus de dépendance")
ch.figure("6.3", "Nombre de supports et concentration des propriétaires, par département")
fig = px.scatter(sc, x="Supports", y="hhi", hover_name="Département", log_x=True,
                 labels={"Supports": "Supports (échelle logarithmique)", "hhi": "Indice HHI"},
                 hover_data={"top1_nom": True, "Supports": ":,", "hhi": ":.0f"})
fig.update_traces(marker=dict(size=10, color=ch.BLUE, opacity=0.75, line=dict(width=1, color=ch.PAPER)))
fig.add_hline(y=1000, line_dash="dot", line_color=ch.INK_2, annotation_text="concentration modérée",
              annotation_font=dict(size=11, color=ch.INK_2))
for _, r in sc.head(5).iterrows():
    fig.add_annotation(x=math.log10(r["Supports"]), y=r["hhi"], text=r["Département"], showarrow=False,
                       yshift=12, font=dict(size=11, color=ch.ACCENT))
ch.plot(fig, 420, legend=False)
corr = sc[["Supports", "hhi"]].corr(method="spearman").iloc[0, 1]
ch.note(f"<b>À remarquer.</b> Corrélation de rang entre nombre de supports et concentration : {corr:+.2f}. "
        "Les départements peu équipés dépendent d'un petit nombre de bailleurs, souvent le diffuseur historique ; "
        "les métropoles offrent de nombreux toits alternatifs.")

# ------------------------------------------------------------------ zoom
st.header("Un département en détail")
choix = st.selectbox("Département", sc["Département"].tolist(), index=0)
d = df[df["dep_nom"] == choix]
kd = an.kpis(d)
ref_f = an.Filtres(zone=f.zone, operateurs=f.operateurs, techno=f.techno)
kn = an.kpis(an.appliquer(sup, ref_f))
row = sc[sc["Département"] == choix].iloc[0]
ch.kpis([
    ("Indice de dépendance", f"{row['Indice de dépendance']:.0f}", f"rang {row['Rang']} sur {len(sc)}", False),
    ("Supports", an.nombre(kd["n_supports"]), None, False),
    ("Premier propriétaire", kd["top1_nom"], f"{an.pct(kd['top1_part'])}, contre {an.pct(kn['top1_part'])} en moyenne",
     kd["top1_part"] > kn["top1_part"]),
    ("Indice HHI", an.nombre(kd["hhi"]), f"{an.nombre(kn['hhi'])} pour {ref_f.libelle()}", kd["hhi"] > kn["hhi"]),
    ("Supports à 4 opérateurs", an.pct(kd["quatre_ops"]), f"{an.pct(kn['quatre_ops'])} pour {ref_f.libelle()}",
     kd["quatre_ops"] > kn["quatre_ops"]),
])
a, b = st.columns([2, 3], gap="large")
with a:
    t = d.groupby(["proprietaire", "categorie"], observed=True).size().reset_index(name="n")\
        .sort_values("n", ascending=False).head(10)
    ch.figure("6.4", f"Premiers propriétaires, {choix}")
    fig = px.bar(t.iloc[::-1], x="n", y="proprietaire", color="categorie", orientation="h",
                 color_discrete_map=ch.COULEURS_CATEGORIES, category_orders={"categorie": ch.CATEGORIES},
                 labels={"n": "Supports", "proprietaire": "", "categorie": ""})
    fig.update_traces(hovertemplate="%{x:,.0f} supports<extra>%{fullData.name}</extra>")
    fig.update_yaxes(categoryorder="total ascending")
    ch.plot(fig, 440, legend=False)
with b:
    ch.figure("6.5", f"Supports par type de propriétaire, {choix}")
    fig = px.scatter_map(
        d, lat="lat", lon="lon", color="categorie", color_discrete_map=ch.COULEURS_CATEGORIES,
        category_orders={"categorie": ch.CATEGORIES}, hover_name="proprietaire",
        hover_data={"lat": False, "lon": False, "n_operateurs": True, "nature": True, "categorie": False},
        labels={"n_operateurs": "Opérateurs", "nature": "Support", "categorie": ""}, zoom=7.5, map_style="carto-positron",
        center=dict(lat=float(d["lat"].median()), lon=float(d["lon"].median())),
    )
    fig.update_traces(marker=dict(size=7, opacity=0.9))
    ch.plot(fig, 440)
ch.note("", source=True)
