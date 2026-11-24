"""Chargement des données préparées, filtres et calcul des indicateurs (KPIs)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from referentiels import normalise

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
OP_COLS = {
    "Orange": "op_orange",
    "SFR": "op_sfr",
    "Bouygues Telecom": "op_bouygues",
    "Free Mobile": "op_free",
}
# Libellés de propriétaires correspondant aux opérateurs eux-mêmes (auto-détention)
PROPRES = {
    "Orange": {"ORANGE", "ORANGE SERVICES FIXES"},
    "SFR": {"SFR"},
    "Bouygues Telecom": {"BOUYGUES"},
    "Free Mobile": {"FREE-MOBILE", "IFW-FREE"},
}
TECHS = ["2G", "3G", "4G", "5G"]


# --------------------------------------------------------------------------- chargement
@st.cache_data(show_spinner="Chargement des supports…")
def load_supports() -> pd.DataFrame:
    df = pd.read_parquet(PROCESSED / "supports.parquet")
    for c in ["dep", "dep_nom", "region", "zone", "categorie", "proprietaire", "nature"]:
        df[c] = df[c].astype("category")
    return df


@st.cache_data
def load_historique() -> pd.DataFrame:
    return pd.read_parquet(PROCESSED / "historique.parquet")


@st.cache_data
def load_qualite() -> dict:
    return json.loads((PROCESSED / "qualite.json").read_text())


def data_ready() -> bool:
    return (PROCESSED / "supports.parquet").exists() and (PROCESSED / "historique.parquet").exists()


# --------------------------------------------------------------------------- filtres
@dataclass
class Filtres:
    zone: str = "Métropole"
    regions: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)
    operateurs: list[str] = field(default_factory=list)
    techno: str = "Toutes"

    def est_national(self) -> bool:
        return not self.regions and not self.deps

    def libelle(self) -> str:
        if self.deps:
            return ", ".join(self.deps) if len(self.deps) <= 3 else f"{len(self.deps)} départements"
        if self.regions:
            return ", ".join(self.regions) if len(self.regions) <= 2 else f"{len(self.regions)} régions"
        return {"Métropole": "France métropolitaine", "Outre-mer": "Outre-mer"}.get(self.zone, "France entière")


def get_filtres() -> Filtres:
    return st.session_state.get("filtres", Filtres())


def appliquer_geo(df: pd.DataFrame, f: Filtres) -> pd.DataFrame:
    m = pd.Series(True, index=df.index)
    if f.zone != "Tout":
        m &= df["zone"] == f.zone
    if f.regions:
        m &= df["region"].isin(f.regions)
    if f.deps:
        m &= df["dep_nom"].isin(f.deps)
    return df[m]


def appliquer(df: pd.DataFrame, f: Filtres) -> pd.DataFrame:
    """Filtres complets sur la table des supports (géographie + opérateur + techno)."""
    df = appliquer_geo(df, f)
    if f.operateurs:
        df = df[df[[OP_COLS[o] for o in f.operateurs]].any(axis=1)]
    if f.techno != "Toutes":
        df = df[df["tech_" + f.techno.lower()]]
    return df


def appliquer_historique(h: pd.DataFrame, f: Filtres) -> pd.DataFrame:
    return appliquer_geo(h, f)


# --------------------------------------------------------------------------- indicateurs
def parts_proprietaires(df: pd.DataFrame, identifies_seulement: bool = False) -> pd.Series:
    d = df[df["proprietaire_identifie"]] if identifies_seulement else df
    s = d.groupby("proprietaire", observed=True).size().sort_values(ascending=False)
    return s / len(df) if len(df) else s


def hhi(df: pd.DataFrame) -> float:
    """Indice Herfindahl-Hirschman (0-10 000) sur les propriétaires identifiés.

    Les libellés génériques (copropriétés, HLM, particuliers, communes…) regroupent
    des milliers d'entités distinctes : on les considère atomisés (contribution ≈ 0).
    """
    if df.empty:
        return float("nan")
    parts = parts_proprietaires(df, identifies_seulement=True) * 100
    return float((parts**2).sum())


def hhi_from_counts(counts: pd.Series, identifie: pd.Series) -> float:
    total = counts.sum()
    if total == 0:
        return float("nan")
    parts = counts[identifie] / total * 100
    return float((parts**2).sum())


def niveau_hhi(v: float) -> str:
    """Seuils usuels des autorités de concurrence."""
    if np.isnan(v):
        return "—"
    if v < 1000:
        return "peu concentré"
    if v < 1800:
        return "modérément concentré"
    return "très concentré"


def kpis(df: pd.DataFrame) -> dict:
    n = len(df)
    if n == 0:
        return {}
    parts = parts_proprietaires(df, identifies_seulement=True)
    towerco = (df["categorie"] == "TowerCo").mean()
    propre = (df["categorie"] == "Opérateur (en propre)").mean()
    communes = communes_dependance(df)
    return {
        "n_supports": n,
        "hhi": hhi(df),
        "top1_nom": parts.index[0] if len(parts) else "—",
        "top1_part": float(parts.iloc[0]) if len(parts) else 0.0,
        "cr4": float(parts.iloc[:4].sum()),
        "part_towerco": float(towerco),
        "part_operateur": float(propre),
        "mutualisation": float((df["n_operateurs"] >= 2).mean()),
        "quatre_ops": float((df["n_operateurs"] >= 4).mean()),
        "n_quatre_ops": int((df["n_operateurs"] >= 4).sum()),
        "communes_mono": float(communes["mono_proprietaire"].mean()) if len(communes) else 0.0,
        "n_communes": int(len(communes)),
    }


def kpis_historiques(h: pd.DataFrame) -> pd.DataFrame:
    """KPIs par instantané annuel (à partir de la table agrégée)."""
    rows = []
    for date, g in h.groupby("instantane"):
        par_prop = g.groupby(["proprietaire", "proprietaire_identifie"])["n_supports"].sum().reset_index()
        total = par_prop["n_supports"].sum()
        ident = par_prop[par_prop["proprietaire_identifie"]].sort_values("n_supports", ascending=False)
        cat = g.groupby("categorie")["n_supports"].sum() / total
        rows.append(
            {
                "instantane": date,
                "annee": date.year,
                "n_supports": int(total),
                "hhi": float(((ident["n_supports"] / total * 100) ** 2).sum()),
                "top1_nom": ident["proprietaire"].iloc[0] if len(ident) else "—",
                "top1_part": float(ident["n_supports"].iloc[0] / total) if len(ident) else 0,
                "cr4": float(ident["n_supports"].iloc[:4].sum() / total),
                "part_towerco": float(cat.get("TowerCo", 0)),
                "part_operateur": float(cat.get("Opérateur (en propre)", 0)),
                "mutualisation": float(g["n_mutualises"].sum() / total),
                "quatre_ops": float(g["n_4ops"].sum() / total),
            }
        )
    return pd.DataFrame(rows)


def communes_dependance(df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par commune : nb de supports, nb de propriétaires, propriétaire dominant."""
    if df.empty:
        return pd.DataFrame(columns=["insee", "n_supports", "n_proprietaires", "mono_proprietaire"])
    g = df.groupby("insee", observed=True)
    out = pd.DataFrame(
        {
            "n_supports": g.size(),
            "n_proprietaires": g["proprietaire"].nunique(),
            "dep": g["dep"].first(),
            "dep_nom": g["dep_nom"].first(),
            "proprietaire_principal": g["proprietaire"].agg(lambda s: s.value_counts().index[0]),
            "identifie": g["proprietaire_identifie"].all(),
        }
    )
    # Commune dépendante : ≥ 2 supports, tous détenus par la même entreprise identifiée.
    out["mono_proprietaire"] = (out["n_supports"] >= 2) & (out["n_proprietaires"] == 1) & out["identifie"]
    return out.reset_index()


