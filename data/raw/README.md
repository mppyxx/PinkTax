# Raw data (not committed)

The raw Kaggle files are large (~750 MB in total), so they are not stored in the repository.
Download them with:

```bash
python src/01_download_data.py
```

| File | Kaggle dataset | Rows | Used for |
|---|---|---|---|
| `myntra_products.csv` | [ashishjangra27/myntra-168k-products](https://www.kaggle.com/datasets/ashishjangra27/myntra-168k-products) | 168,029 | Apparel, footwear, accessories, perfume (men/women/boys/girls) |
| `bigbasket_products.csv` | [surajjha101/bigbasket-entire-product-list-28k-datapoints](https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints) | 27,555 | Deodorants and perfumes (Beauty & Hygiene) |
| `amazon_in_products_2023.csv` | [asaniczka/amazon-india-products-2023-1-5m-products](https://www.kaggle.com/datasets/asaniczka/amazon-india-products-2023-1-5m-products) | 1,589,160 | Personal care with pack sizes: deodorant, perfume, razor, trimmer, washes, shampoo |

All prices are in Indian Rupees (₹). The cleaned output is `data/processed/pinktax_master.csv`.
