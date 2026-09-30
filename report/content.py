"""Text of the internship report. Edit here and re-run build_report.py, or edit the .docx directly.

Markup used by the builder:
  ("h1", text)               chapter heading (new page, appears in contents)
  ("h2", text)               section heading (appears in contents)
  ("h3", text)               bold run-in sub-heading
  ("p", text)                justified paragraph; **bold** is supported
  ("bullets", [..])          bulleted list
  ("numbers", [..])          numbered list
  ("fig", path, caption, width_in)
  ("table", caption, [header], [[row], ..], [col widths in inches])
  ("pagebreak",)
"""

STUDENT = {
    "name": "Kanishka Shah",
    "enrolment": "231260131051",
    "guide": "Prof. Himani Patel",
    "branch": "Computer Science & Engineering",
    "hod": "Dr. Madhuri Parekh",
}

TITLE = "Pink Tax: A Data-Driven Analysis of Gender-Based Price Differences in Indian Online Retail"

ABSTRACT = [
    "The “Pink Tax” is more than a pricing issue. It raises a simple question: do products "
    "marketed to women actually cost more than comparable products marketed to men? This project uses "
    "data analysis to investigate gender-based price differences across everyday consumer products sold "
    "online in India. It compares similar items across categories, brands and product types, and all "
    "prices are in Indian Rupees (₹).",
    "Three public Kaggle datasets were combined: product listings from **Myntra** (fashion, footwear and "
    "accessories), **BigBasket** (beauty and hygiene) and **Amazon.in** (personal care). After cleaning, "
    "de-duplication, outlier removal and tagging each product by its target gender using product URLs "
    "and English and Hindi keywords, the final dataset contained **79,390 products** from **2,769 brands** "
    "in **44 comparable categories**. The analysis was done in Python (Pandas, NumPy, SciPy, Statsmodels, "
    "scikit-learn, Matplotlib, Seaborn and Plotly) on Google Colab, with an Excel workbook and a Power BI "
    "dashboard for reporting.",
    "The prices were examined through four lenses of increasing strictness. The first compared women's "
    "and men's prices within each category using non-parametric tests with bootstrap confidence intervals "
    "and false-discovery-rate correction. The second compared price per 100 ml for liquids. The third "
    "compared 860 brand-matched pairs, where the same brand sells a men's and a women's version in the "
    "same category. The fourth was a fixed-effects regression that controls for brand and category.",
    "The results show that **there is no blanket Pink Tax** in Indian online retail. Women paid "
    "significantly more in only 4 of 44 categories, while men paid more in 22. Within the same brand, the "
    "women's version was dearer in 27% of pairs and the men's version in 54%, and the typical gap was "
    "−5.9%. Personal-care liquids showed no significant difference per 100 ml. The Pink Tax does, "
    "however, appear consistently in specific pockets: girls' night suits (+78%), innerwear (+33%), kids' "
    "clothing sets (+11%) and women's sports shoes (+5%). Women's deodorants on BigBasket also cost 17% "
    "more at the selling price because they are discounted less. Much of the gap comes from brand mix and "
    "product differentiation rather than a uniform surcharge. The practical lesson for consumers is to "
    "compare unit prices and to look across the gender aisle.",
    "**Keywords:** Pink Tax, gender-based pricing, price discrimination, e-commerce, hypothesis testing, "
    "fixed-effects regression, data analytics, Python, Power BI.",
]

INTRODUCTION = [
    "The term **Pink Tax** describes the extra amount women are said to pay for products and services "
    "that are marketed to them, when an almost identical version marketed to men costs less. A razor in "
    "pink packaging, a “for her” deodorant or a girl's T-shirt may cost more than its male "
    "counterpart even when the materials and function are the same. Unlike a real tax, the money does not "
    "go to the government. It is a price difference created by marketing and pricing decisions.",
    "The issue became widely known after a 1994 study by the California Assembly, which led to the Gender "
    "Tax Repeal Act of 1995 for services. The best-known study of goods is the New York City Department of "
    "Consumer Affairs report *From Cradle to Cane* (2015). It compared nearly 800 products with clear "
    "male and female versions and found that women's products cost about 7% more on average, and 13% more "
    "for personal-care products. Later work has been more cautious. The U.S. Government Accountability "
    "Office (2018) found higher prices for women in 5 of 10 personal-care categories but could not "
    "attribute them to gender bias alone. Moshary, Tuchman and Bhatia (2021) found no systematic premium "
    "when truly identical products were compared.",
    "In India, public debate has focused mainly on the “tampon tax”, which ended when "
    "sanitary napkins were exempted from GST in July 2018. Gender-based pricing of everyday goods has "
    "received far less data-driven attention, even though online retail now makes it possible to observe "
    "the prices of tens of thousands of products at once.",
    "This project fills that gap with a reproducible data-analysis pipeline. It collects real product "
    "listings from three Indian e-commerce platforms, labels each product as targeted at women or men, "
    "and uses statistical tests, matched comparisons and regression to measure where the Pink Tax exists, "
    "how large it is and what explains it. The work was carried out during a 15-day summer internship. "
    "Chapter 1 introduces the internship, its aims and the tools used. Chapter 2 records the day-by-day "
    "activities and learning, and Chapter 3 presents the conclusions.",
]