def dependance_operateurs(df: pd.DataFrame, top: int = 8) -> pd.DataFrame:
    """Part des sites de chaque opérateur hébergés par chaque propriétaire."""
    rows = []
    for op, col in OP_COLS.items():
        d = df[df[col]]
        if d.empty:
            continue
        s = d["proprietaire"].value_counts(normalize=True)
        for prop, p in s.items():
            rows.append({"operateur": op, "proprietaire": prop, "part": p, "n": int((d["proprietaire"] == prop).sum())})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    top_props = df[df["proprietaire_identifie"]]["proprietaire"].value_counts().index[:top].tolist()
    out["proprietaire"] = out["proprietaire"].astype(str).where(out["proprietaire"].isin(top_props), "Autres propriétaires")
    return out.groupby(["operateur", "proprietaire"], as_index=False)[["part", "n"]].sum()


def autonomie_operateurs(df: pd.DataFrame) -> pd.DataFrame:
    """Pour chaque opérateur : part des sites détenus en propre vs chez un tiers."""
    rows = []
    for op, col in OP_COLS.items():
        d = df[df[col]]
        if d.empty:
            continue
        propre = d["proprietaire"].astype(str).map(normalise).isin(PROPRES[op])
        towerco = d["categorie"] == "TowerCo"
        top = d.loc[towerco, "proprietaire"].value_counts()
        rows.append(
            {
                "Opérateur": op,
                "Sites": len(d),
                "En propre": propre.mean(),
                "Chez une TowerCo": towerco.mean(),
                "Autres tiers": 1 - propre.mean() - towerco.mean(),
                "Principal bailleur": top.index[0] if len(top) else "—",
                "Part du principal bailleur": (top.iloc[0] / len(d)) if len(top) else 0.0,
            }
        )
    return pd.DataFrame(rows)


