# 👾 InstantEDA: One-Click Exploratory Data Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-red.svg)](https://streamlit.io)

An advanced, interactive web application that automates the entire Exploratory Data Analysis (EDA) workflow. Upload any CSV file and instantly generate a beautiful, comprehensive, and downloadable report.


---


###  UPDATE: App is now deployed on streamlit

🎉 **Test It Here** **[Instant-EDA](https://instant-eda-7vtzmrexjbygrqnlk2wqcx.streamlit.app/)**

---
### ✨ Key Features

This tool goes beyond basic EDA to provide deep, actionable insights:

-   **📊 Comprehensive Data Profiling:** Instant overview of rows, columns, missing data, and duplicates.
-   **⚠️ Automated Health & Outlier Reports:** Proactively identifies columns with high nullity, no variance, high cardinality, and potential outliers using the IQR method.
-   **📈 Rich Interactive Visualizations:**
    -   **Univariate:** Histograms and bar plots for every column.
    -   **Bivariate:** Correlation heatmaps, grouped bar charts for categorical interactions, and box plots for numerical vs. categorical data.
-   **🤖 ML Preprocessing Suggestions:** Provides heuristic-based suggestions and ready-to-use code snippets for feature engineering (scaling, encoding, transformations).
-   **📄 Beautiful, Exportable Reports:** Generate a comprehensive and visually appealing HTML report with a single click, complete with all visualizations and your personal watermark.

---

### 🛠️ Tech Stack

-   **Backend:** Python
-   **Data Manipulation:** Pandas
-   **Web Framework:** Streamlit
-   **Visualization:** Plotly, Seaborn
--

### ⚙️ How to Run Locally

To run this project on your own machine, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/huzaifakhallid/Instant-EDA.git
cd Instant-EDA
```

**2. Create and activate a virtual environment:**
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install the required dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the Streamlit application:**
```bash
streamlit run app.py
```
The application should now be open in your web browser!

---

### 📂 Project Structure

```
Instant-EDA/
│
├── core/
│   ├── __init__.py         # Makes 'core' a Python package
│   ├── analyzer.py       # All data analysis and plotting functions
│   └── report.py         # Logic for generating the HTML report
│
├── app.py                  # The main Streamlit UI application file
├── requirements.txt        # Project dependencies
├── README.md               # You are here!
└── LICENSE                 # Project license
```

---

### 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Created with ❤️ by [Huzaifa](https://github.com/huzaifakhallid)
