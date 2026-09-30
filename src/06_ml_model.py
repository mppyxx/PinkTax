"""Step 6 - Machine-learning check with scikit-learn, plus an interactive Plotly chart.

Question: once we know a product's category, segment, source and brand, how much
extra does knowing its target gender help predict its price?

Model: RandomForestRegressor on log(MRP) with one-hot category / segment / source,
a target-encoded brand, and a Female flag. We report test R^2 and permutation
importance (drop in R^2 when a feature is shuffled).
"""
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, TargetEncoder

from config import FIGURES, INK_2, MEN, NEUTRAL, PROCESSED, ROOT, TABLES, WOMEN, set_style

set_style()


def main():
    df = pd.read_csv(PROCESSED / "pinktax_master.csv", low_memory=False)
    df = df.dropna(subset=["brand"])
    df["female"] = (df.gender == "Women").astype(int)
    df["kids"] = (df.age_group == "Kids").astype(int)
    X = df[["category", "segment", "source", "brand", "female", "kids"]]
    y = np.log(df["mrp"])
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42,
                                              stratify=df["source"])

    pre = ColumnTransformer([
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=10),
         ["category", "segment", "source"]),
        ("brand", TargetEncoder(random_state=42), ["brand"]),
    ], remainder="passthrough")
    model = Pipeline([("prep", pre),
                      ("rf", RandomForestRegressor(n_estimators=200, min_samples_leaf=5,
                                                   n_jobs=-1, random_state=42))])
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    metrics = {"r2_test": r2_score(y_te, pred),
               "mae_log": mean_absolute_error(y_te, pred),
               "median_abs_pct_error": float(np.median(np.abs(np.exp(pred - y_te) - 1)) * 100)}

    sample = X_te.sample(6000, random_state=1)
    imp = permutation_importance(model, sample, y_te.loc[sample.index], n_repeats=5,
                                 random_state=42, n_jobs=-1)
    imp_df = (pd.DataFrame({"feature": sample.columns, "importance": imp.importances_mean,
                            "std": imp.importances_std})
              .sort_values("importance", ascending=False))
    imp_df.to_csv(TABLES / "ml_permutation_importance.csv", index=False)
    pd.DataFrame([metrics]).to_csv(TABLES / "ml_metrics.csv", index=False)
    print(metrics)
    print(imp_df.to_string(index=False))

    # chart
    names = {"brand": "Brand", "category": "Product category", "segment": "Segment",
             "source": "Retailer", "female": "Target gender (women)", "kids": "Kids vs adult"}
    d = imp_df.assign(label=imp_df.feature.map(names)).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    colors = [WOMEN if f == "female" else NEUTRAL if f == "kids" else MEN for f in d.feature]
    ax.barh(d.label, d.importance, xerr=d["std"], color=colors, height=0.6,
            error_kw={"ecolor": INK_2, "lw": 1})
    for i, v in enumerate(d.importance):
        ax.text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=8.5)
    ax.set_xlabel("Drop in test R² when the feature is shuffled (permutation importance)")
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Random-forest price model (test R² = {metrics['r2_test']:.2f}): what drives price?")
    fig.savefig(FIGURES / "fig15_ml_feature_importance.png", facecolor="white")
    plt.close(fig)

    # interactive Plotly chart (open outputs/interactive/category_premium.html in a browser)
    cat = pd.read_csv(TABLES / "category_premium_mrp.csv")
    cat["label"] = cat.category + np.where(cat.age_group == "Kids", " (kids)", "") + " · " + cat.source
    cat = cat.sort_values("premium_median_pct")
    figp = px.scatter(
        cat, x="premium_median_pct", y="label", color="direction",
        color_discrete_map={"Women pay more": WOMEN, "Men pay more": MEN,
                            "No significant gap": NEUTRAL},
        error_x=cat.ci_high_pct - cat.premium_median_pct,
        error_x_minus=cat.premium_median_pct - cat.ci_low_pct,
        hover_data={"n_men": True, "n_women": True, "median_men": ":,.0f",
                    "median_women": ":,.0f", "p_adj_bh": ":.4f", "label": False},
        labels={"premium_median_pct": "Women's median MRP vs men's (%)", "label": ""},
        title="Pink Tax by category - hover for details", height=1100)
    figp.add_vline(x=0, line_color="#5c5b57")
    figp.update_yaxes(categoryorder="array", categoryarray=cat.label.tolist())
    figp.update_layout(template="plotly_white", legend_title_text="")
    out = ROOT / "outputs" / "interactive"
    out.mkdir(exist_ok=True)
    figp.write_html(out / "category_premium.html", include_plotlyjs="cdn")


if __name__ == "__main__":
    main()
