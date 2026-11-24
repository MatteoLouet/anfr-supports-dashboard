import plotly.express as px
import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
df = an.appliquer(an.load_supports(), f)
ch.head("Dépendances", f.libelle(), an.load_qualite()["export_reference"])
st.title("Qui dépend de qui ?")
if df.empty:
    st.warning("Aucun support ne correspond à ces filtres. Élargissez le périmètre dans le panneau de gauche.")
    st.stop()

auto = an.autonomie_operateurs(df)
worst = auto.sort_values("Part du principal bailleur", ascending=False).iloc[0]
st.markdown(
    f"<p class='lead'>Les opérateurs possèdent au plus {an.pct(auto['En propre'].max(), 0)} de leurs sites. {worst['Opérateur']} "
    f"loue {an.pct(worst['Part du principal bailleur'], 0)} des siens à un seul bailleur, {worst['Principal bailleur']}.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ opérateurs
st.header("Des opérateurs locataires")
long = auto.melt(id_vars="Opérateur", value_vars=["En propre", "Chez une TowerCo", "Autres tiers"],
                 var_name="Statut", value_name="part")
long["part"] *= 100
ch.figure("5.1", "Qui possède les supports utilisés par chaque opérateur")
fig = px.bar(long, y="Opérateur", x="part", color="Statut", orientation="h",
             color_discrete_map={"En propre": ch.ACCENT, "Chez une TowerCo": ch.BLUE, "Autres tiers": ch.NEUTRE},
             labels={"part": "% des sites de l'opérateur", "Opérateur": ""})
fig.update_traces(hovertemplate="%{x:.1f} %<extra>%{fullData.name}</extra>")
ch.plot(fig, 290)
st.dataframe(
    auto[["Opérateur", "Sites", "En propre", "Chez une TowerCo", "Principal bailleur", "Part du principal bailleur"]],
    hide_index=True, width="stretch",
    column_config={
        "Sites": st.column_config.NumberColumn(format="localized"),
        "En propre": st.column_config.NumberColumn(format="percent"),
        "Chez une TowerCo": st.column_config.NumberColumn(format="percent"),
        "Part du principal bailleur": st.column_config.NumberColumn(format="percent"),
    },
)
ch.note(f"<b>À remarquer.</b> La part rouge, les sites détenus en propre, ne dépasse pas {an.pct(auto['En propre'].max(), 0)}. "
        f"Entre {an.pct(auto['Chez une TowerCo'].min(), 0)} et {an.pct(auto['Chez une TowerCo'].max(), 0)} des sites "
        "de chaque opérateur sont loués à une TowerCo.")

# ------------------------------------------------------------------ matrice
st.header("Opérateurs et bailleurs")
top_n = st.slider("Propriétaires identifiés affichés", 4, 12, 8)
mat = an.dependance_operateurs(df, top=top_n)
piv = mat.pivot(index="operateur", columns="proprietaire", values="part").fillna(0) * 100
order = [c for c in mat.groupby("proprietaire")["n"].sum().sort_values(ascending=False).index if c != "Autres propriétaires"]
piv = piv[order + (["Autres propriétaires"] if "Autres propriétaires" in piv else [])]
ch.figure("5.2", "Part des sites de chaque opérateur hébergée par chaque propriétaire")
fig = px.imshow(piv, text_auto=".0f", aspect="auto", color_continuous_scale=ch.SEQ, labels=dict(x="", y="", color="%"))
fig.update_traces(hovertemplate="%{y} chez %{x} : %{z:.1f} % des sites<extra></extra>", xgap=2, ygap=2)
fig.update_xaxes(side="top", tickangle=-30, linecolor="rgba(0,0,0,0)", ticks="")
fig.update_layout(coloraxis_colorbar=dict(thickness=10, outlinewidth=0))
ch.plot(fig, 330, legend=False)
ch.note("<b>À remarquer.</b> Chaque opérateur a un bailleur dominant, souvent celui qui a racheté ses anciens pylônes. "
        "La colonne « Autres propriétaires » regroupe surtout des toits privés.")

# ------------------------------------------------------------------ points uniques
st.header("Les supports à quatre opérateurs")
q4 = df[df["n_operateurs"] >= 4]
c1, c2 = st.columns(2, gap="large")
with c1:
    dist = df.assign(n=df["n_operateurs"].clip(upper=4).astype(str)).groupby(["n", "categorie"], observed=True)\
        .size().reset_index(name="supports")
    ch.figure("5.3", "Nombre d'opérateurs hébergés par support")
    fig = px.bar(dist, x="n", y="supports", color="categorie", color_discrete_map=ch.COULEURS_CATEGORIES,
                 category_orders={"categorie": ch.CATEGORIES, "n": ["1", "2", "3", "4"]},
                 labels={"n": "Opérateurs sur le support", "supports": "Supports", "categorie": ""})
    fig.update_traces(hovertemplate="%{y:,.0f} supports<extra>%{fullData.name}</extra>")
    ch.plot(fig, 380)
with c2:
    own4 = q4["proprietaire"].value_counts().head(10).rename_axis("proprietaire").reset_index(name="n")
    own4["part"] = own4["n"] / max(len(q4), 1) * 100
    ch.figure("5.4", f"Propriétaires des {an.nombre(len(q4))} supports à quatre opérateurs")
    fig = px.bar(own4.iloc[::-1], x="n", y="proprietaire", orientation="h", custom_data=["part"],
                 labels={"n": "Supports", "proprietaire": ""})
    fig.update_traces(marker_color=ch.BLUE, hovertemplate="%{x:,.0f} supports (%{customdata[0]:.1f} %)<extra></extra>")
    ch.plot(fig, 380, legend=False)
if len(q4):
    p_tc = (q4["categorie"] == "TowerCo").mean()
    ch.flag(f"{an.pct(p_tc, 0)} des supports qui portent les quatre réseaux appartiennent à une TowerCo. "
            "Une panne, un litige ou une hausse de loyer sur l'un d'eux touche tous les abonnés de la zone.")
    ch.note("", source=True)

# ------------------------------------------------------------------ 5G
st.header("La 5G")
g = df.assign(Réseau=df["tech_5g"].map({True: "Avec 5G", False: "Sans 5G"}))
comp = g.groupby(["Réseau", "categorie"], observed=True).size().reset_index(name="n")
comp["part"] = comp["n"] / comp.groupby("Réseau")["n"].transform("sum") * 100
ch.figure("5.5", "Propriétaires des supports, avec et sans 5G")
fig = px.bar(comp, y="Réseau", x="part", color="categorie", orientation="h",
             color_discrete_map=ch.COULEURS_CATEGORIES, category_orders={"categorie": ch.CATEGORIES},
             labels={"part": "% des supports", "Réseau": "", "categorie": ""})
fig.update_traces(hovertemplate="%{x:.1f} %<extra>%{fullData.name}</extra>")
ch.plot(fig, 240)
s5, s0 = g[g["tech_5g"]], g[~g["tech_5g"]]
if len(s5) and len(s0):
    ch.note(f"<b>À remarquer.</b> Les TowerCos détiennent {an.pct((s5['categorie'] == 'TowerCo').mean(), 0)} des "
            f"supports 5G, contre {an.pct((s0['categorie'] == 'TowerCo').mean(), 0)} des autres.")

# ------------------------------------------------------------------ communes
st.header("Les communes captives")
com = an.communes_dependance(df)
mono = com[com["mono_proprietaire"]]
ch.kpis([
    ("Communes avec au moins 2 supports", an.nombre((com["n_supports"] >= 2).sum()), None, False),
    ("Dont captives d'un propriétaire", an.nombre(len(mono)), None, False),
    ("Communes à support unique", an.nombre((com["n_supports"] == 1).sum()),
     "un seul support porte tout le réseau mobile", False),
])
if len(mono):
    par = mono["proprietaire_principal"].value_counts().head(10).rename_axis("Propriétaire").reset_index(name="Communes captives")
    a, b = st.columns([2, 3], gap="large")
    a.dataframe(par, hide_index=True, width="stretch")
    b.dataframe(
        mono.sort_values("n_supports", ascending=False)[["insee", "dep_nom", "n_supports", "proprietaire_principal"]]
        .rename(columns={"insee": "Code INSEE", "dep_nom": "Département", "n_supports": "Supports",
                         "proprietaire_principal": "Propriétaire unique"}),
        hide_index=True, width="stretch", height=320,
    )
