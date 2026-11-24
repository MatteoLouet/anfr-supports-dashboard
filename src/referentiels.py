"""Référentiels statiques : départements, régions, catégories de propriétaires, opérateurs."""
from __future__ import annotations

import unicodedata

# Code département -> (nom, région)
DEPARTEMENTS: dict[str, tuple[str, str]] = {
    "01": ("Ain", "Auvergne-Rhône-Alpes"), "02": ("Aisne", "Hauts-de-France"),
    "03": ("Allier", "Auvergne-Rhône-Alpes"), "04": ("Alpes-de-Haute-Provence", "Provence-Alpes-Côte d'Azur"),
    "05": ("Hautes-Alpes", "Provence-Alpes-Côte d'Azur"), "06": ("Alpes-Maritimes", "Provence-Alpes-Côte d'Azur"),
    "07": ("Ardèche", "Auvergne-Rhône-Alpes"), "08": ("Ardennes", "Grand Est"),
    "09": ("Ariège", "Occitanie"), "10": ("Aube", "Grand Est"),
    "11": ("Aude", "Occitanie"), "12": ("Aveyron", "Occitanie"),
    "13": ("Bouches-du-Rhône", "Provence-Alpes-Côte d'Azur"), "14": ("Calvados", "Normandie"),
    "15": ("Cantal", "Auvergne-Rhône-Alpes"), "16": ("Charente", "Nouvelle-Aquitaine"),
    "17": ("Charente-Maritime", "Nouvelle-Aquitaine"), "18": ("Cher", "Centre-Val de Loire"),
    "19": ("Corrèze", "Nouvelle-Aquitaine"), "2A": ("Corse-du-Sud", "Corse"),
    "2B": ("Haute-Corse", "Corse"), "21": ("Côte-d'Or", "Bourgogne-Franche-Comté"),
    "22": ("Côtes-d'Armor", "Bretagne"), "23": ("Creuse", "Nouvelle-Aquitaine"),
    "24": ("Dordogne", "Nouvelle-Aquitaine"), "25": ("Doubs", "Bourgogne-Franche-Comté"),
    "26": ("Drôme", "Auvergne-Rhône-Alpes"), "27": ("Eure", "Normandie"),
    "28": ("Eure-et-Loir", "Centre-Val de Loire"), "29": ("Finistère", "Bretagne"),
    "30": ("Gard", "Occitanie"), "31": ("Haute-Garonne", "Occitanie"),
    "32": ("Gers", "Occitanie"), "33": ("Gironde", "Nouvelle-Aquitaine"),
    "34": ("Hérault", "Occitanie"), "35": ("Ille-et-Vilaine", "Bretagne"),
    "36": ("Indre", "Centre-Val de Loire"), "37": ("Indre-et-Loire", "Centre-Val de Loire"),
    "38": ("Isère", "Auvergne-Rhône-Alpes"), "39": ("Jura", "Bourgogne-Franche-Comté"),
    "40": ("Landes", "Nouvelle-Aquitaine"), "41": ("Loir-et-Cher", "Centre-Val de Loire"),
    "42": ("Loire", "Auvergne-Rhône-Alpes"), "43": ("Haute-Loire", "Auvergne-Rhône-Alpes"),
    "44": ("Loire-Atlantique", "Pays de la Loire"), "45": ("Loiret", "Centre-Val de Loire"),
    "46": ("Lot", "Occitanie"), "47": ("Lot-et-Garonne", "Nouvelle-Aquitaine"),
    "48": ("Lozère", "Occitanie"), "49": ("Maine-et-Loire", "Pays de la Loire"),
    "50": ("Manche", "Normandie"), "51": ("Marne", "Grand Est"),
    "52": ("Haute-Marne", "Grand Est"), "53": ("Mayenne", "Pays de la Loire"),
    "54": ("Meurthe-et-Moselle", "Grand Est"), "55": ("Meuse", "Grand Est"),
    "56": ("Morbihan", "Bretagne"), "57": ("Moselle", "Grand Est"),
    "58": ("Nièvre", "Bourgogne-Franche-Comté"), "59": ("Nord", "Hauts-de-France"),
    "60": ("Oise", "Hauts-de-France"), "61": ("Orne", "Normandie"),
    "62": ("Pas-de-Calais", "Hauts-de-France"), "63": ("Puy-de-Dôme", "Auvergne-Rhône-Alpes"),
    "64": ("Pyrénées-Atlantiques", "Nouvelle-Aquitaine"), "65": ("Hautes-Pyrénées", "Occitanie"),
    "66": ("Pyrénées-Orientales", "Occitanie"), "67": ("Bas-Rhin", "Grand Est"),
    "68": ("Haut-Rhin", "Grand Est"), "69": ("Rhône", "Auvergne-Rhône-Alpes"),
    "70": ("Haute-Saône", "Bourgogne-Franche-Comté"), "71": ("Saône-et-Loire", "Bourgogne-Franche-Comté"),
    "72": ("Sarthe", "Pays de la Loire"), "73": ("Savoie", "Auvergne-Rhône-Alpes"),
    "74": ("Haute-Savoie", "Auvergne-Rhône-Alpes"), "75": ("Paris", "Île-de-France"),
    "76": ("Seine-Maritime", "Normandie"), "77": ("Seine-et-Marne", "Île-de-France"),
    "78": ("Yvelines", "Île-de-France"), "79": ("Deux-Sèvres", "Nouvelle-Aquitaine"),
    "80": ("Somme", "Hauts-de-France"), "81": ("Tarn", "Occitanie"),
    "82": ("Tarn-et-Garonne", "Occitanie"), "83": ("Var", "Provence-Alpes-Côte d'Azur"),
    "84": ("Vaucluse", "Provence-Alpes-Côte d'Azur"), "85": ("Vendée", "Pays de la Loire"),
    "86": ("Vienne", "Nouvelle-Aquitaine"), "87": ("Haute-Vienne", "Nouvelle-Aquitaine"),
    "88": ("Vosges", "Grand Est"), "89": ("Yonne", "Bourgogne-Franche-Comté"),
    "90": ("Territoire de Belfort", "Bourgogne-Franche-Comté"), "91": ("Essonne", "Île-de-France"),
    "92": ("Hauts-de-Seine", "Île-de-France"), "93": ("Seine-Saint-Denis", "Île-de-France"),
    "94": ("Val-de-Marne", "Île-de-France"), "95": ("Val-d'Oise", "Île-de-France"),
    "971": ("Guadeloupe", "Outre-mer"), "972": ("Martinique", "Outre-mer"),
    "973": ("Guyane", "Outre-mer"), "974": ("La Réunion", "Outre-mer"),
    "975": ("Saint-Pierre-et-Miquelon", "Outre-mer"), "976": ("Mayotte", "Outre-mer"),
    "977": ("Saint-Barthélemy", "Outre-mer"), "978": ("Saint-Martin", "Outre-mer"),
    "986": ("Wallis-et-Futuna", "Outre-mer"), "987": ("Polynésie française", "Outre-mer"),
    "988": ("Nouvelle-Calédonie", "Outre-mer"),
}


