import pandas as pd
import numpy as np

coords = pd.read_csv("coords.csv")
coords = coords.rename(columns={'City': 'Municipality'})

def recommend_vendors(df, user_prefs, top_n=5, weights=None, strict_service=True):
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
        return 2 * R * np.arcsin(np.sqrt(a))
    
    df = df.copy()
    # default weights
    if weights is None:
        weights = {'price':0.5, 'rating':0.20, 'package':0.15, 'municipality':0.15, 'category':0.10, 'distance':0.15}

    user_muni = user_prefs.get('Municipality')
    user_coords = coords[coords['Municipality'].str.lower() == user_muni.lower()]
    user_lat = user_coords['Latitude'].values[0]
    user_lon = user_coords['Longitude'].values[0]

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['Distance_km'] = df.apply(
            lambda row: haversine(user_lat, user_lon, row['Latitude'], row['Longitude']),
            axis=1
        )

    # 1) Optional hard-filter by Service (recommended)
    requested_service = user_prefs.get('Category', None)
    if requested_service and strict_service:
        mask = df['Category'].str.lower() == requested_service.lower()
        filtered = df[mask].copy()
        if filtered.empty:
            filtered = df.copy()
        df = filtered

    # If df became empty for other reasons, return empty
    if df.empty:
        return pd.DataFrame(columns=list(df.columns) + ['Score', 'Explanation'])

    # 2) Price similarity (normalized distance -> 0..1)
    budget = user_prefs.get('Budget', df['Estimated Price'].median())
    min_p, max_p = df['Estimated Price'].min(), df['Estimated Price'].max()
    denom = max_p - min_p if (max_p - min_p) > 0 else max_p + 1e-9
    price_sim = 1 - (np.abs(df['Estimated Price'] - budget) / denom)
    price_sim = price_sim.clip(0, 1)

    # 3) Rating normalized 0..1
    min_r, max_r = df['Rating'].min(), df['Rating'].max()
    rating_sim = (df['Rating'] - min_r) / (max_r - min_r + 1e-9)

    # 4) Package match (binary)
    pkg = user_prefs.get('Package', None)
    if pkg:
        pkg_match = (df['Package'].str.lower() == pkg.lower()).astype(float)
    else:
        pkg_match = np.ones(len(df))

    # Distance similarity (closer = higher score)
    if 'Distance_km' in df.columns:
        max_dist = df['Distance_km'].max()
        min_dist = df['Distance_km'].min()
        denom = max_dist - min_dist if (max_dist - min_dist) > 0 else max_dist + 1e-9
        dist_sim = 1 - ((df['Distance_km'] - min_dist) / denom)
    else:
        dist_sim = np.ones(len(df))

    # 5) Municipality match (binary)
    muni = user_prefs.get('Municipality', None)
    if muni:
        muni_match = (df['Municipality'].str.lower() == muni.lower()).astype(float)
    else:
        muni_match = np.ones(len(df))

    # 6) Service match (if not strict filtering)
    if not strict_service and requested_service:
        service_match = (df['Category'].str.lower() == requested_service.lower()).astype(float)
    else:
        service_match = np.ones(len(df))  # all 1 if strict_service applied

    # 7) Combine with weights
    score = (
        weights.get('price',0) * price_sim +
        weights.get('rating',0) * rating_sim +
        weights.get('package',0) * pkg_match +
        weights.get('municipality',0) * muni_match +
        weights.get('category',0) * service_match +
        weights.get('distance',0) * dist_sim
    )
    df['Score'] = score

    # 8) Build an explanation column
    explanations = []
    for idx, row in df.iterrows():
        parts = []
        parts.append(f"price_diff={int(abs(row['Estimated Price']-budget))}")
        parts.append(f"rating={row['Rating']:.1f}")
        if pkg:
            parts.append(f"package_match={'yes' if row['Package'].lower()==pkg.lower() else 'no'}")
        if muni:
            parts.append(f"municipality_match={'yes' if row['Municipality'].lower()==muni.lower() else 'no'}")
        if 'Distance_km' in row:
            parts.append(f"distance={row['Distance_km']:.1f}km")
        explanations.append('; '.join(parts))
    df['Explanation'] = explanations

    # 9) Return top-n sorted by Score, then Rating
    out = df.sort_values(['Score','Rating'], ascending=[False, False]).head(top_n)
    return out.reset_index(drop=True)

# Example usage:
vendors_df = pd.read_csv("vendors.csv", header=1)
prefs = {"Category":"Lights","Municipality":"Lucban","Budget":50000,"Package":"Standard"}
recs = recommend_vendors(vendors_df, prefs, top_n=5, weights=None, strict_service=True)

print(recs[['Vendor Name','Category','Municipality','Estimated Price','Rating','Score', 'Explanation']])