# Qui contrôle l'infrastructure mobile française ?

Tableau de bord décisionnel Streamlit — projet individuel BDML (Data Visualization, Data Storytelling & BI).

> **Question décisionnelle** : qui contrôle l'infrastructure mobile française, et cette concentration
> crée-t-elle des risques de dépendance ?
>
> **Audience** : décideurs publics du numérique (régulateur, services de l'État, collectivités).

## Récit

| Page | Rôle dans le récit |
|---|---|
| 1 · Problème | Contexte, question, audience, chiffres d'accroche |
| 2 · Données | Source, chaîne de traitement, contrôle qualité, hypothèses, limites |
| 3 · KPIs | Tableau de bord des indicateurs, évolution 2018 → 2026, benchmark territoire vs national |
| 4 · Qui contrôle ? | Bascule opérateurs → TowerCos, acteurs dominants, trajectoires |
| 5 · Dépendances | Opérateur × propriétaire, sites « tout-en-un », 5G, communes captives |
| 6 · Territoires | Indice de dépendance par département (pondérable), carte, classement, zoom |
| 7 · Recommandations | Insights chiffrés, implications, recommandations, limites |

Filtres globaux (barre latérale) : périmètre Métropole / Outre-mer, région, département, opérateur hébergé, technologie.

## Données

- **Jeu** : [Données sur les installations radioélectriques de plus de 5 watts](https://www.data.gouv.fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1)
- **Portail** : data.gouv.fr · **Producteur** : ANFR · **Licence** : Licence Ouverte Etalab
- **Instantanés** : export d'octobre de chaque année, 2018 → 2026 (9 exports)
- **Tables utilisées** : `SUP_SUPPORT`, `SUP_STATION`, `SUP_EMETTEUR`, `SUP_PROPRIETAIRE`, `SUP_EXPLOITANT`, `SUP_NATURE`

## KPIs

| KPI | Définition |
|---|---|
| Part TowerCo | % des supports détenus par une société d'infrastructures (TOTEM, TDF, Hivory, Cellnex, ATC…) |
| Auto-détention opérateurs | % des supports détenus par un opérateur télécom |
| Poids du 1er propriétaire / CR4 | Part du 1er / des 4 premiers propriétaires identifiés |
| HHI | Herfindahl-Hirschman sur les propriétaires identifiés (0-10 000) |
| Taux de mutualisation | % des supports hébergeant ≥ 2 opérateurs |
| Sites « tout-en-un » | % des supports hébergeant les 4 opérateurs (point unique de défaillance) |
| Communes captives | % des communes (≥ 2 supports) dont tous les supports ont le même propriétaire |
| Indice de dépendance | Moyenne pondérée (0-100) de 4 composantes normalisées min-max par département |

## Installation et exécution

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Les données préparées (`data/processed/`, ~2 Mo) sont fournies : l'application se lance directement.

```bash
streamlit run app.py
```

Pour tout régénérer depuis data.gouv.fr (~600 Mo téléchargés, quelques minutes) :

```bash
python src/download.py
python src/prepare.py
```

`python src/download.py --latest` ne télécharge que le dernier export.

## Direction graphique

Reprise de la direction « Données, éditorialement » : papier ivoire `#F5F3EE`, encre `#181818`,
filets `#D8D5CE`, rouge `#CC1505` réservé au signal. Titres en Inter Tight, texte en Inter,
métadonnées en IBM Plex Mono. Chaque graphique est une figure numérotée (titre, phrase « À remarquer »,
source). Palette catégorielle validée (contraste et daltonisme) sur le fond papier :
bleu `#315C9B`, rouge `#CC1505`, vert `#3F8A4E`, ocre `#C99A1E`, neutre `#B9B5AC`.
Thème : `.streamlit/config.toml` ; styles et figures : `src/charts.py`.

## Structure

```
app.py                 navigation + filtres globaux
views/                 une page par étape du récit
src/download.py        ingestion via l'API data.gouv.fr
src/prepare.py         nettoyage, jointures, agrégats, contrôle qualité
src/referentiels.py    départements, catégories de propriétaires, opérateurs
src/analytics.py       chargement, filtres, calcul des KPIs et de l'indice
src/charts.py          style commun des graphiques
data/processed/        supports_*.parquet, historique.parquet, qualite.json
consignes.md           consignes du projet
```

## Hypothèses et limites

- Périmètre mobile : stations portant un émetteur GSM 900/1800, UMTS, LTE ou 5G NR (hors GSM-R et LTE privé).
- Unité d'analyse : le **support physique** (pylône, toit, château d'eau…).
- Les libellés génériques (copropriétés, HLM, particuliers, communes…) sont exclus du HHI car ils regroupent de nombreux propriétaires distincts.
- Les liens capitalistiques entre TowerCos et opérateurs ne sont pas publiés : la concentration par groupe est sous-estimée.
- Défense, Intérieur et Aviation civile sont exclus du registre par l'ANFR.
- Les dates de mise en service des émetteurs sont absentes de l'export 2018.
