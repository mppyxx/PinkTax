"""Step 2 - Clean the raw Kaggle files, tag each product by target gender and
product category, and build one tidy master table.

Output: data/processed/pinktax_master.csv  (one row per product)

Columns
    source, product_id, product_name, brand, segment, category, gender,
    age_group, mrp, selling_price, discount_pct, size_value, size_unit,
    unit_price_100, rating, rating_count
"""
import re

import numpy as np
import pandas as pd

from config import PROCESSED, RAW

MEN_WORDS = r"\b(?:men|man|mens|men's|male|him|his|gents|gentleman|homme|boys?)\b"
WOMEN_WORDS = r"\b(?:women|woman|womens|women's|female|her|ladies|lady|girls?|femme|donna)\b"
MEN_HI = "पुरुष"
WOMEN_HI = "महिला"
UNISEX_WORDS = r"\b(?:unisex|couple|couples|men\s*(?:&|and|/)\s*women|women\s*(?:&|and|/)\s*men|him\s*(?:&|and)\s*her|his\s*(?:&|and)\s*hers)\b"
MULTIPACK = r"(?:pack of\s*\d|set of\s*\d|combo|\b\d+\s*x\s*\d+|gift set|kit\b|\bduo\b|trio|का पैक|का सेट|कॉम्बो)"


# --------------------------------------------------------------------------- helpers
def gender_from_text(text: pd.Series) -> pd.Series:
    t = text.fillna("").str.lower()
    men = t.str.contains(MEN_WORDS) | t.str.contains(MEN_HI)
    women = t.str.contains(WOMEN_WORDS) | t.str.contains(WOMEN_HI)
    unisex = t.str.contains(UNISEX_WORDS)
    out = pd.Series(pd.NA, index=text.index, dtype="object")
    out[men & ~women & ~unisex] = "Men"
    out[women & ~men & ~unisex] = "Women"
    return out


def extract_size(text: pd.Series):
    """Return (value, unit) for the first ml / g quantity in a product title."""
    t = text.fillna("").str.lower()
    ml = t.str.extract(r"(\d+(?:\.\d+)?)\s?(?:ml|मिली|मिलीलीटर|एमएल)\b")[0].astype(float)
    ltr = t.str.extract(r"(\d+(?:\.\d+)?)\s?(?:l|ltr|litre|liter)\b")[0].astype(float) * 1000
    gm = t.str.extract(r"(\d+(?:\.\d+)?)\s?(?:g|gm|gms|gram|grams|ग्राम)\b")[0].astype(float)
    value = ml.fillna(ltr)
    unit = pd.Series(np.where(value.notna(), "ml", None), index=text.index, dtype="object")
    value = value.fillna(gm)
    unit[unit.isna() & gm.notna()] = "g"
    value[(value < 5) | (value > 2000)] = np.nan  # implausible pack sizes
    unit[value.isna()] = None
    return value, unit


def classify(text: pd.Series, rules: list[tuple[str, str]]) -> pd.Series:
    """First matching (category, regex) wins."""
    t = text.fillna("").str.lower()
    out = pd.Series(pd.NA, index=text.index, dtype="object")
    for name, pattern in rules:
        hit = out.isna() & t.str.contains(pattern)
        out[hit] = name
    return out


GENERIC_FIRST_WORDS = {"THE", "A", "NEW", "PREMIUM", "LUXURY", "ORIGINAL", "BEST", "SUPER"}


def first_word_brand(title: pd.Series) -> pd.Series:
    """Amazon titles start with the brand; use two words when the first is generic ("The Man ...")."""
    words = title.fillna("").str.strip().str.split()
    first = words.str[0].fillna("").str.replace(r"[^A-Za-z0-9&]", "", regex=True).str.upper()
    second = words.str[1].fillna("").str.replace(r"[^A-Za-z0-9&]", "", regex=True).str.upper()
    brand = first.where(~first.isin(GENERIC_FIRST_WORDS), first + " " + second)
    return brand.replace("", np.nan)


# Personal-care categories (order = priority when a title matches several).
PERSONAL_CARE_RULES = [
    ("Perfume", r"attar|ittar|अतार|इत्र"),
    ("Trimmer", r"trimmer|ट्रिमर|epilator"),
    ("Hair Removal Cream", r"hair removal cream|depilatory|रिमूवल क्रीम|hair eraser|हेयर इरेज़र"),
    ("Razor", r"razor|(?<![\u0900-\u097F])(?:रेज़र|रेजर)|cartridge"),
    ("Face Wash", r"face ?wash|फेस वॉश|फेस वाश|facewash|face cleanser"),
    ("Body Wash", r"body ?wash|shower gel|बॉडी वॉश|शॉवर जेल"),
    ("Shampoo", r"shampoo|शैम्पू"),
    ("Soap", r"\bsoap\b|bathing bar|साबुन"),
    ("Deodorant", r"deodorant|\bdeo\b|body spray|roll[- ]?on|डिओडोरेंट|डियो|बॉडी स्प्रे"),
    ("Perfume", r"perfume|parfum|eau de|\bedp\b|\bedt\b|cologne|attar|ittar|परफ्यूम|इत्र"),
    ("Moisturiser & Lotion", r"moisturi[sz]er|body lotion|face cream|day cream|night cream|body butter"),
    ("Talc", r"talc|powder"),
    ("Soap", r"\bsoap\b|bathing bar|साबुन"),
]