def code_departement(insee: str | None) -> str | None:
    """Déduit le code département d'un code commune INSEE."""
    if not isinstance(insee, str) or len(insee) < 2:
        return None
    insee = insee.strip().zfill(5)
    if insee.startswith(("97", "98")):
        return insee[:3]
    return insee[:2]


def normalise(label: str | None) -> str:
    if not isinstance(label, str):
        return ""
    label = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode()
    return " ".join(label.upper().split())


# Catégories de propriétaires de supports (libellés ANFR normalisés)
TOWERCOS = {
    "TOTEM", "TDF", "HIVORY", "ON TOWER FRANCE", "ATC FRANCE", "CELLNEX",
    "PHOENIX FRANCE INFRASTRUCTURES", "TOWERCAST", "VALOCIME", "TOWEO", "NEXT TOWER",
    "ITAS TIM", "ONE CAST", "FPS TOWERS",
}
OPERATEURS = {
    "ORANGE", "ORANGE SERVICES FIXES", "SFR", "BOUYGUES", "FREE-MOBILE", "9 CEGETEL",
    "COMPLETEL", "BOLLORE", "BELGACOM", "DIGICEL", "ONATI", "OUTREMER TELECOM",
    "DAUPHIN TELECOM", "FRANCE CARAIBES MOBILES", "STE REUNIONN. DE RADIOTELEPH.",
    "TELCO OI", "ZEOP", "PACIFIC MOBILE TELECOM", "VITI", "OFFICE DES POSTES ET TELECOM",
    "SERVICE DES POSTES ET TELECOM", "HUBONE", "MEDIASERV", "ALTITUDE TELECOM",
    "IFW-FREE", "TIKIPHONE", "MADIACOM", "EUTELSAT", "ONEWEB", "GLOBECAST", "EXPERTMEDIA",
}
PUBLICS = {
    "COMMUNE, COMMUNAUTE DE COMMUNE", "CONSEIL DEPARTEMENTAL", "CONSEIL REGIONAL",
    "ETS PUBLIC , MINIST, SYND MIXT", "SYNDICAT DES EAUX, ADDUCTION", "DDE",
    "SDIS, SECOURS, INCENDIE", "GENDARMERIE", "INTERIEUR", "AVIATION CIVILE", "METEO",
    "ANFR", "CROSS", "PHARES ET BALISES", "VOIES NAVIGABLES DE FRANCE", "GUYANE NUMERIQUE",
    "REUNION NUMERIQUE", "REGIE HTES PYRENEES HAUT DEBIT", "SYADEN", "DGEN",
    "SOCIETE DES GRANDS PROJETS", "LA POSTE", "ETAT MINISTERE", "ETAT, MINISTERE",
}
GRANDS_RESEAUX = {
    "SNCF RESEAU", "SNCF", "RATP", "RTE", "EDF OU GDF", "SOCIETES D'AUTOROUTES",
    "ELECTRICITE DE TAHITI",
}

