import argparse
import json
import math
import os
import random
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def find_columns(df):
    lat_candidates = [
        "latitude",
        "Latitude",
        "lat",
        "LATITUDE",
    ]
    lon_candidates = [
        "longitude",
        "Longitude",
        "lon",
        "LONGITUDE",
    ]
    nkill_candidates = ["nkill", "NKILL"]
    lat = next((c for c in lat_candidates if c in df.columns), None)
    lon = next((c for c in lon_candidates if c in df.columns), None)
    nkill = next((c for c in nkill_candidates if c in df.columns), None)
    return lat, lon, nkill


def load_data(path):
    df = pd.read_csv(path, encoding="ISO-8859-1", low_memory=False)
    lat, lon, nkill = find_columns(df)
    if lat is None or lon is None:
        raise ValueError("Colunas de latitude/longitude não encontradas.")
    extra_cols = []
    if "iyear" in df.columns:
        extra_cols.append("iyear")
    region_col = None
    if "region_txt" in df.columns:
        region_col = "region_txt"
        extra_cols.append("region_txt")
    elif "region" in df.columns:
        region_col = "region"
        extra_cols.append("region")
    cols = [lat, lon] + ([nkill] if nkill else []) + extra_cols
    df = df[cols].copy()
    for c in [lat, lon] + ([nkill] if nkill else []):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "iyear" in df.columns:
        df["iyear"] = pd.to_numeric(df["iyear"], errors="coerce")
    df = df.dropna(subset=[lat, lon])
    df = df[(df[lat].between(-90, 90)) & (df[lon].between(-180, 180))]
    return df, lat, lon, nkill, region_col


def to_radians(a):
    return np.radians(a)


def run_dbscan_radians(coords_rad, eps_rad, min_samples):
    model = DBSCAN(eps=eps_rad, min_samples=min_samples, metric="haversine", n_jobs=-1)
    labels = model.fit_predict(coords_rad)
    return labels


def try_hdbscan(coords_rad, min_samples):
    try:
        import hdbscan  # type: ignore

        model = hdbscan.HDBSCAN(min_cluster_size=min_samples, metric="haversine")
        labels = model.fit_predict(coords_rad)
        return labels
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="globalterrorismdb_0718dist.csv")
    parser.add_argument("--output", default="clusters_data.json")
    parser.add_argument("--eps", type=float, default=0.005)
    parser.add_argument("--min-samples", type=int, default=10)
    parser.add_argument("--max-points", type=int, default=80000)
    args = parser.parse_args()

    df, lat, lon, nkill, region_col = load_data(args.input)
    n = len(df)
    if n > args.max_points:
        idx = np.random.RandomState(42).choice(n, size=args.max_points, replace=False)
        df = df.iloc[idx]

    coords_rad = np.column_stack((to_radians(df[lat].values), to_radians(df[lon].values)))
    labels = try_hdbscan(coords_rad, args.min_samples)
    if labels is None:
        labels = run_dbscan_radians(coords_rad, args.eps, args.min_samples)

    nk = df[nkill].values if nkill else np.full(len(df), np.nan)
    out = []
    for i in range(len(df)):
        item = {
            "lat": float(df.iloc[i][lat]),
            "lon": float(df.iloc[i][lon]),
            "cluster_id": int(labels[i]),
        }
        if not np.isnan(nk[i]):
            item["nkill"] = int(nk[i])
        if "iyear" in df.columns and not pd.isna(df.iloc[i]["iyear"]):
            item["iyear"] = int(df.iloc[i]["iyear"]) 
        if region_col is not None:
            val = df.iloc[i][region_col]
            if pd.notna(val):
                item["region_txt"] = str(val)
        out.append(item)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    counts = {}
    for l in labels:
        k = str(int(l))
        counts[k] = counts.get(k, 0) + 1
    summary = {
        "points": len(out),
        "clusters": len({l for l in labels if l >= 0}),
        "noise": counts.get("-1", 0),
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