CHAPTER1 = [
    ("h1", "Chapter 1: Introduction"),
    ("h2", "1.1 Introduction of Summer Internship"),
    ("p", "The summer internship was a 15-day, project-based programme in **data analytics**. Its purpose was "
          "to take a real-world question from idea to evidence: finding and understanding data, cleaning and "
          "transforming it, analysing it with statistics, and communicating the results through charts, "
          "spreadsheets and dashboards. The work was organised as a single end-to-end project, "
          "*the Pink Tax in Indian online retail*, so that every new skill was applied straight away to the "
          "same dataset."),
    ("p", "The internship was divided into four phases:"),
    ("bullets", [
        "**Foundations (Days 1–3):** problem understanding, literature review, setting up Python, "
        "Google Colab and GitHub, and revising NumPy and Pandas.",
        "**Data engineering (Days 4–7):** sourcing data from Kaggle, profiling it, cleaning it and "
        "engineering features such as gender, category and price per 100 ml.",
        "**Analysis (Days 8–13):** exploratory analysis, visualisation, hypothesis testing, "
        "brand-matched comparison, regression and a machine-learning check.",
        "**Reporting (Days 14–15):** an Excel workbook with live formulas, a Power BI dashboard, the "
        "GitHub repository and this report.",
    ]),
    ("p", "Each day ended with a short log of what was done, what was learned and what problems came up. "
          "Chapter 2 is based on these logs."),
    ("h2", "1.2 Aim & Objective"),
    ("p", "**Aim:** to find out, using real data and sound statistical methods, whether products marketed to "
          "women in India cost more than comparable products marketed to men, and where any such Pink Tax "
          "appears most consistently."),
    ("h3", "Objectives"),
    ("numbers", [
        "Build a clean, gender-tagged dataset of Indian consumer products from public sources.",
        "Compare women's and men's prices within each product category and test whether the differences "
        "are statistically significant.",
        "Compare like with like: price per 100 ml for liquids, and the same brand's men's and women's lines.",
        "Separate a true gender premium from brand and category effects using regression.",
        "Check whether discounts change the gap between the list price (MRP) and the price actually paid.",
        "Present the results in a Colab notebook, an Excel workbook and a Power BI dashboard, and publish "
        "the project on GitHub.",
    ]),
    ("h3", "Research questions and hypotheses"),
    ("bullets", [
        "**RQ1:** Within a product category, do women's products have higher prices than men's?",
        "**RQ2:** Does the gap survive when unit price, brand and category are held constant?",
        "**RQ3:** In which categories does the Pink Tax appear most consistently?",
        "**H₀:** the price distributions of women's and men's products are the same. "
        "**H₁:** they differ. The significance level is α = 0.05, with a false-discovery-rate "
        "correction.",
    ]),
    ("h2", "1.3 Tools & Technology used during Internship"),
    ("table", "Table 1.1: Tools and technologies used",
     ["Tool / Library", "Purpose in this project"],
     [["Python 3.11 with Google Colab / Jupyter", "Main language and notebooks for the complete, reproducible data pipeline"],
      ["NumPy and Pandas", "Numerical operations, bootstrap resampling; loading, cleaning, grouping and pivoting data"],
      ["Regular expressions (re)", "Extracting gender, category and pack size from product titles and URLs"],
      ["Matplotlib, Seaborn and Plotly", "Publication-quality static charts and an interactive chart with hover details"],
      ["SciPy and Statsmodels", "Mann-Whitney, Welch, Wilcoxon and chi-square tests; OLS / fixed-effects regression, FDR correction"],
      ["scikit-learn", "Random-forest price model, target encoding, permutation importance"],
      ["Microsoft Excel and OpenPyXL", "Workbook with COUNTIFS / AVERAGEIFS summaries, pivot-style tables, conditional formatting"],
      ["Power BI", "Star-schema data model, DAX measures and an interactive dashboard"],
      ["Git, GitHub and Kaggle", "Version control, publishing (github.com/mppyxx/PinkTax) and the data source"]],
     [2.0, 4.4]),
    ("h2", "1.4 Dataset Description"),
    ("p", "All data came from public Kaggle datasets, and every price is in Indian Rupees. The **MRP** "
          "(maximum retail price) is the list price printed by the brand. The **selling price** is the "
          "price after the platform's discount."),
    ("table", "Table 1.2: Datasets used",
     ["Source", "Raw size", "Used", "Content"],
     [["Myntra (2023)", "168,029 × 13", "72,771", "Apparel, footwear, accessories, perfume; men, women, boys, girls"],
      ["BigBasket (2022)", "27,555 × 10", "736", "Beauty & hygiene: deodorants and perfumes"],
      ["Amazon.in (2023)", "1,589,160 × 11", "5,883", "Personal care: deodorant, perfume, razor, trimmer, washes, shampoo"],
      ["Total", "", "79,390", "44 categories, 2,769 brands; adults: 46,022 men's and 28,906 women's items; kids: 4,462 items"]],
     [1.45, 1.35, 0.8, 2.8]),
]