MYNTRA_ADULT = {
    "tshirts": "T-Shirts", "shirts": "Shirts", "jeans": "Jeans", "trousers": "Trousers",
    "track-pants": "Track Pants", "shorts": "Shorts", "jackets": "Jackets",
    "sweatshirts": "Sweatshirts", "sweaters": "Sweaters", "blazers": "Blazers",
    "kurtas": "Kurtas", "night-suits": "Night Suits", "lounge-pants": "Lounge Pants",
    "briefs": "Innerwear (Briefs)", "socks": "Socks", "tracksuits": "Tracksuits",
    "casual-shoes": "Casual Shoes", "sports-shoes": "Sports Shoes", "flip-flops": "Flip-Flops",
    "watches": "Watches", "wallets": "Wallets", "belts": "Belts", "sunglasses": "Sunglasses",
    "perfume-and-body-mist": "Perfume",
}
MYNTRA_KIDS = {
    "tshirts": "T-Shirts", "shorts": "Shorts", "jeans": "Jeans", "track-pants": "Track Pants",
    "trousers": "Trousers", "sweatshirts": "Sweatshirts", "casual-shoes": "Casual Shoes",
    "night-suits": "Night Suits", "clothing-set": "Clothing Sets", "kurta-sets": "Kurta Sets",
}
ACCESSORIES = {"Watches", "Wallets", "Belts", "Sunglasses"}
FOOTWEAR = {"Casual Shoes", "Sports Shoes", "Flip-Flops"}


# --------------------------------------------------------------------------- sources
def load_myntra() -> pd.DataFrame:
    df = pd.read_csv(RAW / "myntra_products.csv")
    df = df.drop_duplicates("product_link")
    who = df["product_link"].str.extract(r"-(men|women|boys|girls|unisex)-")[0]
    df["gender"] = who.map({"men": "Men", "boys": "Men", "women": "Women", "girls": "Women"})
    df["age_group"] = who.map({"men": "Adult", "women": "Adult", "boys": "Kids", "girls": "Kids"})
    adult = df["age_group"].eq("Adult") & df["product_tag"].isin(MYNTRA_ADULT)
    kids = df["age_group"].eq("Kids") & df["product_tag"].isin(MYNTRA_KIDS)
    df = df[adult | kids].copy()
    df["category"] = np.where(df["age_group"].eq("Adult"),
                              df["product_tag"].map(MYNTRA_ADULT),
                              df["product_tag"].map(MYNTRA_KIDS))
    df["segment"] = np.select(
        [df["category"].isin(ACCESSORIES), df["category"].isin(FOOTWEAR),
         df["category"].eq("Perfume")],
        ["Accessories", "Footwear", "Personal Care"], default="Apparel")
    out = pd.DataFrame({
        "source": "Myntra",
        "product_id": df["product_link"].str.extract(r"/(\d+)/buy")[0].fillna(df["product_link"]),
        "product_name": df["product_name"],
        "brand": df["brand_name"].str.strip().str.upper(),
        "segment": df["segment"], "category": df["category"],
        "gender": df["gender"], "age_group": df["age_group"],
        "mrp": df["marked_price"].astype(float),
        "selling_price": df["discounted_price"].astype(float),
        "size_value": np.nan, "size_unit": None,
        "rating": df["rating"].replace(0, np.nan), "rating_count": df["rating_count"],
    })
    return out


def load_bigbasket() -> pd.DataFrame:
    df = pd.read_csv(RAW / "bigbasket_products.csv")
    df = df[df["category"].eq("Beauty & Hygiene")].drop_duplicates(["product", "brand", "market_price"])
    text = df["product"].fillna("") + " " + df["type"].fillna("")
    g = gender_from_text(df["product"])
    g[df["type"].eq("Men's Deodorants")] = "Men"
    g[df["type"].eq("Women's Deodorants")] = "Women"
    g[g.isna() & df["sub_category"].eq("Men's Grooming")] = "Men"
    cat = classify(text, PERSONAL_CARE_RULES)
    cat[df["type"].isin(["Men's Deodorants", "Women's Deodorants"])] = "Deodorant"
    cat[cat.isna() & df["type"].isin(["Eau De Toilette", "Eau De Parfum", "Perfume", "Attar",
                                        "Eau De Cologne", "Body Sprays & Mists"])] = "Perfume"
    size_v, size_u = extract_size(df["product"])
    out = pd.DataFrame({
        "source": "BigBasket", "product_id": df["index"].astype(str),
        "product_name": df["product"], "brand": df["brand"].str.strip().str.upper(),
        "segment": "Personal Care", "category": cat, "gender": g, "age_group": "Adult",
        "mrp": df["market_price"].astype(float), "selling_price": df["sale_price"].astype(float),
        "size_value": size_v, "size_unit": size_u,
        "rating": df["rating"], "rating_count": np.nan,
    })
    return out


