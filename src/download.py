"""Téléchargement des exports ANFR depuis data.gouv.fr.

Jeu : « Données sur les installations radioélectriques de plus de 5 watts »
https://www.data.gouv.fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1

Le script interroge l'API data.gouv.fr, puis télécharge pour chaque année
l'export d'octobre (ou le plus proche avant) : un instantané annuel comparable.
Seules les tables utiles au projet sont extraites.

Usage :
    python src/download.py              # toutes les années disponibles depuis 2018
    python src/download.py --latest     # uniquement le dernier export
"""
from __future__ import annotations

import argparse
import io
import re
import zipfile
from pathlib import Path

import requests

DATASET_API = (
    "https://www.data.gouv.fr/api/1/datasets/"
    "donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1/"
)
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
TABLES = {
    "SUP_SUPPORT.txt",
    "SUP_STATION.txt",
    "SUP_EMETTEUR.txt",
    "SUP_PROPRIETAIRE.txt",
    "SUP_EXPLOITANT.txt",
    "SUP_NATURE.txt",
}
FIRST_YEAR = 2018
PATTERN = re.compile(r"/(\d{8})-export-etalab-(data|ref)\.zip$")


def list_exports() -> dict[str, dict[str, str]]:
    """Retourne {AAAAMMJJ: {"data": url, "ref": url}} pour les exports complets."""
    resources = requests.get(DATASET_API, timeout=60).json()["resources"]
    exports: dict[str, dict[str, str]] = {}
    for res in resources:
        m = PATTERN.search(res["url"])
        if m:
            exports.setdefault(m.group(1), {})[m.group(2)] = res["url"]
    return {d: u for d, u in exports.items() if {"data", "ref"} <= u.keys()}


def pick_snapshots(exports: dict, latest_only: bool) -> list[str]:
    dates = sorted(exports)
    latest = dates[-1]
    if latest_only:
        return [latest]
    picked = []
    for year in range(FIRST_YEAR, int(latest[:4]) + 1):
        candidates = [d for d in dates if d[:4] == str(year) and d[4:6] <= "10"]
        if candidates:
            picked.append(candidates[-1])
    # L'export le plus récent remplace l'instantané de son année.
    picked = [d for d in picked if d[:4] != latest[:4]] + [latest]
    return picked


def fetch(snapshot: str, urls: dict[str, str]) -> None:
    target = RAW_DIR / snapshot
    if target.exists() and all((target / t).exists() for t in TABLES):
        print(f"[ok]   {snapshot} déjà présent")
        return
    target.mkdir(parents=True, exist_ok=True)
    for kind in ("ref", "data"):
        print(f"[get]  {snapshot} {kind} …", flush=True)
        blob = requests.get(urls[kind], timeout=600).content
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            for name in zf.namelist():
                base = Path(name).name
                if base in TABLES:
                    (target / base).write_bytes(zf.read(name))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", action="store_true", help="dernier export seulement")
    args = parser.parse_args()
    exports = list_exports()
    for snap in pick_snapshots(exports, args.latest):
        fetch(snap, exports[snap])
    print("Terminé →", RAW_DIR)


if __name__ == "__main__":
    main()