# --------------------------------------------------------------------------- days
S = "../docs/screenshots/"
F = "../outputs/figures/"

DAYS = [
    # ------------------------------------------------------------------ 1
    [("h2", "Day-1: Orientation and Understanding the Pink Tax"),
     ("p", "**Objective:** understand the problem, review earlier research and turn a broad idea into "
           "questions that can be tested."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Attended the orientation session and discussed the project scope: an end-to-end data analytics "
         "study of gender-based pricing.",
         "Read the NYC Department of Consumer Affairs study *From Cradle to Cane* (2015). Women's products "
         "cost 7% more on average, and 13% more for personal care.",
         "Read the U.S. GAO report (2018) and the paper by Moshary et al. (2021), which argue that many "
         "gaps disappear when truly identical products are compared.",
         "Wrote down the research questions (RQ1–RQ3) and the null and alternative hypotheses.",
         "Planned the workflow shown in Figure 2.1.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "Good analysis starts with a precise question. “Do women pay more?” is too vague. "
           "“Within the same category and brand, is the women's version priced higher?” can be "
           "tested. I also learned the difference between the **Pink Tax** (a price gap between gendered "
           "versions of a product) and the **tampon tax** (a sales tax on menstrual products, removed in "
           "India in 2018)."),
     ("fig", F + "fig01_workflow.png", "Figure 2.1: Project workflow planned on Day 1", 6.3)],
    # ------------------------------------------------------------------ 2
    [("h2", "Day-2: Setting up the Development Environment"),
     ("p", "**Objective:** prepare a reproducible working environment for the project."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Set up Google Colab and a local Jupyter environment, and learned the difference between a "
         "hosted runtime and a local kernel.",
         "Installed and imported the main libraries: NumPy, Pandas, Matplotlib, Seaborn, Plotly, SciPy, "
         "Statsmodels, scikit-learn and OpenPyXL. Recorded their versions in *requirements.txt*.",
         "Created the GitHub repository **PinkTax** and a clear folder structure: *src/*, *data/*, "
         "*notebooks/*, *outputs/*, *excel/*, *powerbi/* and *report/*.",
         "Learned basic Git commands (*clone, add, commit, push*) and wrote a *.gitignore* so that large "
         "raw files are not uploaded.",
         "Wrote *config.py* to keep all paths and chart colours in one place.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "A project is only useful if someone else can run it. Keeping the code in numbered scripts "
           "(*01_download_data.py … 07_powerbi_export.py*) and the settings in one configuration file "
           "means the whole analysis can be reproduced with a few commands, locally or in Colab."),
     ("fig", S + "nb_cell03.png", "Figure 2.2: Importing the analysis libraries in the Colab notebook", 6.3),
     ("fig", S + "nb_cell00.png", "Figure 2.3: Notebook overview with the Open-in-Colab link", 5.2)],
    # ------------------------------------------------------------------ 3
    [("h2", "Day-3: Python Refresher – NumPy and Pandas"),
     ("p", "**Objective:** strengthen the Python data-handling skills needed for the project."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Revised NumPy arrays, vectorised operations, broadcasting and random number generation, which "
         "are used later for bootstrapping.",
         "Practised Pandas: Series and DataFrame, *loc/iloc* indexing, boolean filtering, *groupby*, "
         "*agg*, *pivot_table*, *merge* and *concat*.",
         "Learned the *.str* accessor for text columns: *contains*, *extract*, *replace* and *split*.",
         "Practised regular expressions such as *-(men|women|boys|girls)-*, which later pulled the gender "
         "out of Myntra product URLs.",
         "Solved small exercises: average price per brand, the most expensive category, and the share of "
         "discounted items.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "Vectorised Pandas code is much faster and clearer than Python loops. Filtering about 1.6 million "
           "Amazon rows took seconds with boolean masks. Regular expressions are a powerful tool for turning "
           "free text into structured features."),
     ("table", "Table 2.1: Pandas operations practised and where they were used",
      ["Operation", "Used for"],
      [["read_csv, info, describe", "Loading and profiling the raw files"],
       ["str.extract / str.contains", "Gender and category tagging, pack-size extraction"],
       ["drop_duplicates, dropna", "Cleaning"],
       ["groupby + agg / transform", "Category medians, outlier limits, fixed effects"],
       ["pivot_table, crosstab", "Summary tables and brand-matched pairs"]],
      [2.4, 4.0])],
    # ------------------------------------------------------------------ 4
    [("h2", "Day-4: Data Sourcing from Kaggle"),
     ("p", "**Objective:** find public datasets with real Indian prices that can be tagged by gender."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Searched Kaggle for “pink tax”, “gender price”, Myntra, Nykaa, BigBasket, "
         "Flipkart and Amazon India. No ready-made Pink Tax dataset exists, so product catalogues had "
         "to be used.",
         "Evaluated candidates against four criteria: prices in ₹, a way to identify the target gender, "
         "enough products per category, and a clear licence and source.",
         "Selected three datasets: **Myntra 168k products**, the **BigBasket product list** and **Amazon "
         "India products 2023** (1.5 million listings).",
         "Wrote *01_download_data.py* to download and unzip the files automatically through the Kaggle "
         "API, so that the download is reproducible.",
         "Loaded the files and checked their shapes and columns (Figure 2.4).",
     ]),
     ("h3", "Learning outcome"),
     ("p", "In real projects the perfect dataset rarely exists. The skill is to combine sources that each "
           "answer part of the question. Myntra covers fashion with gender in the URL, BigBasket labels "
           "men's and women's deodorants, and Amazon titles include pack sizes for unit-price comparison."),
     ("fig", S + "nb_cell07.png", "Figure 2.4: Loading the raw Myntra and BigBasket files with Pandas", 6.3)],
    # ------------------------------------------------------------------ 5
    [("h2", "Day-5: Data Understanding and Profiling"),
     ("p", "**Objective:** understand what each column means, how the data is stored and what quality "
           "problems exist."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Used *info()*, *describe()* and *value_counts()* to check data types, missing values and "
         "distributions.",
         "Found where the gender is stored in each source: in the product URL for Myntra, in the product "
         "type for BigBasket and only in the title for Amazon.",
         "Found that most Amazon titles are in **Hindi** (for example “पुरुषों "
         "के लिए” means “for men”), so English-only keywords would "
         "miss most products.",
         "Noted quality issues: zero list prices, duplicate listings, unisex and combo packs, and "
         "extreme prices.",
         "Decided to use MRP as the main price and the selling price as a second measure.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "Profiling before cleaning saves time. Checking gender labels on Myntra showed 58,436 women's, "
           "53,615 men's, 4,671 girls' and 4,209 boys' products, plus 43,823 without a gender tag. That "
           "told me how much usable data there was before writing any cleaning code."),
     ("fig", S + "nb_cell09.png", "Figure 2.5: Extracting the target gender from Myntra product URLs using a "
                                  "regular expression", 6.3)],
    # ------------------------------------------------------------------ 6
    [("h2", "Day-6: Data Cleaning"),
     ("p", "**Objective:** turn the raw files into a reliable, analysis-ready table."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Removed duplicate listings using product links, ASINs, or name + brand + price.",
         "Dropped products with zero or missing prices, and capped the selling price at the MRP.",
         "Removed unisex, “men and women”, couple and multipack products, because they have no "
         "single target gender.",
         "Kept only categories with at least 15 products for **each** gender, so that every comparison "
         "is between genuine alternatives.",
         "Removed outliers beyond **3 × IQR on the log price** within each category, a rule that suits "
         "right-skewed prices.",
         "Recorded every step in a cleaning log (Table 2.2).",
     ]),
     ("table", "Table 2.2: Cleaning log",
      ["Step", "Rows remaining"],
      [["Products in scope (Myntra 72,914 + BigBasket 7,273 + Amazon 62,078)", "142,265"],
       ["After gender and category tagging", "80,008"],
       ["After removing zero or missing prices", "79,817"],
       ["After keeping comparable categories (≥ 15 per gender)", "79,553"],
       ["After log-IQR outlier removal and final de-duplication", "79,390"]],
      [4.8, 1.6]),
     ("h3", "Learning outcome"),
     ("p", "Every cleaning rule is a decision that can change the result, so each rule must be justified and "
           "documented. Using the log scale for outliers was important. A normal IQR rule on raw prices "
           "would have removed many genuine premium products."),
     ("fig", S + "nb_cell14.png", "Figure 2.6: Cleaning log produced by the pipeline", 5.0)],
    # ------------------------------------------------------------------ 7
    [("h2", "Day-7: Feature Engineering – Gender, Category and Unit Price"),
     ("p", "**Objective:** create the variables needed for a fair comparison."),
     ("h3", "Activities performed"),
     ("bullets", [
         "**Gender:** built keyword rules in English (men, man's, him, gents, women, her, ladies, "
         "femme …) and Hindi (पुरुष, महिला). "
         "Titles that match both genders are excluded.",
         "**Category:** wrote ordered regular-expression rules. For example, *attar* is tested before "
         "*razor* because the Hindi word for “treasure” (ट्रेजर) "
         "contains the letters of “razor” (रेजर). I found and fixed this bug "
         "during spot checks.",
         "**Pack size and unit price:** extracted ml and g values from titles and calculated "
         "**₹ per 100 ml** for liquids.",
         "**Discount %** = (1 − selling price / MRP) × 100.",
         "**Segment:** grouped categories into Apparel, Footwear, Accessories and Personal Care, and "
         "added an age group (Adult or Kids).",
         "Saved the tidy master table (79,390 rows × 16 columns) as *pinktax_master.csv*.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "Automatic tagging must always be checked by reading real examples. Printing random samples for "
           "each category and gender showed mistakes that summary statistics would never reveal, such as "
           "hair-removal creams being counted as razors."),
     ("fig", S + "nb_cell12.png", "Figure 2.7: Output of the cleaning and tagging script: products per "
                                  "source, category and gender", 5.6)],
    # ------------------------------------------------------------------ 8
    [("h2", "Day-8: Exploratory Data Analysis (EDA)"),
     ("p", "**Objective:** understand the shape of the data before testing anything."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Built pivot tables of product counts and median prices by source, segment and gender.",
         "Checked the distributions. Prices are strongly right-skewed, so medians and log prices are "
         "better summaries than means.",
         "Compared means with medians. In personal care the mean women's price is 21% higher, but the "
         "median is 7% lower, because a few expensive women's perfumes pull the mean up.",
         "Found that the sample is unbalanced: Myntra lists far more men's shirts and T-shirts, and far "
         "more women's kurtas and night suits.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "EDA stops the analysis from reaching the wrong conclusions. Comparing overall averages would be "
           "misleading because men's and women's catalogues contain different mixes of products. Every "
           "later comparison was therefore made **within** a category."),
     ("fig", F + "fig02_dataset_composition.png", "Figure 2.8: Composition of the final dataset by source, "
                                                  "segment and gender", 6.0),
     ("fig", S + "nb_cell16.png", "Figure 2.9: Pivot table of product counts and median MRP", 5.6)],
    # ------------------------------------------------------------------ 9
    [("h2", "Day-9: Data Visualisation with Matplotlib, Seaborn and Plotly"),
     ("p", "**Objective:** design clear and honest charts that explain the data."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Chose one colour for women (pink) and one for men (blue) and checked that the pair can be told "
         "apart by colour-blind readers. The same colours are used in Python, Excel and Power BI.",
         "Drew box plots on a log scale (Figure 2.10), grouped bar charts, dot plots with confidence "
         "intervals, histograms and a correlation heatmap.",
         "Followed chart design rules: direct labels, a single axis, light grid lines, and titles that "
         "state what the chart shows.",
         "Built an interactive Plotly chart where hovering over a category shows the sample sizes, "
         "medians and p-value.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "A chart is an argument. The log scale made both cheap socks and expensive watches readable on "
           "one axis. The box plots already hint that adult women's median prices are not higher than men's "
           "in apparel and footwear."),
     ("fig", F + "fig03_price_distribution.png", "Figure 2.10: MRP distribution by segment and gender (adults)", 6.0),
     ("fig", S + "plotly_interactive.png", "Figure 2.11: Interactive Plotly chart with hover details", 6.3, 4.6)],
    # ------------------------------------------------------------------ 10
    [("h2", "Day-10: Hypothesis Testing Across 44 Categories"),
     ("p", "**Objective:** test, category by category, whether women's and men's prices differ."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Used the **Mann-Whitney U test**, which does not assume a normal distribution, and **Welch's "
         "t-test on log price**, which allows unequal variances.",
         "Measured the effect size with **Cohen's d** and computed **bootstrap 95% confidence intervals** "
         "(2,000 resamples) for the median premium.",
         "Corrected for testing 44 categories at once with the **Benjamini-Hochberg** false-discovery-rate "
         "method.",
         "Worked example: adult T-shirts on Myntra had a median of ₹999 for women vs ₹1,299 for "
         "men (−23%, p < 10⁻¹⁰⁰).",
     ]),
     ("h3", "Result"),
     ("p", "Women pay significantly more in **4 of 44** categories: girls' night suits (+78%), innerwear "
           "(+33%), kids' clothing sets (+11%) and sports shoes (+5%). Men pay more in **22** categories, "
           "including belts (−43%), blazers (−36%), sunglasses (−32%) and jackets (−25%). "
           "The other 18 categories show no significant gap."),
     ("fig", F + "fig04_category_premium.png", "Figure 2.12: Median price gap for 44 categories with 95% "
                                               "confidence intervals", 5.3, 4.35)],
    # ------------------------------------------------------------------ 11
    [("h2", "Day-11: Comparing Like with Like – Unit Price and Brand-Matched Pairs"),
     ("p", "**Objective:** remove the effect of pack size and brand from the comparison."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Compared **₹ per 100 ml** for deodorants, perfumes, body wash, face wash and shampoo. No "
         "category showed a significant gap. Deodorant, for example, was ₹210 vs ₹201 per "
         "100 ml (+4.6%, p = 0.80).",
         "Built **860 brand-matched pairs**, each one brand selling both a men's and a women's line in "
         "the same category, and compared the two median prices.",
         "Tested the pairs with the **Wilcoxon signed-rank test** and a **sign test**, and used a "
         "chi-square test to check whether the outcomes differ by segment.",
     ]),
     ("h3", "Result"),
     ("p", "The women's version was dearer in **27%** of pairs, the men's in **54%**, and 18% were "
           "within ±2%. The typical gap was **−5.9%** (95% CI −7.7% to −4.0%, "
           "p < 0.001). Personal care was the only balanced segment (35% vs 37%, p = 0.93), and the "
           "outcome depends on the segment (χ² = 37.0, p < 0.001)."),
     ("fig", F + "fig06_brand_pairs_scatter.png", "Figure 2.13: Brand-matched pairs. Points above the line "
                                                  "mean the women's line is dearer", 4.3),
     ("fig", F + "fig07_pairs_outcome.png", "Figure 2.14: Share of pairs where each version is dearer, by segment", 5.6)],
    # ------------------------------------------------------------------ 12
    [("h2", "Day-12: Regression with Fixed Effects (Statsmodels)"),
     ("p", "**Objective:** estimate the gender premium while controlling for brand and category."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Fitted OLS models of the form **log(MRP) = β·Female + group effects**, where "
         "eᵝ − 1 is the percentage premium.",
         "Used the *within* (demeaning) estimator for brand × category fixed effects and **clustered "
         "standard errors by brand**.",
         "Estimated separate models for each segment, for kids, and for price per 100 ml.",
         "Checked for a **composition effect**: kids' products look 18% dearer for girls overall, but the "
         "gap disappears within categories because girls' categories (kurta sets, clothing sets) are "
         "pricier in general.",
     ]),
     ("h3", "Result"),
     ("p", "Within the same brand and category, adult women's products are **7.7% cheaper** (95% CI "
           "−9.8% to −5.6%). Accessories show no gap (+0.4%, p = 0.93), and personal care per "
           "100 ml shows no gap (+1.2%, p = 0.63). The kids' premium is not significant (−4.8%, "
           "p = 0.38)."),
     ("fig", F + "fig08_regression_forest.png", "Figure 2.15: Fixed-effects estimates of the women's price premium", 6.0),
     ("fig", F + "fig11_composition_effect.png", "Figure 2.16: How the answer changes when like is compared "
                                                 "with like", 5.4)],
    # ------------------------------------------------------------------ 13
    [("h2", "Day-13: Discount Analysis and Machine Learning (scikit-learn)"),
     ("p", "**Objective:** check whether discounts change the picture, and measure how much gender really "
           "explains price."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Compared discounts. Women's items carry deeper discounts (**36.7% vs 32.9%**, p < 0.001), "
         "especially in apparel and accessories.",
         "Repeated the category tests on the **selling price**. The innerwear premium flips from +33% "
         "on MRP to −11% after discounts. BigBasket women's deodorants go from no gap to **+17%**, "
         "because they are discounted less. This is a Pink Tax at the point of sale.",
         "Trained a **random-forest** model (scikit-learn) to predict log price from category, segment, "
         "retailer, brand (target-encoded) and gender. It reached a test R² of 0.78.",
         "Used **permutation importance** to rank the features.",
     ]),
     ("h3", "Result"),
     ("p", "Brand (importance 0.97) and category (0.35) explain most of the price. Target gender adds "
           "only 0.02. Price is driven by *what* the product is and *who makes it*, not by *who it is "
           "marketed to*."),
     ("fig", F + "fig15_ml_feature_importance.png", "Figure 2.17: Permutation importance of each feature in "
                                                    "the random-forest model", 6.0),
     ("fig", F + "fig09_discount.png", "Figure 2.18: Average discount by segment and gender", 5.4)],
    # ------------------------------------------------------------------ 14
    [("h2", "Day-14: Excel Workbook – Formulas, Pivot Summaries and Charts"),
     ("p", "**Objective:** make the analysis available to Excel users without Python."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Loaded all 79,390 products into an **Excel Table** (*tbl_Products*) so that it can be filtered, "
         "sorted and pivoted.",
         "Built a **Category_Summary** sheet with live **COUNTIFS** and **AVERAGEIFS** formulas, "
         "for example =AVERAGEIFS(MRP, Source, A5, Category, D5, Gender, \"Women\"), next to the "
         "medians, confidence intervals and p-values from Python.",
         "Built a pivot-style **segment × gender** summary, a **Matched_Pairs** sheet with data bars, "
         "and a **Stats_Tests** sheet.",
         "Applied **conditional formatting**: a blue-to-pink colour scale on the premium and coloured "
         "result labels.",
         "Added native Excel bar charts and checked that the formulas give the same numbers as Python.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "Excel is still the most widely used analysis tool. Formulas that update when the data changes "
           "make a workbook reusable. Checking that the Excel formulas give the same numbers as Python is a "
           "quick way to validate both."),
     ("fig", S + "excel_category_summary_zoom.png", "Figure 2.19: Category_Summary sheet with formulas and "
                                               "conditional formatting", 6.3),
     ("fig", S + "excel_charts.png", "Figure 2.20: Native Excel charts", 6.3, 4.6)],
    # ------------------------------------------------------------------ 15
    [("h2", "Day-15: Power BI Dashboard, GitHub Publishing and Report"),
     ("p", "**Objective:** build an interactive dashboard and publish the complete project."),
     ("h3", "Activities performed"),
     ("bullets", [
         "Exported Power BI-ready tables and designed a **star schema**: *fact_products* linked to "
         "*dim_category*, with *category_premium* and *brand_pairs* as result tables.",
         "Loaded them through **Power Query**, set the data types and created **DAX measures** such as "
         "*Median MRP (Women)*, *Pink Tax % = DIVIDE([Median MRP (Women)], [Median MRP (Men)]) − 1*, "
         "*Pairs Women Dearer %* and a conditional-colour measure.",
         "Built the dashboard: six KPI cards, a category gap chart, segment medians, a "
         "brand-pair outcome chart, a table of the Pink Tax pockets, and slicers for source, segment, "
         "age group and category. Applied a custom JSON theme.",
         "Wrote the README, pushed everything to GitHub and completed this report.",
     ]),
     ("h3", "Learning outcome"),
     ("p", "A dashboard lets a non-technical user explore the result: selecting “Kids” or "
           "“Personal Care” in a slicer immediately updates every visual. Publishing the code "
           "and data on GitHub makes the whole study transparent and reproducible."),
     ("fig", "../powerbi/dashboard_layout.png", "Figure 2.21: Pink Tax dashboard design (Power BI)", 6.3)],
]

