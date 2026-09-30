"""Step 4 - Charts for the report, notebook and README (saved to outputs/figures/)."""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D

from config import (FIGURES, GENDER_COLORS, GRID, INK, INK_2, MEN, NEUTRAL, PROCESSED, TABLES,
                    WOMEN, set_style)

set_style()
DIR_COLORS = {"Women pay more": WOMEN, "Men pay more": MEN, "No significant gap": NEUTRAL}
OUT_COLORS = {"Women's version dearer": WOMEN, "Within +/-2%": NEUTRAL, "Men's version dearer": MEN}


def rupees(x, _=None):
    return f"₹{x:,.0f}"


def save(fig, name):
    fig.savefig(FIGURES / f"{name}.png", facecolor="white")
    plt.close(fig)
    print("saved", name)


def gender_legend(ax, loc="lower right", **kw):
    ax.legend(handles=[Patch(color=WOMEN, label="Women"), Patch(color=MEN, label="Men")],
              loc=loc, **kw)


# --------------------------------------------------------------------------------- 01
def fig_pipeline():
    steps = [("Collect", "3 Kaggle datasets\nMyntra · BigBasket\nAmazon.in (₹)"),
             ("Clean", "De-duplicate, fix\nprices, drop outliers\n(log-IQR rule)"),
             ("Tag", "Gender from URL /\nkeywords (EN + HI)\ncategory + pack size"),
             ("Analyse", "Tests, bootstrap CI,\nmatched pairs,\nfixed-effects OLS"),
             ("Present", "Charts · Excel\nPower BI dashboard\nReport")]
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.set_xlim(0, len(steps) * 2.2)
    ax.set_ylim(0, 2.4)
    ax.axis("off")
    for i, (title, body) in enumerate(steps):
        x = i * 2.2 + 0.1
        ax.add_patch(FancyBboxPatch((x, 0.15), 1.8, 2.0, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#fbf3f6" if i % 2 == 0 else "#f1f6fd",
                                    ec=WOMEN if i % 2 == 0 else MEN, lw=1.4))
        ax.text(x + 0.9, 1.78, f"{i + 1}. {title}", ha="center", va="center", fontsize=11.5,
                fontweight="bold", color=INK)
        ax.text(x + 0.9, 0.9, body, ha="center", va="center", fontsize=9, color=INK_2,
                linespacing=1.5)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.18, 1.15), xytext=(x + 1.92, 1.15),
                        arrowprops=dict(arrowstyle="-|>", color=INK_2, lw=1.4))
    ax.set_title("Project workflow: from raw listings to evidence", pad=6)
    save(fig, "fig01_workflow")


