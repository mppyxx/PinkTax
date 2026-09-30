"""Step 7 - Export Power BI-ready tables, a report theme and a dashboard layout mock-up.

Outputs in powerbi/:
  data/fact_products.csv        one row per product (the fact table)
  data/dim_category.csv         category dimension with segment
  data/category_premium.csv     statistical results per category
  data/brand_pairs.csv          brand-matched comparisons
  data/regression.csv           fixed-effects model results
  PinkTax_theme.json            Power BI theme (View > Themes > Browse for themes)
  dashboard_layout.png          layout mock-up to follow while building the report
The DAX measures and the build steps live in powerbi/DAX_measures.dax and
powerbi/PowerBI_Build_Guide.md.
"""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from config import INK, INK_2, MEN, NEUTRAL, POWERBI, PROCESSED, TABLES, WOMEN, set_style

set_style()
DATA = POWERBI / "data"
DATA.mkdir(exist_ok=True)


def export_tables():
    df = pd.read_csv(PROCESSED / "pinktax_master.csv", low_memory=False)
    df.insert(0, "product_key", range(1, len(df) + 1))
    df["category_key"] = df.source + " | " + df.age_group + " | " + df.category
    df.drop(columns=["product_name"]).to_csv(DATA / "fact_products.csv", index=False)
    dim = (df[["category_key", "source", "age_group", "segment", "category"]]
           .drop_duplicates().sort_values("category_key"))
    dim.to_csv(DATA / "dim_category.csv", index=False)
    cat = pd.read_csv(TABLES / "category_premium_mrp.csv")
    cat.insert(0, "category_key", cat.source + " | " + cat.age_group + " | " + cat.category)
    cat.round(4).to_csv(DATA / "category_premium.csv", index=False)
    pairs = pd.read_csv(TABLES / "brand_matched_pairs.csv")
    pairs.insert(0, "category_key", pairs.source + " | " + pairs.age_group + " | " + pairs.category)
    pairs.round(4).to_csv(DATA / "brand_pairs.csv", index=False)
    pd.read_csv(TABLES / "regression_fixed_effects.csv").round(4).to_csv(DATA / "regression.csv",
                                                                          index=False)
    return df, cat, pairs


def export_theme():
    theme = {
        "name": "Pink Tax",
        "dataColors": [WOMEN, MEN, "#8a8983", "#eb6834", "#1baf7a", "#4a3aa7"],
        "background": "#FFFFFF", "foreground": "#1F1F1D", "tableAccent": WOMEN,
        "good": MEN, "neutral": NEUTRAL, "bad": WOMEN,
        "textClasses": {
            "title": {"fontFace": "Segoe UI Semibold", "fontSize": 14, "color": "#1F1F1D"},
            "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": "#5C5B57"},
            "callout": {"fontFace": "Segoe UI Semibold", "fontSize": 26, "color": "#1F1F1D"},
        },
    }
    (POWERBI / "PinkTax_theme.json").write_text(json.dumps(theme, indent=2))


def card(ax, x, y, w, h, value, label, color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc="white", ec="#e6e5e0", lw=1, transform=ax.transAxes))
    ax.text(x + 0.012, y + h * 0.58, value, transform=ax.transAxes, fontsize=19 if len(value) < 10 else 15,
            fontweight="bold", color=color, va="center")
    ax.text(x + 0.012, y + h * 0.2, label, transform=ax.transAxes, fontsize=8.5, color=INK_2,
            va="center")