CONCLUSION = [
    ("h1", "Chapter 3: Conclusion"),
    ("h2", "3.1 Summary of Findings"),
    ("p", "This project set out to answer a simple question with real data: do products marketed to women "
          "in India cost more than comparable products marketed to men? After analysing 79,390 products from "
          "Myntra, BigBasket and Amazon.in, the answer is **“not in general, but yes in specific "
          "places.”**"),
    ("numbers", [
        "**No blanket Pink Tax.** Women pay significantly more in 4 of 44 categories and men pay more in 22. "
        "Within the same brand and category, adult women's products are about 7.7% cheaper.",
        "**The Pink Tax is concentrated** in girls' night suits (+78%), innerwear (+33%), kids' clothing "
        "sets (+11%) and sports shoes (+5%) at MRP, and in women's deodorants at the selling price (+17%).",
        "**Like-for-like comparisons remove most gaps.** Personal care per 100 ml shows no significant "
        "difference, and the raw kids' premium disappears within categories.",
        "**Brand and category drive price; gender barely does.** In the machine-learning model gender adds "
        "about 0.02 to R², compared with 0.97 for brand.",
        "**Discounts matter.** Women's items are discounted more deeply on average, so the MRP and the "
        "price actually paid can tell different stories.",
    ]),
    ("p", "These results agree with recent research that finds no systematic premium for identical "
          "products. The gaps reported in earlier studies mostly come from comparing differentiated products "
          "and different brand mixes. For consumers the practical advice is to compare **unit prices** "
          "and to look at the other gender's version of simple products such as razors, deodorants and "
          "basic clothing."),
    ("h2", "3.2 What I Learned from the Internship"),
    ("bullets", [
        "**Technical:** writing a complete, reproducible data pipeline in Python; advanced Pandas and "
        "regular expressions (including Hindi text); visualisation with Matplotlib, Seaborn and Plotly; "
        "Excel formulas and conditional formatting; Power Query, data modelling and DAX in Power BI; Git "
        "and GitHub.",
        "**Statistical:** choosing non-parametric tests for skewed data, bootstrap confidence intervals, "
        "multiple-testing correction, effect sizes, fixed-effects regression with clustered errors, "
        "composition effects (Simpson's paradox) and model interpretation with permutation importance.",
        "**Analytical thinking:** a headline number such as “women pay X% more” depends on "
        "*what is compared with what*. Checking assumptions and reading real examples matters as much as "
        "writing code.",
        "**Professional:** planning work in daily milestones, documenting decisions, and presenting findings "
        "honestly even when they differ from the popular expectation.",
    ]),
    ("h2", "3.3 Limitations and Future Scope"),
    ("bullets", [
        "Gender and category tags are based on keywords, so a small share of products may be mislabelled.",
        "“Comparable” is approximated by same category and same brand. Differences in fabric, fit "
        "and design remain.",
        "The data are one-time snapshots (2022–2023) of listed prices and do not include sales volumes.",
        "**Future work:** track prices over time with web scraping, match exact twin products (same SKU "
        "except gender), add offline stores and services such as salons and dry-cleaning, and use text "
        "similarity models to find near-identical products automatically.",
    ]),
]

