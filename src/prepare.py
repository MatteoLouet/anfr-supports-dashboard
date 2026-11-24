"""Nettoyage et transformation des exports ANFR en tables analytiques (parquet).

Entrée  : data/raw/<AAAAMMJJ>/SUP_*.txt  (voir src/download.py)
Sorties : data/processed/
    supports.parquet   un support mobile par ligne (dernier export)
    historique.parquet supports mobiles agrégés par instantané × département × propriétaire
    qualite.json       journal des contrôles qualité (affiché dans l'application)

Périmètre « mobile » : stations portant au moins un émetteur GSM 900/1800, UMTS,
LTE ou 5G NR (hors GSM-R ferroviaire et bandes LTE privées « P »).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from referentiels import (
    ALIAS_PROPRIETAIRES,
    DEPARTEMENTS,
    est_identifie,
    categorie_proprietaire,
    code_departement,
    normalise,
    operateur_court,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

MOBILE_RE = re.compile(r"^(GSM 900|GSM 1800|UMTS \d+|LTE \d+|5G NR \d+)$")
TECH_RE = {"2G": r"^GSM", "3G": r"^UMTS", "4G": r"^LTE", "5G": r"^5G NR"}


def read(folder: Path, name: str, **kw) -> pd.DataFrame:
    return pd.read_csv(folder / name, sep=";", encoding="utf-8", encoding_errors="replace", dtype=str, **kw)


def dms_to_dec(deg, mn, sec, hemi) -> pd.Series:
    sec = pd.to_numeric(sec.str.replace(",", ".", regex=False), errors="coerce")
    val = pd.to_numeric(deg, errors="coerce") + pd.to_numeric(mn, errors="coerce") / 60 + sec / 3600
    return np.where(hemi.isin(["S", "W"]), -val, val)


def load_snapshot(folder: Path, qualite: dict | None = None) -> pd.DataFrame:
    """Construit la table des supports mobiles d'un export (1 ligne = 1 support)."""
    sup = read(folder, "SUP_SUPPORT.txt")
    sta = read(folder, "SUP_STATION.txt")
    # EMR_DT_SERVICE n'existe pas dans les exports antérieurs à 2019.
    emr = read(folder, "SUP_EMETTEUR.txt", usecols=lambda c: c in {"STA_NM_ANFR", "EMR_LB_SYSTEME", "EMR_DT_SERVICE"})
    if "EMR_DT_SERVICE" not in emr:
        emr["EMR_DT_SERVICE"] = None
    own = read(folder, "SUP_PROPRIETAIRE.txt")
    adm = read(folder, "SUP_EXPLOITANT.txt")
    nat = read(folder, "SUP_NATURE.txt")

    q = {}
    q["lignes_supports_brutes"] = len(sup)
    q["lignes_stations_brutes"] = len(sta)
    q["lignes_emetteurs_brutes"] = len(emr)
    q["doublons_supports_exacts"] = int(sup.duplicated().sum())
    q["doublons_stations"] = int(sta.duplicated("STA_NM_ANFR").sum())
    sup = sup.drop_duplicates()
    sta = sta.drop_duplicates("STA_NM_ANFR")

    # --- Émetteurs mobiles -> technologies par station
    emr["EMR_LB_SYSTEME"] = emr["EMR_LB_SYSTEME"].fillna("").str.strip()
    mob = emr[emr["EMR_LB_SYSTEME"].str.match(MOBILE_RE)].copy()
    q["emetteurs_mobiles"] = len(mob)
    mob["date"] = pd.to_datetime(mob["EMR_DT_SERVICE"], format="%d/%m/%Y", errors="coerce")
    q["emetteurs_mobiles_sans_date"] = int(mob["date"].isna().sum())
    for tech, pat in TECH_RE.items():
        mob[tech] = mob["EMR_LB_SYSTEME"].str.contains(pat)
    tech_sta = mob.groupby("STA_NM_ANFR")[list(TECH_RE)].any()
    first5g = mob[mob["5G"]].groupby("STA_NM_ANFR")["date"].min().rename("date_5g")

    # --- Stations mobiles -> opérateur
    sta = sta[sta["STA_NM_ANFR"].isin(tech_sta.index)].copy()
    sta["operateur"] = sta["ADM_ID"].map(dict(zip(adm["ADM_ID"], adm["ADM_LB_NOM"]))).map(operateur_court)
    sta["date_implantation"] = pd.to_datetime(sta["DTE_IMPLANTATION"], format="%d/%m/%Y", errors="coerce")
    sta = sta.join(tech_sta, on="STA_NM_ANFR").join(first5g, on="STA_NM_ANFR")

    # --- Lien support <-> station mobile
    lien = sup.merge(sta, on="STA_NM_ANFR", how="inner")
    q["stations_mobiles"] = int(sta.shape[0])
    q["stations_mobiles_sans_support"] = int((~sta["STA_NM_ANFR"].isin(sup["STA_NM_ANFR"])).sum())

    # Attributs physiques : une valeur par support
    attr = lien.drop_duplicates("SUP_ID").set_index("SUP_ID")
    df = pd.DataFrame(index=attr.index)
    df["lat"] = dms_to_dec(attr["COR_NB_DG_LAT"], attr["COR_NB_MN_LAT"], attr["COR_NB_SC_LAT"], attr["COR_CD_NS_LAT"])
    df["lon"] = dms_to_dec(attr["COR_NB_DG_LON"], attr["COR_NB_MN_LON"], attr["COR_NB_SC_LON"], attr["COR_CD_EW_LON"])
    df["hauteur_m"] = pd.to_numeric(attr["SUP_NM_HAUT"].str.replace(",", ".", regex=False), errors="coerce")
    df["nature"] = attr["NAT_ID"].map(dict(zip(nat["NAT_ID"], nat["NAT_LB_NOM"]))).fillna("Non renseignée")
    df["proprietaire"] = attr["TPO_ID"].map(dict(zip(own["TPO_ID"], own["TPO_LB"])))
    df["insee"] = attr["COM_CD_INSEE"].str.strip().str.zfill(5)
    df["code_postal"] = attr["ADR_NM_CP"]

    q["supports_mobiles"] = int(len(df))
    q["supports_sans_proprietaire"] = int(df["proprietaire"].isna().sum())
    q["supports_sans_insee"] = int(df["insee"].isna().sum())
    q["supports_sans_coordonnees"] = int(df[["lat", "lon"]].isna().any(axis=1).sum())
    q["supports_hauteur_aberrante"] = int(((df["hauteur_m"] <= 0) | (df["hauteur_m"] > 350)).sum())

    df["proprietaire"] = df["proprietaire"].fillna("Non renseigné").str.strip().replace(ALIAS_PROPRIETAIRES)
    df["proprietaire_identifie"] = df["proprietaire"].map(est_identifie)
    df["categorie"] = df["proprietaire"].map(categorie_proprietaire)
    df.loc[(df["hauteur_m"] <= 0) | (df["hauteur_m"] > 350), "hauteur_m"] = np.nan
    df["dep"] = df["insee"].map(code_departement)
    df["dep_nom"] = df["dep"].map(lambda d: DEPARTEMENTS.get(d, ("Inconnu", "Inconnu"))[0])
    df["region"] = df["dep"].map(lambda d: DEPARTEMENTS.get(d, ("Inconnu", "Inconnu"))[1])
    df["zone"] = np.where(df["region"] == "Outre-mer", "Outre-mer", "Métropole")
    q["supports_departement_inconnu"] = int((df["region"] == "Inconnu").sum())

    # Agrégats par support : opérateurs hébergés, technologies, dates
    ops = pd.crosstab(lien["SUP_ID"], lien["operateur"]).gt(0)
    for op in ["Orange", "SFR", "Bouygues Telecom", "Free Mobile", "Autres (Outre-mer)"]:
        df["op_" + normalise(op).split()[0].lower()] = ops[op] if op in ops else False
    df["n_operateurs"] = ops.sum(axis=1)
    techs = lien.groupby("SUP_ID")[list(TECH_RE)].any()
    for t in TECH_RE:
        df["tech_" + t.lower()] = techs[t].astype(bool)
    dates = lien.groupby("SUP_ID").agg(date_implantation=("date_implantation", "min"), date_5g=("date_5g", "min"))
    df["annee_implantation"] = dates["date_implantation"].dt.year.astype("Int64")
    df["annee_5g"] = dates["date_5g"].dt.year.astype("Int64")
    q["supports_sans_date_implantation"] = int(df["annee_implantation"].isna().sum())

    df = df.reset_index().rename(columns={"SUP_ID": "sup_id"})
    if qualite is not None:
        qualite.update(q)
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    snapshots = sorted(p for p in RAW.iterdir() if p.is_dir() and re.fullmatch(r"\d{8}", p.name))
    if not snapshots:
        raise SystemExit("Aucun export dans data/raw : lancer d'abord python src/download.py")

    historique = []
    qualite: dict = {}
    for i, folder in enumerate(snapshots):
        last = i == len(snapshots) - 1
        print(f"[prep] {folder.name}", flush=True)
        df = load_snapshot(folder, qualite if last else None)
        agg = (
            df.assign(mutualise=df["n_operateurs"] >= 2, quatre_ops=df["n_operateurs"] >= 4)
            .groupby(["dep", "dep_nom", "region", "zone", "proprietaire", "categorie", "proprietaire_identifie"], dropna=False)
            .agg(n_supports=("sup_id", "size"), n_mutualises=("mutualise", "sum"), n_4ops=("quatre_ops", "sum"))
            .reset_index()
        )
        agg.insert(0, "instantane", pd.Timestamp(folder.name))
        historique.append(agg)
        if last:
            df.to_parquet(OUT / "supports.parquet", index=False)
            qualite["export_reference"] = folder.name
            print(f"       {len(df):,} supports mobiles enregistrés")

    pd.concat(historique, ignore_index=True).to_parquet(OUT / "historique.parquet", index=False)
    qualite["instantanes_historiques"] = [p.name for p in snapshots]
    (OUT / "qualite.json").write_text(json.dumps(qualite, indent=2, ensure_ascii=False))
    print("Terminé →", OUT)


if __name__ == "__main__":
    main()
