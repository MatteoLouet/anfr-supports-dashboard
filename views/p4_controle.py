import plotly.express as px
import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
df = an.appliquer(an.load_supports(), f)
h = an.appliquer_historique(an.load_historique(), f)
ch.head("Qui contrôle ?", f.libelle(), an.load_qualite()["export_reference"])
st.title("Qui contrôle les points hauts ?")
if df.empty:
    st.warning("Aucun support ne correspond à ces filtres. Élargissez le périmètre dans le panneau de gauche.")
    st.stop()
hk = an.kpis_historiques(h)
a, b = hk.iloc[0], hk.iloc[-1]
st.markdown(
    f"<p class='lead'>En huit ans, la propriété des supports est passée des opérateurs aux TowerCos : "
    f"{an.pct(a.part_towerco, 0)} des supports en {a.annee}, {an.pct(b.part_towerco, 0)} en {b.annee}.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ bascule
st.header("Le transfert")
cat_year = h.groupby(["instantane", "categorie"], as_index=False)["n_supports"].sum()
cat_year["annee"] = cat_year["instantane"].dt.year
cat_year["part"] = cat_year["n_supports"] / cat_year.groupby("annee")["n_supports"].transform("sum") * 100
ch.figure("4.1", "Répartition des supports par type de propriétaire")
fig = px.bar(cat_year, x="annee", y="part", color="categorie",
             category_orders={"categorie": ch.CATEGORIES}, color_discrete_map=ch.COULEURS_CATEGORIES,
             labels={"annee": "", "part": "% des supports", "categorie": ""}, custom_data=["n_supports"])
fig.update_traces(hovertemplate="%{y:.1f} % (%{customdata[0]:,.0f} supports)<extra>%{fullData.name}</extra>")
ch.plot(fig, 400)
ch.note(f"<b>À remarquer.</b> La part des opérateurs chute de {an.pct(a.part_operateur, 0)} à "
        f"{an.pct(b.part_operateur, 0)}. Le saut de 2022 correspond aux transferts de pylônes vers des filiales "
        f"et des fonds d'infrastructures.")

# ------------------------------------------------------------------ acteurs
st.header("Les acteurs aujourd'hui")
n_top = st.slider("Nombre de propriétaires affichés", 5, 25, 15)
top = df.groupby(["proprietaire", "categorie"], observed=True).size().reset_index(name="n")
top = top.sort_values("n", ascending=False).head(n_top)
top["part"] = top["n"] / len(df) * 100
ch.figure("4.2", f"Les {n_top} premiers propriétaires de supports")
fig = px.bar(top.iloc[::-1], x="n", y="proprietaire", color="categorie", orientation="h",
             color_discrete_map=ch.COULEURS_CATEGORIES, category_orders={"categorie": ch.CATEGORIES},
             labels={"n": "Supports", "proprietaire": "", "categorie": ""}, custom_data=["part"])
fig.update_traces(hovertemplate="%{y} : %{x:,.0f} supports (%{customdata[0]:.1f} %)<extra></extra>")
fig.update_yaxes(categoryorder="total ascending")
ch.plot(fig, 26 * n_top + 90)
ch.note("<b>À remarquer.</b> Les TowerCos occupent le haut du classement. Les libellés « Copropriété », "
        "« Société HLM » ou « Société privée » regroupent des milliers de propriétaires distincts.")

# ------------------------------------------------------------------ trajectoires
st.header("Trajectoires")
ident = h[h["proprietaire_identifie"]]
leaders = ident.groupby("proprietaire")["n_supports"].sum().sort_values(ascending=False).index.tolist()
choix = st.multiselect("Propriétaires comparés (4 au plus)", sorted(ident["proprietaire"].unique()),
                       default=leaders[:4], max_selections=4)
traj = ident[ident["proprietaire"].isin(choix)].groupby(["instantane", "proprietaire"], as_index=False)["n_supports"].sum()
traj["annee"] = traj["instantane"].dt.year
ch.figure("4.3", "Supports détenus par les principaux propriétaires identifiés")
fig = px.line(traj, x="annee", y="n_supports", color="proprietaire", markers=True,
              category_orders={"proprietaire": choix}, color_discrete_sequence=ch.SERIES,
              labels={"annee": "", "n_supports": "Supports détenus", "proprietaire": ""})
fig.update_traces(line_width=2, marker_size=8, hovertemplate="%{y:,.0f}<extra>%{fullData.name}</extra>")
ch.plot(fig, 400)
ch.note("<b>À remarquer.</b> TOTEM, Hivory et On Tower France, absents du registre en 2018, comptent aujourd'hui "
        "parmi les premiers propriétaires. Les supports détenus par Orange et SFR reculent au même rythme.")

# ------------------------------------------------------------------ millésimes
st.header("Les sites récents")
recent = df[df["annee_implantation"].between(2010, 2026)]
vint = recent.groupby(["annee_implantation", "categorie"], observed=True).size().reset_index(name="n")
vint["part"] = vint["n"] / vint.groupby("annee_implantation")["n"].transform("sum") * 100
ch.figure("4.4", "Propriétaire actuel des supports, selon leur année d'implantation")
fig = px.bar(vint, x="annee_implantation", y="part", color="categorie",
             color_discrete_map=ch.COULEURS_CATEGORIES, category_orders={"categorie": ch.CATEGORIES},
             labels={"annee_implantation": "Année d'implantation", "part": "% des supports de l'année", "categorie": ""},
             custom_data=["n"])
fig.update_traces(hovertemplate="%{y:.1f} % (%{customdata[0]:,.0f} supports)<extra>%{fullData.name}</extra>")
ch.plot(fig, 380)
tc = recent.assign(tc=recent["categorie"] == "TowerCo").groupby(recent["annee_implantation"] >= 2023)["tc"].mean()
if len(tc) == 2:
    ch.note(f"<b>À remarquer.</b> Les TowerCos détiennent {an.pct(tc[False], 0)} des supports implantés entre 2010 "
            f"et 2022, contre {an.pct(tc[True], 0)} de ceux implantés depuis 2023.")
