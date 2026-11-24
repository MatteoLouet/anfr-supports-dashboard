import streamlit as st

import analytics as an
import charts as ch

f = an.get_filtres()
df = an.appliquer(an.load_supports(), f)
hist = an.kpis_historiques(an.appliquer_historique(an.load_historique(), f))
q = an.load_qualite()
k = an.kpis(df)

ch.head("Le problème", f.libelle(), q["export_reference"])
if not k:
    st.warning("Aucun support ne correspond à ces filtres. Élargissez le périmètre dans le panneau de gauche.")
    st.stop()
h0, h1 = hist.iloc[0], hist.iloc[-1]

st.title("Qui contrôle l'infrastructure mobile française ?")
st.markdown(
    f"<p class='lead'>En {h0.annee}, les opérateurs possédaient {an.pct(h0.part_operateur, 0)} des pylônes et toits "
    f"qui portent leurs antennes. En {h1.annee}, {an.pct(h1.part_operateur, 0)}. Cette concentration crée-t-elle "
    f"des risques de dépendance ?</p>",
    unsafe_allow_html=True,
)

ch.kpis([
    ("Supports détenus par une TowerCo", an.pct(h1.part_towerco, 0),
     f"{(h1.part_towerco - h0.part_towerco) * 100:+.0f} pts depuis {h0.annee}", True),
    ("Supports détenus par les opérateurs", an.pct(h1.part_operateur, 0),
     f"{(h1.part_operateur - h0.part_operateur) * 100:+.0f} pts depuis {h0.annee}", False),
    ("Premier propriétaire", k["top1_nom"], f"{an.pct(k['top1_part'])} des supports", False),
    ("Supports partagés par les 4 opérateurs", an.pct(h1.quatre_ops, 0),
     f"{(h1.quatre_ops - h0.quatre_ops) * 100:+.1f} pts depuis {h0.annee}", True),
])

left, right = st.columns([3, 2], gap="large")
with left:
    st.header("Ce qui a changé")
    st.markdown(
        """
Orange, SFR, Bouygues Telecom et Free ont vendu l'essentiel de leurs infrastructures passives
(pylônes, mâts, toits loués) à des **sociétés d'infrastructures**, les TowerCos. Les opérateurs
sont devenus locataires des points hauts qui portent leurs réseaux.

Pour l'État et les collectivités, la question devient une question de gouvernance :

- **Pouvoir de marché.** Une poignée de bailleurs fixe-t-elle le prix d'accès aux points hauts ?
- **Résilience.** Combien de pylônes portent les quatre réseaux à la fois ?
- **Équité territoriale.** Quels départements dépendent d'un seul propriétaire ?
- **Levier public.** Où l'acteur public possède-t-il encore le foncier ?
"""
    )
with right:
    st.header("Pour qui")
    st.markdown(
        """
Les décideurs publics du numérique : régulateur des télécoms, services de l'État en région,
conseils départementaux et régionaux.

Trois décisions à éclairer :

1. Surveiller ou encadrer les TowerCos dominantes.
2. Choisir les territoires où diversifier les points hauts.
3. Cibler l'investissement public dans des pylônes ouverts à tous.
"""
    )

st.header("Le parcours")
st.markdown(
    """
<div class="steps">
<div><b>Données</b>Registre ANFR des antennes, un instantané par an de 2018 à 2026.</div>
<div><b>Indicateurs</b>Concentration, part des TowerCos, mutualisation, communes captives.</div>
<div><b>Qui contrôle ?</b>Le transfert des opérateurs vers les TowerCos.</div>
<div><b>Dépendances</b>Quel opérateur loue chez quel bailleur.</div>
<div><b>Territoires</b>Un indice de dépendance par département.</div>
<div><b>Recommandations</b>Ce que l'action publique peut faire.</div>
</div>
""",
    unsafe_allow_html=True,
)