def dashboard_mockup(df, cat, pairs):
    kpi = json.loads((TABLES / "kpis.json").read_text())
    fig = plt.figure(figsize=(16, 9), facecolor="#f6f5f2")
    bg = fig.add_axes([0, 0, 1, 1])
    bg.axis("off")
    bg.add_patch(plt.Rectangle((0, 0.915), 1, 0.085, color="#3b2a33", transform=bg.transAxes))
    bg.text(0.02, 0.957, "PINK TAX DASHBOARD  ·  Gender-based pricing in Indian online retail",
            color="white", fontsize=17, fontweight="bold", va="center", transform=bg.transAxes)
    bg.text(0.98, 0.957, "Slicers:  Source ▾   Segment ▾   Age group ▾   Category ▾",
            color="#f1d6e1", fontsize=10.5, ha="right", va="center", transform=bg.transAxes)

    cards = [
        (f"{kpi['products']:,}", "Products analysed", INK),
        (f"{kpi['categories']}", "Comparable categories", INK),
        (f"{kpi['cells_women_more']} / {kpi['cells_men_more']}", "Categories: women / men pay more", INK),
        (f"{kpi['pairs_geo_premium_pct']:+.1f}%", "Brand-matched gap (women vs men)", MEN),
        (f"{kpi['pairs_women_dearer_pct']:.0f}%", "Pairs where women's line is dearer", WOMEN),
        (f"{kpi['discount_mean_women']:.1f}% vs {kpi['discount_mean_men']:.1f}%",
         "Avg discount: women vs men", INK),
    ]
    for i, (v, l, c) in enumerate(cards):
        card(bg, 0.02 + i * 0.163, 0.79, 0.153, 0.1, v, l, c)

    # left: category premium bar chart
    ax1 = fig.add_axes([0.13, 0.06, 0.33, 0.68])
    c = cat.sort_values("premium_median_pct").copy()
    c["label"] = c.category + np.where(c.age_group == "Kids", " (kids)", "") + " · " + c.source
    c = pd.concat([c.head(10), c.tail(10)])
    col = c.direction.map({"Women pay more": WOMEN, "Men pay more": MEN,
                           "No significant gap": NEUTRAL})
    ax1.barh(c.label, c.premium_median_pct, color=col, height=0.7)
    ax1.axvline(0, color=INK_2, lw=1)
    ax1.tick_params(axis="y", labelsize=7.5)
    ax1.set_title("Median price gap by category (top & bottom 10)", fontsize=11)
    ax1.set_xlabel("Women vs men (%)", fontsize=8.5)
    ax1.grid(axis="y", visible=False)

    # middle-top: segment medians
    ax2 = fig.add_axes([0.53, 0.44, 0.2, 0.3])
    seg = df[df.age_group == "Adult"].groupby(["segment", "gender"]).mrp.median().unstack()
    x = np.arange(len(seg))
    ax2.bar(x - 0.2, seg["Women"], 0.38, color=WOMEN, label="Women")
    ax2.bar(x + 0.2, seg["Men"], 0.38, color=MEN, label="Men")
    ax2.set_xticks(x, [s.replace(" ", "\n") for s in seg.index], fontsize=7.5)
    ax2.set_title("Median MRP by segment (₹)", fontsize=11)
    ax2.legend(fontsize=7.5)
    ax2.grid(axis="x", visible=False)

    # middle-bottom: pairs outcome
    ax3 = fig.add_axes([0.53, 0.06, 0.2, 0.28])
    t = pd.crosstab(pairs.segment, pairs.outcome, normalize="index") * 100
    t = t[["Women's version dearer", "Within +/-2%", "Men's version dearer"]]
    left = np.zeros(len(t))
    for colname, colr in zip(t.columns, [WOMEN, NEUTRAL, MEN]):
        ax3.barh(t.index, t[colname], left=left, color=colr, height=0.6)
        left += t[colname].values
    ax3.tick_params(axis="y", labelsize=8)
    ax3.set_xlim(0, 100)
    ax3.legend(["Women's dearer", "Within ±2%", "Men's dearer"], fontsize=7, ncol=3,
               loc="upper center", bbox_to_anchor=(0.5, -0.1))
    ax3.set_title("Brand-matched pairs: who pays more? (%)", fontsize=11)
    ax3.grid(visible=False)

    # right: table visual
    ax4 = fig.add_axes([0.765, 0.06, 0.215, 0.68])
    ax4.axis("off")
    ax4.set_title("Largest Pink Tax pockets", fontsize=11, loc="left")
    top = cat[cat.direction == "Women pay more"].sort_values("premium_median_pct", ascending=False)
    rows = [["Category", "Men ₹", "Women ₹", "Gap"]] + [
        [f"{r.category}{' (kids)' if r.age_group == 'Kids' else ''}", f"{r.median_men:,.0f}",
         f"{r.median_women:,.0f}", f"{r.premium_median_pct:+.0f}%"] for r in top.itertuples()]
    tb = ax4.table(cellText=rows, loc="upper center", cellLoc="left", colWidths=[0.42, 0.18, 0.22, 0.16])
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1, 1.9)
    for (r, _), cell in tb.get_celld().items():
        cell.set_edgecolor("#e6e5e0")
        if r == 0:
            cell.set_facecolor("#3b2a33")
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
    ax4.text(0, 0.35, "Design mock-up generated in Python.\nBuild the live version in Power BI\n"
             "with PowerBI_Build_Guide.md.", fontsize=8.5, color=INK_2, transform=ax4.transAxes,
             va="top")
    fig.savefig(POWERBI / "dashboard_layout.png", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    df, cat, pairs = export_tables()
    export_theme()
    dashboard_mockup(df, cat, pairs)
    print("Power BI files written to", POWERBI)
