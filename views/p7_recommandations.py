import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
df = an.appliquer(an.load_supports(), f)
ch.head("Recommandations", f.libelle(), an.load_qualite()["export_reference"])
st.title("Ce qu'il faut retenir, ce qu'il faut faire")
if df.empty:
    st.warning("Aucun support ne correspond à ces filtres. Élargissez le périmètre dans le panneau de gauche.")
    st.stop()

k = an.kpis(df)
hk = an.kpis_historiques(an.appliquer_historique(an.load_historique(), f))
a, b = hk.iloc[0], hk.iloc[-1]
auto = an.autonomie_operateurs(df)
sc = an.scorecard_departements(df, {c: 1 for c in an.COMPOSANTES})
q4 = df[df["n_operateurs"] >= 4]
p_tc4 = (q4["categorie"] == "TowerCo").mean() if len(q4) else 0
public = (df["categorie"] == "Acteur public").mean()
n_conc = int((sc["hhi"] > 1000).sum()) if len(sc) else 0

st.header("Constats")
constats = [
    ("Le contrôle a changé de mains.",
     f"Les TowerCos détiennent {an.pct(b.part_towerco, 0)} des supports, contre {an.pct(a.part_towerco, 0)} en {a.annee}. "
     f"Les opérateurs n'en possèdent plus que {an.pct(b.part_operateur, 0)}."),
    ("Le marché national reste fragmenté.",
     f"L'indice HHI vaut {an.nombre(k['hhi'])} ({an.niveau_hhi(k['hhi'])}). Le premier propriétaire, {k['top1_nom']}, "
     f"détient {an.pct(k['top1_part'])} des supports."),
    ("La dépendance est locale.",
     (f"{n_conc} départements dépassent le seuil de concentration modérée (HHI supérieur à 1 000). "
      f"Les plus exposés : {', '.join(sc['Département'].head(3))}.") if len(sc) else
     "Le périmètre choisi est trop restreint pour classer les départements."),
    ("Chaque opérateur a son bailleur dominant.",
     "; ".join(f"{r['Opérateur']} : {an.pct(r['Part du principal bailleur'], 0)} de ses sites chez {r['Principal bailleur']}"
               for _, r in auto.iterrows()) + "."),
    ("Les points uniques de défaillance se multiplient.",
     f"{an.pct(k['quatre_ops'], 1)} des supports portent les quatre réseaux ({an.pct(a.quatre_ops, 1)} en {a.annee}). "
     f"{an.pct(p_tc4, 0)} d'entre eux appartiennent à une TowerCo."),
    ("L'acteur public pèse peu.",
     f"Les collectivités et établissements publics détiennent {an.pct(public, 0)} des supports."),
]
for i, (t, txt) in enumerate(constats, 1):
    st.markdown(f"**{i}. {t}** {txt}")

st.header("Ce que cela implique")
st.markdown(
    """
- **Négociation.** Devenus locataires, les opérateurs négocient avec quelques bailleurs. Une hausse des loyers
  pèse d'abord sur l'investissement en zone rurale, la moins rentable.
- **Résilience.** La mutualisation réduit le nombre de pylônes mais rassemble les quatre réseaux sur un même point.
  Une tempête, un sabotage ou un conflit commercial peut couper tous les opérateurs d'une zone.
- **Équité territoriale.** La dépendance est la plus forte là où les alternatives sont les plus rares.
- **Angle mort.** Les fréquences sont régulées ; la propriété des pylônes ne l'est pas. Elle est pourtant devenue stratégique.
"""
)

st.header("Recommandations")
top_deps = ", ".join(sc["Département"].head(5)) if len(sc) else "les départements les plus dépendants"
recos = [
    ("Créer un observatoire des infrastructures passives.",
     "Publier chaque année la part des TowerCos, l'indice HHI et le nombre de supports à quatre opérateurs, "
     "et exiger la déclaration des liens capitalistiques des propriétaires.", "Régulateur, État", "Court terme"),
    ("Cibler les départements les plus dépendants.",
     f"Financer en priorité des pylônes publics ouverts à plusieurs bailleurs dans : {top_deps}.",
     "Préfectures, conseils départementaux", "Moyen terme"),
    ("Encadrer les supports à quatre opérateurs.",
     "Imposer à leurs propriétaires une continuité de service (énergie de secours, redondance) "
     "et un tarif d'accès non discriminatoire.", "Régulateur", "Moyen terme"),
    ("Garder la main sur le foncier public.",
     "Recenser les points hauts publics (châteaux d'eau, bâtiments) et refuser leur cession exclusive à un seul acteur.",
     "Collectivités", "En continu"),
    ("Contrôler les rachats.",
     "Examiner toute acquisition qui porterait un acteur au-delà de 25 % des supports d'un département.",
     "Autorité de la concurrence", "En continu"),
]
st.dataframe(
    [{"Recommandation": f"{i}. {t}", "Contenu": d, "Porteur": who, "Échéance": when}
     for i, (t, d, who, when) in enumerate(recos, 1)],
    hide_index=True, width="stretch",
    column_config={"Contenu": st.column_config.TextColumn(width="large")},
)

st.header("Limites et suites")
st.markdown(
    """
- Le registre ne publie pas qui possède quelle TowerCo. La concentration réelle, par groupe, est donc sous-estimée.
- Les installations de la Défense et de l'Intérieur sont absentes du registre public.
- Suite possible : pondérer la dépendance par la population couverte (INSEE) et par la qualité de service mesurée
  (ANFR, application OpenBarres).
"""
)