CATEGORIES = [
    "TowerCo",
    "Opérateur (en propre)",
    "Acteur public",
    "Transport et énergie",
    "Privés et particuliers",
]
COULEURS_CATEGORIES = {  # palette validée sur fond papier ; "privés" = neutre (catégorie résiduelle)
    "TowerCo": "#315C9B",
    "Opérateur (en propre)": "#CC1505",
    "Acteur public": "#3F8A4E",
    "Transport et énergie": "#C99A1E",
    "Privés et particuliers": "#B9B5AC",
}


def categorie_proprietaire(label: str | None) -> str:
    n = normalise(label)
    if n in TOWERCOS:
        return CATEGORIES[0]
    if n in OPERATEURS:
        return CATEGORIES[1]
    if n in PUBLICS:
        return CATEGORIES[2]
    if n in GRANDS_RESEAUX:
        return CATEGORIES[3]
    return CATEGORIES[4]


# Opérateurs mobiles (exploitants ANFR) -> libellé court
OPERATEURS_MOBILES = {
    "ORANGE": "Orange",
    "SFR": "SFR",
    "BOUYGUES TELECOM": "Bouygues Telecom",
    "FREE MOBILE": "Free Mobile",
}
OPERATEURS_COURTS = ["Orange", "SFR", "Bouygues Telecom", "Free Mobile"]
COULEURS_OPERATEURS = {
    "Orange": "#C99A1E", "SFR": "#CC1505", "Bouygues Telecom": "#315C9B",
    "Free Mobile": "#3F8A4E", "Autres (Outre-mer)": "#B9B5AC",
}


def operateur_court(label: str | None) -> str:
    return OPERATEURS_MOBILES.get(normalise(label), "Autres (Outre-mer)")


# Libellés de propriétaires qui désignent une CLASSE d'acteurs (milliers d'entités
# distinctes) et non une entreprise unique : exclus du calcul de concentration.
GENERIQUES = {
    "COPROPRIETE, SYNDIC, SCI", "SOCIETE HLM", "SOCIETE PRIVEE", "SOCIETE PRIVEE SA",
    "PARTICULIER", "COMMUNE, COMMUNAUTE DE COMMUNE", "CONSEIL DEPARTEMENTAL",
    "CONSEIL REGIONAL", "SYNDICAT DES EAUX, ADDUCTION", "ETABLISSEMENT DE SOINS",
    "COOPERATIVE AGRICOLE, VINICOLE", "ASSOCIATION", "AUTRES", "NON RENSEIGNE",
    "CCI,CH METIERS,PORT AUT,AEROP", "ETS PUBLIC , MINIST, SYND MIXT", "ETAT MINISTERE",
    "ETAT, MINISTERE", "TITULAIRE PROGRAMME RADIO/TV", "SOCIETES D'AUTOROUTES",
}

ALIAS_PROPRIETAIRES = {"Société Privée SA": "Société Privée", "Etat Ministère": "Etat, Ministère"}


def est_identifie(label: str | None) -> bool:
    """Vrai si le propriétaire est une entité unique identifiable."""
    return normalise(label) not in GENERIQUES
