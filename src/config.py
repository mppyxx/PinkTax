"""Shared paths, dataset sources and chart styling for the Pink Tax project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "outputs" / "figures"
TABLES = ROOT / "outputs" / "tables"
EXCEL = ROOT / "excel"
POWERBI = ROOT / "powerbi"

for _p in (RAW, PROCESSED, FIGURES, TABLES, EXCEL, POWERBI):
    _p.mkdir(parents=True, exist_ok=True)

# Public Kaggle datasets used in the project (all prices in Indian Rupees).
KAGGLE_DATASETS = {
    "myntra": {
        "ref": "ashishjangra27/myntra-168k-products",
        "file": "data.csv",
        "save_as": "myntra_products.csv",
    },
    "bigbasket": {
        "ref": "surajjha101/bigbasket-entire-product-list-28k-datapoints",
        "file": "BigBasket Products.csv",
        "save_as": "bigbasket_products.csv",
    },
    "amazon": {
        "ref": "asaniczka/amazon-india-products-2023-1-5m-products",
        "file": "amz_in_total_products_data_processed.csv",
        "save_as": "amazon_in_products_2023.csv",
    },
}

# Colours: validated for colour-vision deficiency (CVD delta-E 13.8, contrast >= 3:1).
WOMEN = "#d6457f"
MEN = "#2a78d6"
NEUTRAL = "#b9b8b2"
INK = "#1f1f1d"
INK_2 = "#5c5b57"
GRID = "#e6e5e0"
GENDER_COLORS = {"Women": WOMEN, "Men": MEN}


def set_style():
    """Apply one consistent Matplotlib/Seaborn look to every chart."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelcolor": INK_2,
        "axes.edgecolor": GRID,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "text.color": INK,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