# --------------------------------------------------------------------------------- 02
def fig_composition(df):
    ct = df.groupby(["source", "segment", "gender"]).size().unstack(fill_value=0)
    ct.index = [f"{s} · {g}" for s, g in ct.index]
    ct = ct.loc[ct.sum(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    y = np.arange(len(ct))
    ax.barh(y, ct["Men"], color=MEN, height=0.62, label="Men")
    ax.barh(y, ct["Women"], left=ct["Men"], color=WOMEN, height=0.62, label="Women",
            edgecolor="white", linewidth=1.5)
    for yi, (m, w) in enumerate(zip(ct["Men"], ct["Women"])):
        ax.text(m + w + ct.values.sum() * 0.004, yi, f"{m + w:,}  ({w / (m + w):.0%} women)",
                va="center", fontsize=8.5, color=INK_2)
    ax.set_yticks(y, ct.index)
    ax.set_xlabel("Number of products")
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:,.0f}")
    ax.set_xlim(0, ct.sum(axis=1).max() * 1.28)
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Analysis dataset: {len(df):,} gender-targeted products")
    gender_legend(ax)
    save(fig, "fig02_dataset_composition")


# --------------------------------------------------------------------------------- 03
def fig_distribution(df):
    d = df[df.age_group == "Adult"]
    order = ["Apparel", "Footwear", "Accessories", "Personal Care"]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    sns.boxplot(data=d, x="segment", y="mrp", hue="gender", order=order, hue_order=["Women", "Men"],
                palette=GENDER_COLORS, log_scale=True, showfliers=False, width=0.6, gap=0.15,
                linewidth=1, ax=ax, medianprops=dict(color="white", linewidth=2), saturation=1)
    med = d.groupby(["segment", "gender"]).mrp.median()
    q3 = d.groupby(["segment", "gender"]).mrp.quantile(0.75)
    for i, s in enumerate(order):
        for j, g in enumerate(["Women", "Men"]):
            ax.text(i + (-0.16 if j == 0 else 0.16), q3[s, g] * 1.12, f"median\n{rupees(med[s, g])}",
                    ha="center", va="bottom", fontsize=7.5, color=INK, fontweight="bold",
                    linespacing=1.1)
    ax.set_xlabel("")
    ax.set_ylabel("MRP (log scale)")
    ax.yaxis.set_major_formatter(rupees)
    ax.set_title("Price distribution by segment (adults, MRP, boxes = middle 50%)")
    ax.legend(title=None, loc="upper right")
    save(fig, "fig03_price_distribution")


# --------------------------------------------------------------------------------- 04
def fig_category_premium(cat):
    c = cat.copy()
    c["label"] = c.category + np.where(c.age_group == "Kids", " (kids)", "") + "  ·  " + c.source
    c = c.sort_values("premium_median_pct")
    fig, ax = plt.subplots(figsize=(9, 11))
    y = np.arange(len(c))
    colors = c.direction.map(DIR_COLORS)
    ax.hlines(y, c.ci_low_pct, c.ci_high_pct, color=colors, lw=2, alpha=0.45)
    ax.scatter(c.premium_median_pct, y, color=colors, s=46, zorder=3, edgecolor="white", lw=1.2)
    ax.axvline(0, color=INK_2, lw=1)
    ax.set_yticks(y, c.label, fontsize=8.5)
    ax.set_xlabel("Women's median MRP vs men's median MRP (%)   ·   line = bootstrap 95% CI")
    ax.set_xlim(-80, 100)
    ax.grid(axis="y", visible=False)
    for yi, (v, lo, hi, dname) in enumerate(zip(c.premium_median_pct, c.ci_low_pct, c.ci_high_pct,
                                               c.direction)):
        if dname != "No significant gap":
            ax.text(hi + 2 if v > 0 else lo - 2, yi, f"{v:+.0f}%", va="center",
                    ha="left" if v > 0 else "right", fontsize=8, color=INK, fontweight="bold")
    ax.text(3, len(c) - 0.2, "women pay more →", color=WOMEN, fontsize=9, fontweight="bold")
    ax.text(-3, len(c) - 0.2, "← men pay more", color=MEN, fontsize=9, fontweight="bold", ha="right")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=v, label=k, markersize=8)
                       for k, v in DIR_COLORS.items()],
              loc="lower right", title="After Benjamini-Hochberg correction", title_fontsize=8.5)
    ax.set_title("Gender price gap in 44 product categories")
    save(fig, "fig04_category_premium")


# --------------------------------------------------------------------------------- 05
def fig_unit_price(df):
    d = df[(df.size_unit == "ml") & df.unit_price_100.notna() & (df.source == "Amazon.in")]
    order = (d.groupby("category").unit_price_100.median().sort_values(ascending=False).index)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    sns.pointplot(data=d, x="unit_price_100", y="category", hue="gender", order=order,
                  hue_order=["Women", "Men"], palette=GENDER_COLORS, estimator=np.median,
                  errorbar=("ci", 95), n_boot=1000, seed=1, dodge=0.35, linestyle="none",
                  markers="o", markersize=7, err_kws={"linewidth": 2}, ax=ax, log_scale=True)
    ax.xaxis.set_major_formatter(rupees)
    ax.set_xlabel("Median price per 100 ml (log scale, 95% CI)")
    ax.set_ylabel("")
    ax.set_title("Like-for-like: price per 100 ml of personal-care liquids (Amazon.in)")
    ax.legend(title=None, loc="lower right")
    save(fig, "fig05_unit_price")


# --------------------------------------------------------------------------------- 06
def fig_pairs_scatter(pairs):
    fig, ax = plt.subplots(figsize=(7, 6.3))
    for outcome, col in OUT_COLORS.items():
        p = pairs[pairs.outcome == outcome]
        ax.scatter(p.median_men, p.median_women, s=22, color=col, alpha=0.75, edgecolor="white",
                   lw=0.6, label=f"{outcome} ({len(p)})")
    lim = [pairs[["median_men", "median_women"]].min().min() * 0.8,
           pairs[["median_men", "median_women"]].max().max() * 1.2]
    ax.plot(lim, lim, color=INK_2, lw=1, ls="--")
    ax.text(lim[1] * 0.25, lim[1] * 0.19, "equal price", rotation=45, color=INK_2, fontsize=8.5,
            ha="center", va="center")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.xaxis.set_major_formatter(rupees)
    ax.yaxis.set_major_formatter(rupees)
    ax.set_xlabel("Men's line: median MRP")
    ax.set_ylabel("Women's line: median MRP")
    ax.set_title(f"{len(pairs)} brand-matched pairs (same brand, same category)")
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "fig06_brand_pairs_scatter")