def load_amazon() -> pd.DataFrame:
    pc_cats = ["खुशबू", "स्नान और शावर", "त्वचा की देखभाल", "बालों की देखभाल",
               "व्यक्तिगत देखभाल", "Men's Grooming store", "व्यक्तिगत देखभाल के उपकरण"]
    df = pd.read_csv(RAW / "amazon_in_products_2023.csv",
                     usecols=["asin", "title", "stars", "reviews", "price", "listPrice",
                              "categoryName", "boughtInLastMonth"])
    df = df[df["categoryName"].isin(pc_cats)].drop_duplicates("asin")
    df = df[~df["title"].str.lower().str.contains(MULTIPACK)]
    g = gender_from_text(df["title"])
    cat = classify(df["title"], PERSONAL_CARE_RULES)
    size_v, size_u = extract_size(df["title"])
    mrp = df["listPrice"].where(df["listPrice"] > 0, df["price"])
    out = pd.DataFrame({
        "source": "Amazon.in", "product_id": df["asin"], "product_name": df["title"],
        "brand": first_word_brand(df["title"]), "segment": "Personal Care",
        "category": cat, "gender": g, "age_group": "Adult",
        "mrp": mrp.astype(float), "selling_price": df["price"].astype(float),
        "size_value": size_v, "size_unit": size_u,
        "rating": df["stars"].replace(0, np.nan), "rating_count": df["reviews"],
    })
    return out


# --------------------------------------------------------------------------- cleaning
def remove_outliers(df: pd.DataFrame, col="mrp", k=3.0) -> pd.DataFrame:
    """Drop prices beyond k * IQR on the log scale within each source-category-age cell."""
    logp = np.log(df[col])
    grp = df.groupby(["source", "category", "age_group"])[col]
    q1 = grp.transform(lambda s: np.log(s).quantile(0.25))
    q3 = grp.transform(lambda s: np.log(s).quantile(0.75))
    iqr = q3 - q1
    keep = (logp >= q1 - k * iqr) & (logp <= q3 + k * iqr)
    return df[keep]


def build_master() -> pd.DataFrame:
    frames = {"Myntra": load_myntra(), "BigBasket": load_bigbasket(), "Amazon.in": load_amazon()}
    log = []
    for name, f in frames.items():
        log.append((name, "raw rows in scope", len(f)))
    df = pd.concat(frames.values(), ignore_index=True)

    df = df.dropna(subset=["gender", "category"])
    log.append(("all", "after gender + category tagging", len(df)))
    df = df[(df["mrp"] > 0) & (df["selling_price"] > 0)]
    df["selling_price"] = df[["selling_price", "mrp"]].min(axis=1)
    log.append(("all", "after removing zero / missing prices", len(df)))

    # keep only categories that have a meaningful number of BOTH genders
    counts = df.groupby(["source", "category", "age_group", "gender"]).size().unstack(fill_value=0)
    ok = counts[(counts.get("Men", 0) >= 15) & (counts.get("Women", 0) >= 15)].index
    df = df.set_index(["source", "category", "age_group"]).loc[lambda d: d.index.isin(ok)].reset_index()
    log.append(("all", "after keeping comparable categories (>=15 per gender)", len(df)))

    df = remove_outliers(df)
    log.append(("all", "after log-IQR outlier removal", len(df)))

    df["discount_pct"] = (1 - df["selling_price"] / df["mrp"]) * 100
    liquid = df["size_unit"].notna() & df["category"].isin(
        ["Deodorant", "Perfume", "Body Wash", "Face Wash", "Shampoo", "Moisturiser & Lotion",
         "Hair Removal Cream", "Talc", "Soap"])
    df["unit_price_100"] = np.where(liquid, df["mrp"] / df["size_value"] * 100, np.nan)
    df = df.drop_duplicates(["source", "product_id"])

    cols = ["source", "product_id", "product_name", "brand", "segment", "category", "gender",
            "age_group", "mrp", "selling_price", "discount_pct", "size_value", "size_unit",
            "unit_price_100", "rating", "rating_count"]
    df = df[cols].sort_values(["source", "segment", "category", "gender"]).reset_index(drop=True)
    pd.DataFrame(log, columns=["source", "step", "rows"]).to_csv(
        PROCESSED / "cleaning_log.csv", index=False)
    return df


if __name__ == "__main__":
    master = build_master()
    master.to_csv(PROCESSED / "pinktax_master.csv", index=False)
    print(pd.read_csv(PROCESSED / "cleaning_log.csv").to_string(index=False))
    print(f"\nMaster table: {len(master):,} products")
    print(master.groupby(["source", "gender"]).size().unstack())
    print(master.groupby(["source", "age_group", "category", "gender"]).size().unstack().to_string())