REFERENCES = [
    "New York City Department of Consumer Affairs (2015). *From Cradle to Cane: The Cost of Being a Female "
    "Consumer – A Study of Gender Pricing in New York City.*",
    "U.S. Government Accountability Office (2018). *Consumer Protection: Gender-Related Price Differences "
    "for Goods and Services* (GAO-18-500).",
    "Moshary, S., Tuchman, A., & Bhatia, N. (2021). *Investigating the Pink Tax: Evidence against a "
    "Systematic Price Premium for Women in CPG.* SSRN Working Paper.",
    "Duesterhaus, M., Grauerholz, L., Weichsel, R., & Guittar, N. A. (2011). The cost of doing femininity: "
    "Gendered disparities in pricing of personal care products and services. *Gender Issues*, 28(4), "
    "175–191.",
    "State of California. *Gender Tax Repeal Act of 1995* (Civil Code \u00a751.6) and Assembly Bill "
    "AB-1287 (2022), *Price discrimination: gender*.",
    "Government of India, GST Council (2018). Exemption of sanitary napkins from GST, effective 27 July 2018.",
    "Kaggle datasets: *Myntra 168k Products* (ashishjangra27); *BigBasket Entire Product List* "
    "(surajjha101); *Amazon India Products 2023* (asaniczka).",
    "McKinney, W. (2022). *Python for Data Analysis* (3rd ed.). O'Reilly Media.",
    "Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal "
    "Statistical Society: Series B*, 57(1), 289–300.",
    "Project repository: https://github.com/mppyxx/PinkTax",
]