# --------------------------------------------------------------------------------- 07
def fig_pairs_outcome(pairs):
    t = pd.crosstab(pairs.segment, pairs.outcome, normalize="index") * 100
    n = pairs.segment.value_counts()
    t = t[list(OUT_COLORS)].loc[["Personal Care", "Accessories", "Footwear", "Apparel"]]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    left = np.zeros(len(t))
    for col in t.columns:
        ax.barh(t.index, t[col], left=left, color=OUT_COLORS[col], height=0.6, label=col,
                edgecolor="white", linewidth=2)
        for i, v in enumerate(t[col]):
            if v > 7:
                ax.text(left[i] + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color="white" if col != "Within +/-2%" else INK, fontweight="bold")
        left += t[col].values
    ax.set_yticks(range(len(t)), [f"{s}  (n={n[s]})" for s in t.index])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of brand-matched pairs (%)")
    ax.grid(visible=False)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.25), fontsize=9)
    ax.set_title("Within the same brand, whose version costs more?")
    save(fig, "fig07_pairs_outcome")


# --------------------------------------------------------------------------------- 08
def fig_forest(reg):
    r = reg.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    col = np.where(r.ci_low_pct > 0, WOMEN, np.where(r.ci_high_pct < 0, MEN, NEUTRAL))
    ax.hlines(r.index, r.ci_low_pct, r.ci_high_pct, color=col, lw=2.2)
    ax.scatter(r.premium_pct, r.index, color=col, s=55, zorder=3, edgecolor="white", lw=1.2)
    ax.axvline(0, color=INK_2, lw=1)
    for i, row in r.iterrows():
        ptxt = "p<0.001" if row.p_value < 0.001 else f"p={row.p_value:.3f}"
        ax.text(12, i, f"{row.premium_pct:+.1f}%   ({ptxt}, n={row.n_products:,})",
                va="center", fontsize=8, color=INK_2)
    ax.set_yticks(r.index, r.model, fontsize=9)
    ax.set_xlim(-22, 32)
    ax.set_xlabel("Estimated women's price premium (%), 95% CI, SE clustered by brand")
    ax.grid(axis="y", visible=False)
    ax.set_title("Fixed-effects regression: log(price) ~ Female + group effects")
    save(fig, "fig08_regression_forest")


# --------------------------------------------------------------------------------- 09
def fig_discount(df):
    order = ["Apparel", "Footwear", "Accessories", "Personal Care"]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    sns.barplot(data=df, x="segment", y="discount_pct", hue="gender", order=order,
                hue_order=["Women", "Men"], palette=GENDER_COLORS, errorbar=("ci", 95),
                n_boot=500, seed=1, width=0.6, gap=0.1, ax=ax, err_kws={"linewidth": 1.2},
                saturation=1)
    for cont in ax.containers:
        ax.bar_label(cont, fmt="%.1f%%", fontsize=8.5, padding=3, color=INK)
    ax.set_xlabel("")
    ax.set_ylabel("Average discount off MRP (%)")
    ax.set_title("Women's items carry deeper discounts in apparel and accessories")
    ax.legend(title=None)
    save(fig, "fig09_discount")


# --------------------------------------------------------------------------------- 10
def fig_mrp_vs_selling(cat, cat_sp):
    m = cat.merge(cat_sp, on=["source", "age_group", "segment", "category"], suffixes=("_mrp", "_sp"))
    m = m[m.significant_mrp | m.significant_sp].copy()
    m["label"] = m.category + np.where(m.age_group == "Kids", " (kids)", "")
    m = m.sort_values("premium_median_pct_mrp")
    fig, ax = plt.subplots(figsize=(9, 7.5))
    y = np.arange(len(m))
    ax.hlines(y, m.premium_median_pct_mrp, m.premium_median_pct_sp, color=GRID, lw=3)
    ax.scatter(m.premium_median_pct_mrp, y, color=INK_2, s=40, label="On MRP (list price)", zorder=3)
    ax.scatter(m.premium_median_pct_sp, y, color=WOMEN, s=40, label="On selling price (after discount)",
               zorder=3, marker="D")
    ax.axvline(0, color=INK_2, lw=1)
    ax.set_yticks(y, m.label, fontsize=8.5)
    ax.set_xlabel("Women's median price vs men's (%)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right")
    ax.set_title("Discounts shift the gap: list price vs price actually paid")
    save(fig, "fig10_mrp_vs_selling")


