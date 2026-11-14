#!/usr/bin/env python3
"""Download and extract authentic Maharashtra GeoJSON boundary from geoBoundaries gbOpen IND ADM1.
"""
import json
import sys
from pathlib import Path
import requests

def main():
    url = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/IND/ADM1/geoBoundaries-IND-ADM1.geojson"
    print("Downloading India ADM1 from geoBoundaries...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    target_feature = None
    for f in data.get("features", []):
        name = f.get("properties", {}).get("shapeName", "")
        iso = f.get("properties", {}).get("shapeISO", "")
        # Match 'maharashtra' or 'IN-MH'
        import unicodedata
        norm_name = "".join(c for c in unicodedata.normalize("NFD", name) if unicodedata.category(c) != "Mn").lower()
        if "maharashtra" in norm_name or iso == "IN-MH":
            target_feature = f
            break

    if not target_feature:
        print("ERROR: Maharashtra feature not found in geoBoundaries dataset!", file=sys.stderr)
        sys.exit(1)

    out_path = Path("data/boundaries/maharashtra.geojson")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fc = {
        "type": "FeatureCollection",
        "metadata": {
            "region_name": "Maharashtra",
            "country": "India",
            "source": "geoBoundaries gbOpen (ADM1) / DataMeet / Election Commission of India",
            "source_url": url,
            "license": "Creative Commons Attribution 2.5 India (CC BY 2.5 IN)",
            "shapeName": target_feature["properties"].get("shapeName"),
            "shapeISO": target_feature["properties"].get("shapeISO"),
            "shapeID": target_feature["properties"].get("shapeID"),
        },
        "features": [target_feature]
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fc, f, indent=2)

    print(f"Successfully extracted Maharashtra GeoJSON to {out_path} ({out_path.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