COMPOSANTES = {
    "hhi": "Concentration des propriétaires (HHI)",
    "top1_part": "Poids du 1er propriétaire",
    "communes_mono": "Communes sous propriétaire unique",
    "quatre_ops": "Sites hébergeant les 4 opérateurs",
}


def scorecard_departements(df: pd.DataFrame, poids: dict[str, float]) -> pd.DataFrame:
    """Indice de dépendance (0-100) par département, composantes normalisées min-max."""
    rows = []
    for (dep, nom, region), d in df.groupby(["dep", "dep_nom", "region"], observed=True):
        if len(d) < 20:  # trop peu de supports pour un indicateur stable
            continue
        k = kpis(d)
        rows.append(
            {
                "dep": dep, "Département": nom, "Région": region,
                "Supports": k["n_supports"], "hhi": k["hhi"], "top1_nom": k["top1_nom"],
                "top1_part": k["top1_part"], "communes_mono": k["communes_mono"],
                "quatre_ops": k["quatre_ops"], "part_towerco": k["part_towerco"],
                "lat": d["lat"].median(), "lon": d["lon"].median(),
            }
        )
    sc = pd.DataFrame(rows)
    if sc.empty:
        return sc
    total = sum(poids.values()) or 1
    score = 0
    for c, w in poids.items():
        x = sc[c]
        rng = x.max() - x.min()
        sc[c + "_norm"] = (x - x.min()) / rng if rng else 0.0
        score = score + w * sc[c + "_norm"]
    sc["Indice de dépendance"] = (score / total * 100).round(1)
    sc["Rang"] = sc["Indice de dépendance"].rank(ascending=False, method="min").astype(int)
    return sc.sort_values("Indice de dépendance", ascending=False)


# --------------------------------------------------------------------------- format
def pct(x: float, d: int = 1) -> str:
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x * 100:.{d}f}\u202f%".replace(".", ",")


def nombre(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")