# --------------------------------------------------------------------------------- 11
def fig_composition_effect(age, reg):
    raw = age.set_index("age_group").premium_median_pct
    get = lambda name: reg.set_index("model").loc[name, "premium_pct"]
    data = pd.DataFrame({
        "Raw median gap": [raw["Adult"], raw["Kids"]],
        "Same category": [get("Adults: within category"), get("Kids: within category")],
        "Same brand + category": [get("Adults: within brand x category"),
                                   get("Kids: within brand x category")],
    }, index=["Adults", "Kids"])
    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = np.arange(3)
    for i, (grp, row) in enumerate(data.iterrows()):
        bars = ax.bar(x + (i - 0.5) * 0.36, row.values, width=0.34,
                      color=[INK_2, "#8a8983"][i], label=grp, edgecolor="white", lw=1.5)
        ax.bar_label(bars, labels=[f"{v:+.1f}%" for v in row.values], padding=3, fontsize=9)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xticks(x, data.columns)
    ax.set_ylabel("Women's premium (%)")
    ax.set_ylim(-18, 24)
    ax.grid(axis="x", visible=False)
    ax.legend()
    ax.set_title("Comparing like with like changes the answer")
    save(fig, "fig11_composition_effect")


# --------------------------------------------------------------------------------- 12
def fig_corr(df):
    d = df[["mrp", "selling_price", "discount_pct", "rating", "rating_count", "female"]].rename(
        columns={"mrp": "MRP", "selling_price": "Selling price", "discount_pct": "Discount %",
                 "rating": "Rating", "rating_count": "No. of ratings", "female": "Women's product"})
    corr = d.corr(method="spearman")
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    cmap = sns.diverging_palette(250, 345, s=75, l=55, as_cmap=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap, vmin=-1, vmax=1, center=0, square=True,
                linewidths=2, linecolor="white", cbar_kws={"shrink": 0.7}, ax=ax,
                annot_kws={"fontsize": 9})
    ax.set_title("Spearman correlation matrix")
    save(fig, "fig12_correlation_heatmap")


# --------------------------------------------------------------------------------- 13
def fig_ratio_hist(pairs):
    fig, ax = plt.subplots(figsize=(9, 3.6))
    pct = (pairs.ratio - 1) * 100
    bins = np.arange(-82.5, 107.6, 5)
    n, edges, patches = ax.hist(pct.clip(-80, 100), bins=bins, edgecolor="white", lw=1)
    for p, left in zip(patches, edges[:-1]):
        p.set_facecolor(WOMEN if left >= 2.5 else MEN if left < -2.5 else NEUTRAL)
    ax.axvline(pct.median(), color=INK, lw=1.4, ls="--")
    ax.text(pct.median() + 2, n.max() * 0.92, f"median {pct.median():+.1f}%", fontsize=9)
    ax.set_xlabel("Women's line vs men's line, same brand & category (%)   ·   gaps above +100% grouped at +100")
    ax.set_ylabel("Number of pairs")
    ax.grid(axis="x", visible=False)
    ax.set_title("Distribution of brand-matched price differences")
    save(fig, "fig13_pairs_histogram")


# --------------------------------------------------------------------------------- 14
def fig_top_categories(df):
    top = df[(df.source == "Myntra") & (df.age_group == "Adult")]
    order = top.category.value_counts().head(10).index
    med = (top[top.category.isin(order)].groupby(["category", "gender"]).mrp.median().unstack()
             .loc[order[::-1]])
    fig, ax = plt.subplots(figsize=(9, 4.6))
    y = np.arange(len(med))
    ax.barh(y + 0.19, med["Women"], height=0.36, color=WOMEN, label="Women")
    ax.barh(y - 0.19, med["Men"], height=0.36, color=MEN, label="Men")
    for yi, (w, m) in enumerate(zip(med["Women"], med["Men"])):
        ax.text(w + 40, yi + 0.19, rupees(w), va="center", fontsize=8)
        ax.text(m + 40, yi - 0.19, rupees(m), va="center", fontsize=8)
    ax.set_yticks(y, med.index)
    ax.xaxis.set_major_formatter(rupees)
    ax.set_xlabel("Median MRP")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right")
    ax.set_title("Median MRP in the 10 largest Myntra categories")
    save(fig, "fig14_top_categories")


def main():
    df = pd.read_csv(PROCESSED / "pinktax_master.csv", low_memory=False)
    df["female"] = (df.gender == "Women").astype(int)
    cat = pd.read_csv(TABLES / "category_premium_mrp.csv")
    cat_sp = pd.read_csv(TABLES / "category_premium_selling_price.csv")
    pairs = pd.read_csv(TABLES / "brand_matched_pairs.csv")
    reg = pd.read_csv(TABLES / "regression_fixed_effects.csv")
    age = pd.read_csv(TABLES / "age_group_premium_mrp.csv")

    fig_pipeline()
    fig_composition(df)
    fig_distribution(df)
    fig_category_premium(cat)
    fig_unit_price(df)
    fig_pairs_scatter(pairs)
    fig_pairs_outcome(pairs)
    fig_forest(reg)
    fig_discount(df)
    fig_mrp_vs_selling(cat, cat_sp)
    fig_composition_effect(age, reg)
    fig_corr(df)
    fig_ratio_hist(pairs)
    fig_top_categories(df)


if __name__ == "__main__":
    main()
