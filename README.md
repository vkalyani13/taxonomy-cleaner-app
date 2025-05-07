# 🔬 Taxonomy Cleaner App

This is a **Streamlit web application** built to clean, validate, and standardize mammal taxonomy data using the [GBIF Species API](https://www.gbif.org/developer/species). Designed for researchers and data managers working with biological specimen data, this tool automatically corrects taxonomic fields and flags rows needing review.

---

## 🔍 Features

* 📁 Upload `.xlsx` Excel files with taxonomic specimen data
* ✅ Validates species names via GBIF API
* 🔄 Automatically corrects `ORDER`, `FAMILY`, and `GENUS` columns based on GBIF matches
* 🚩 Flags missing, generic, or suspicious data entries
* 📝 Generates review summaries and correction notes per row
* 📦 Download the final cleaned Excel file with review columns

---

## 📂 Required Input Format

Your Excel file must include at least the following column:

* `Species`

Optional (but recommended) columns for full cleaning support:

* `ORDER`
* `FAMILY`
* `GENUS`
* `AGE`, `CONDITION`, `COMPLETENESS`, `PHOTO?`, `RANK`, etc.

---

## 🚀 Run the App Locally

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/taxonomy-cleaner-app.git
   cd taxonomy-cleaner-app
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the app**:

   ```bash
   streamlit run app.py
   ```

4. **Open in browser** (usually at [http://localhost:8501](http://localhost:8501))

---

## 🧪 Output Columns

The final downloaded Excel file will include these additional columns:

* `species_validation_status` – Result from GBIF match
* `taxonomy_hierarchy_issues` – Flags mismatches in ORDER/FAMILY/GENUS
* `correction_note` – Shows what values were auto-corrected
* `row_issue_summary` – Summarizes missing or suspicious fields
* `needs_review` – Boolean flag if row needs attention

---

## 🌐 Deploy It Online

You can deploy this app publicly using [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push your code to GitHub
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **“New App”**, select your repo, and deploy

You’ll get a link like:

```
[https://your-username.streamlit.app](https://taxonomy-cleaner-app-vmat73k6zug3lenvma4tzd.streamlit.app)
```

---

## 📦 Dependencies

Your `requirements.txt` should include:

```
streamlit
pandas
openpyxl
requests
```

---

## 👩‍🔬 Project Context

This tool was developed as part of a data cleaning initiative at Indiana University to standardize mammal specimen taxonomy data for research and public database publication.

---

## 📚 Built With

* [Streamlit](https://streamlit.io/)
* [GBIF API](https://www.gbif.org/developer/species)
* [Pandas](https://pandas.pydata.org/)
* [OpenPyXL](https://openpyxl.readthedocs.io/)

---

## 🙋‍♀️ Maintainer

**Venkata Kalyani Vemula**

---
