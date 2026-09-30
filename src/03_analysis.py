"""Step 3 - Statistical analysis of gender-based price differences.

Four complementary lenses, each answering a sharper version of the question
"do women pay more for comparable products?":

  A. Category comparison   - women's vs men's prices inside the same product category
                             (Mann-Whitney U, Welch t-test on log price, Cohen's d,
                             bootstrap 95% CI of the median premium, Benjamini-Hochberg FDR)
  B. Unit-price comparison - Rs per 100 ml for liquids (deodorant, perfume, body wash ...)
  C. Brand-matched pairs   - same brand + same category, men's vs women's line
                             (Wilcoxon signed-rank, sign test)
  D. Fixed-effects model   - log(MRP) = b*Female + brand x category effects,
                             standard errors clustered by brand

All tables are written to outputs/tables/.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

from config import PROCESSED, TABLES

RNG = np.random.default_rng(42)
N_BOOT = 2000
CELL = ["source", "age_group", "segment", "category"]


def load():
    df = pd.read_csv(PROCESSED / "pinktax_master.csv", low_memory=False)
    df["female"] = (df["gender"] == "Women").astype(int)
    df["log_mrp"] = np.log(df["mrp"])
    return df


def pct(ratio):
    return (ratio - 1) * 100


def boot_median_ratio(w, m, n=N_BOOT):
    """Bootstrap CI for median(women) / median(men)."""
    w, m = np.asarray(w), np.asarray(m)
    wi = RNG.integers(0, len(w), (n, len(w)))
    mi = RNG.integers(0, len(m), (n, len(m)))
    ratios = np.median(w[wi], axis=1) / np.median(m[mi], axis=1)
    return np.percentile(ratios, [2.5, 97.5])


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return (np.mean(a) - np.mean(b)) / sp


def compare_groups(df, value, by):
    rows = []
    for key, g in df.groupby(by):
        w = g.loc[g.gender == "Women", value].dropna().values
        m = g.loc[g.gender == "Men", value].dropna().values
        if len(w) < 10 or len(m) < 10:
            continue
        lo, hi = boot_median_ratio(w, m)
        mw = stats.mannwhitneyu(w, m, alternative="two-sided")
        wt = stats.ttest_ind(np.log(w), np.log(m), equal_var=False)
        rows.append({
            **dict(zip(by, key if isinstance(key, tuple) else (key,))),
            "n_men": len(m), "n_women": len(w),
            "median_men": np.median(m), "median_women": np.median(w),
            "mean_men": m.mean(), "mean_women": w.mean(),
            "premium_median_pct": pct(np.median(w) / np.median(m)),
            "premium_mean_pct": pct(w.mean() / m.mean()),
            "ci_low_pct": pct(lo), "ci_high_pct": pct(hi),
            "mannwhitney_U": mw.statistic, "p_mannwhitney": mw.pvalue,
            "welch_t_log": wt.statistic, "p_welch_log": wt.pvalue,
            "cohens_d_log": cohens_d(np.log(w), np.log(m)),
        })
    out = pd.DataFrame(rows)
    out["p_adj_bh"] = multipletests(out["p_mannwhitney"], method="fdr_bh")[1]
    out["significant"] = out["p_adj_bh"] < 0.05
    out["direction"] = np.select(
        [out.significant & (out.premium_median_pct > 0), out.significant & (out.premium_median_pct < 0)],
        ["Women pay more", "Men pay more"], default="No significant gap")
    return out.sort_values("premium_median_pct", ascending=False)


def brand_matched(df, value="mrp", min_each=2):
    cells = CELL + ["brand"]
    med = (df.dropna(subset=[value, "brand"])
             .groupby(cells + ["gender"])[value].agg(["median", "size"]).unstack("gender"))
    med.columns = [f"{a}_{b}" for a, b in med.columns]
    med = med.dropna()
    med = med[(med["size_Men"] >= min_each) & (med["size_Women"] >= min_each)].reset_index()
    med = med.rename(columns={"median_Men": "median_men", "median_Women": "median_women",
                              "size_Men": "n_men", "size_Women": "n_women"})
    med["ratio"] = med["median_women"] / med["median_men"]
    med["log_ratio"] = np.log(med["ratio"])
    med["outcome"] = np.select([med.ratio > 1.02, med.ratio < 0.98],
                               ["Women's version dearer", "Men's version dearer"], "Within +/-2%")
    return med


def summarise_pairs(pairs, label):
    lr = pairs["log_ratio"].values
    wil = stats.wilcoxon(lr) if len(lr) > 10 else None
    n_w = (pairs.outcome == "Women's version dearer").sum()
    n_m = (pairs.outcome == "Men's version dearer").sum()
    sign = stats.binomtest(n_w, n_w + n_m, 0.5) if n_w + n_m else None
    boot = [np.exp(np.mean(RNG.choice(lr, len(lr)))) for _ in range(N_BOOT)]
    return {
        "scope": label, "pairs": len(pairs),
        "women_dearer_pct": n_w / len(pairs) * 100,
        "men_dearer_pct": n_m / len(pairs) * 100,
        "within_2pct_pct": (pairs.outcome == "Within +/-2%").mean() * 100,
        "geo_mean_premium_pct": pct(np.exp(lr.mean())),
        "ci_low_pct": pct(np.percentile(boot, 2.5)), "ci_high_pct": pct(np.percentile(boot, 97.5)),
        "median_premium_pct": pct(np.exp(np.median(lr))),
        "p_wilcoxon": wil.pvalue if wil else np.nan,
        "p_sign_test": sign.pvalue if sign else np.nan,
    }


def fixed_effects(df, group_cols, label, y="log_mrp"):
    """Within estimator: demean y and Female inside each group, OLS, cluster SE by brand."""
    d = df.dropna(subset=[y, "brand"]).copy()
    d["_g"] = d[group_cols].astype(str).agg("|".join, axis=1)
    both = d.groupby("_g")["female"].transform("nunique") == 2
    d = d[both]
    yd = d[y] - d.groupby("_g")[y].transform("mean")
    xd = d["female"] - d.groupby("_g")["female"].transform("mean")
    clusters = pd.factorize(d["brand"])[0]
    fit = sm.OLS(yd.values, xd.values.reshape(-1, 1)).fit(
        cov_type="cluster", cov_kwds={"groups": clusters})
    b, se = fit.params[0], fit.bse[0]
    return {"model": label, "n_products": len(d), "n_groups": d["_g"].nunique(),
            "n_brands": d["brand"].nunique(), "coef_female": b, "se_cluster": se,
            "premium_pct": pct(np.exp(b)), "ci_low_pct": pct(np.exp(b - 1.96 * se)),
            "ci_high_pct": pct(np.exp(b + 1.96 * se)), "p_value": fit.pvalues[0]}


def main():
    df = load()
    kpi = {}

    # --- dataset overview -------------------------------------------------------------
    overview = df.pivot_table(index=["source", "segment"], columns="gender", values="mrp",
                              aggfunc="size", fill_value=0).reset_index()
    overview.to_csv(TABLES / "dataset_overview.csv", index=False)
    kpi["products"] = int(len(df))
    kpi["categories"] = int(df.groupby(CELL).ngroups)
    kpi["brands"] = int(df["brand"].nunique())
    kpi["sources"] = sorted(df["source"].unique().tolist())

    desc = df.groupby(["segment", "gender"])["mrp"].describe(percentiles=[.25, .5, .75]).round(1)
    desc.to_csv(TABLES / "descriptive_stats_by_segment.csv")

    # --- A. category comparison ----------------------------------------------------------
    cat = compare_groups(df, "mrp", CELL)
    cat.to_csv(TABLES / "category_premium_mrp.csv", index=False)
    cat_sp = compare_groups(df, "selling_price", CELL)
    cat_sp.to_csv(TABLES / "category_premium_selling_price.csv", index=False)
    seg = compare_groups(df[df.age_group == "Adult"], "mrp", ["segment"])
    seg.to_csv(TABLES / "segment_premium_mrp.csv", index=False)
    age = compare_groups(df, "mrp", ["age_group"])
    age.to_csv(TABLES / "age_group_premium_mrp.csv", index=False)

    kpi["cells_tested"] = int(len(cat))
    kpi["cells_women_more"] = int((cat.direction == "Women pay more").sum())
    kpi["cells_men_more"] = int((cat.direction == "Men pay more").sum())
    kpi["cells_no_gap"] = int((cat.direction == "No significant gap").sum())
    kpi["median_cell_premium_pct"] = float(cat.premium_median_pct.median())

    # --- B. unit price (Rs / 100 ml) --------------------------------------------------------
    unit = compare_groups(df[df.size_unit == "ml"], "unit_price_100", ["source", "category"])
    unit.to_csv(TABLES / "unit_price_premium.csv", index=False)

    # --- C. brand-matched pairs -------------------------------------------------------------
    pairs = brand_matched(df)
    pairs.to_csv(TABLES / "brand_matched_pairs.csv", index=False)
    pair_summary = [summarise_pairs(pairs, "All matched pairs")]
    for (seg_name), p in pairs.groupby("segment"):
        pair_summary.append(summarise_pairs(p, f"Segment: {seg_name}"))
    for (a), p in pairs.groupby("age_group"):
        pair_summary.append(summarise_pairs(p, f"Age group: {a}"))
    pair_summary = pd.DataFrame(pair_summary)
    pair_summary.to_csv(TABLES / "brand_matched_summary.csv", index=False)
    by_cat = (pairs.groupby(["age_group", "segment", "category"])
                   .apply(lambda p: pd.Series(summarise_pairs(p, "")), include_groups=False)
                   .drop(columns="scope").reset_index())
    by_cat = by_cat[by_cat.pairs >= 8].sort_values("geo_mean_premium_pct", ascending=False)
    by_cat.to_csv(TABLES / "brand_matched_by_category.csv", index=False)
    kpi["matched_pairs"] = int(len(pairs))
    kpi["pairs_women_dearer_pct"] = float(pair_summary.iloc[0].women_dearer_pct)
    kpi["pairs_men_dearer_pct"] = float(pair_summary.iloc[0].men_dearer_pct)
    kpi["pairs_geo_premium_pct"] = float(pair_summary.iloc[0].geo_mean_premium_pct)

    # --- D. fixed-effects regression --------------------------------------------------------
    adults = df[df.age_group == "Adult"]
    models = [
        fixed_effects(adults, ["source", "category"], "Adults: within category"),
        fixed_effects(adults, ["source", "category", "brand"], "Adults: within brand x category"),
    ]
    for s in ["Apparel", "Footwear", "Accessories", "Personal Care"]:
        models.append(fixed_effects(adults[adults.segment == s], ["source", "category", "brand"],
                                    f"{s}: within brand x category"))
    kids = df[df.age_group == "Kids"]
    models.append(fixed_effects(kids, ["source", "category"], "Kids: within category"))
    models.append(fixed_effects(kids, ["source", "category", "brand"], "Kids: within brand x category"))
    liquids = df[df.unit_price_100.notna()].assign(log_unit=lambda d: np.log(d.unit_price_100))
    models.append(fixed_effects(liquids, ["source", "category", "brand"],
                                "Personal care Rs/100ml: within brand x category", y="log_unit"))
    reg = pd.DataFrame(models)
    reg.to_csv(TABLES / "regression_fixed_effects.csv", index=False)
    kpi["fe_within_category_pct"] = float(reg.iloc[0].premium_pct)
    kpi["fe_within_brand_pct"] = float(reg.iloc[1].premium_pct)

    # --- E. discounts ------------------------------------------------------------------------
    disc = (df.groupby(["segment", "gender"])["discount_pct"].agg(["mean", "median", "count"])
              .round(2).reset_index())
    disc.to_csv(TABLES / "discount_by_gender.csv", index=False)
    mw = stats.mannwhitneyu(df.loc[df.gender == "Women", "discount_pct"],
                            df.loc[df.gender == "Men", "discount_pct"])
    kpi["discount_mean_women"] = float(df.loc[df.gender == "Women", "discount_pct"].mean())
    kpi["discount_mean_men"] = float(df.loc[df.gender == "Men", "discount_pct"].mean())
    kpi["discount_p"] = float(mw.pvalue)

    # --- F. chi-square: is "women's version dearer" independent of segment? ----------------
    ct = pd.crosstab(pairs.segment, pairs.outcome)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    ct.to_csv(TABLES / "pairs_outcome_by_segment.csv")
    kpi["chi2_segment_outcome"] = {"chi2": float(chi2), "dof": int(dof), "p": float(p)}

    # --- correlations -----------------------------------------------------------------------
    corr = df[["mrp", "selling_price", "discount_pct", "rating", "rating_count", "female"]].corr(
        method="spearman").round(3)
    corr.to_csv(TABLES / "spearman_correlations.csv")

    with open(TABLES / "kpis.json", "w") as f:
        json.dump(kpi, f, indent=2)

    pd.set_option("display.width", 220)
    print(json.dumps(kpi, indent=2))
    print(cat[["source", "age_group", "category", "n_men", "n_women", "median_men", "median_women",
               "premium_median_pct", "ci_low_pct", "ci_high_pct", "p_adj_bh", "direction"]]
          .round(2).to_string(index=False))
    print(unit.round(2).to_string(index=False))
    print(pair_summary.round(3).to_string(index=False))
    print(by_cat.round(2).to_string(index=False))
    print(reg.round(4).to_string(index=False))
    print(disc.to_string(index=False))
    print(seg.round(3).to_string(index=False))
    print(age.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
