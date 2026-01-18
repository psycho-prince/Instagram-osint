def username_variants(u):
    base = u.replace(".", "").replace("_", "")
    return list(set([
        u,
        u.replace(".", ""),
        u.replace("_", ""),
        f"_{u}",
        f"{u}_",
        base,
        f"_{base}_",
    ]))
