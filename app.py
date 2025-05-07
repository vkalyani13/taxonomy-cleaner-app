import streamlit as st
import pandas as pd
import requests
import io
import time
st.set_page_config(page_title="Taxonomy Cleaner", layout="wide")
st.title("🧬 Taxonomy Cleaner using GBIF API")
#GBIF API base
GBIF_API = "https://api.gbif.org/v1/species/match?name="
#File upload
uploaded_file = st.file_uploader("📁 Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, dtype=str)
    st.success("✅ File uploaded successfully!")
    st.write("📄 First few rows of the uploaded file:")
    st.dataframe(df.head())
    if "Species" not in df.columns:
        st.error("❌ The file must contain a 'Species' column.")
    else:
        if "GENUS" not in df.columns:
            df["GENUS"] = df["Species"].astype(str).str.strip().str.split().str[0]
        important_columns = [
            "Original Catalog Number", "ORDER", "FAMILY", "SUBFAMILY",
            "Species", "Common Name", "AGE", "CONDITION",
            "COMPLETENESS", "RANK", "PHOTO?"
        ]
        def identify_missing_fields(row):
            missing = [col for col in important_columns if pd.isna(row.get(col)) or str(row.get(col)).strip() == ""]
            return ", ".join(missing) if missing else ""
        suspicious_terms = {
            "Species": ["undetermined", "unknown", "sp.", "cf."],
            "Common Name": ["undetermined", "unknown"],
            "AGE": ["indeterminate", "unknown"],
            "CONDITION": ["poor", "fair"],
            "COMPLETENESS": ["fragment", "element"]
        }
        def identify_suspicious_fields(row):
            flagged = []
            for col, terms in suspicious_terms.items():
                val = str(row.get(col, "")).lower()
                if any(term in val for term in terms):
                    flagged.append(col)
            return ", ".join(flagged) if flagged else ""
        def compare_field(field_value, gbif_value, label):
            if pd.isna(field_value) or pd.isna(gbif_value):
                return ""
            if str(field_value).strip().lower() != str(gbif_value).strip().lower():
                return f"{label} mismatch"
            return ""
        def validate_taxonomic_hierarchy(row):
            species = row.get("Species")
            if pd.isna(species) or str(species).strip() == "":
                return "Missing species"
            species_lower = species.lower()
            if any(term in species_lower for term in ["sp.", "cf.", "undetermined", "unknown"]):
                return "Generic/Undetermined species"
            try:
                response = requests.get(GBIF_API + requests.utils.quote(species), timeout=10)
                data = response.json()
                if data.get("proxy", False):
                    return "Proxy match"
                mismatches = []
                mismatches.append(compare_field(row.get("ORDER"), data.get("order"), "ORDER"))
                mismatches.append(compare_field(row.get("FAMILY"), data.get("family"), "FAMILY"))
                mismatches.append(compare_field(row.get("GENUS"), data.get("genus"), "GENUS"))
                return ", ".join([m for m in mismatches if m])
            except:
                return "GBIF error"
        def compare_and_correct(row, gbif_data):
            correction_log = []
            def check_and_update(field, gbif_value):
                original = str(row.get(field)).strip() if pd.notna(row.get(field)) else ""
                gbif_clean = str(gbif_value).strip() if gbif_value else ""
                if original.lower() != gbif_clean.lower() and gbif_clean:
                    correction_log.append(f"{field}: '{original}' → '{gbif_clean}'")
                    df.at[row.name, field] = gbif_clean
            check_and_update("ORDER", gbif_data.get("order"))
            check_and_update("FAMILY", gbif_data.get("family"))
            check_and_update("GENUS", gbif_data.get("genus"))
            return row, "; ".join(correction_log)
        def auto_correct_row(row):
            species = row.get("Species")
            if pd.isna(species) or any(term in str(species).lower() for term in ["sp.", "cf.", "undetermined", "unknown"]):
                return "Skipped - generic name"
            try:
                response = requests.get(GBIF_API + requests.utils.quote(species), timeout=10)
                data = response.json()
                df.at[row.name, "species_validation_status"] = data.get("matchType", "Unknown")
                if data.get("matchType") == "EXACT" and data.get("confidence", 0) >= 90:
                    updated_row, note = compare_and_correct(row, data)
                    return note
                else:
                    return "No confident match"
            except:
                df.at[row.name, "species_validation_status"] = "GBIF error"
                return "GBIF lookup error"
        if st.button("🚀 Run GBIF API"):
            st.info("⏳ Processing... please wait")
            progress_bar = st.progress(0)
            total = len(df)
            for i, idx in enumerate(df.index):
                row = df.loc[idx]
                df.at[idx, "review_fields"] = identify_missing_fields(row)
                df.at[idx, "suspicious_fields"] = identify_suspicious_fields(row)
                df.at[idx, "taxonomy_hierarchy_issues"] = validate_taxonomic_hierarchy(row)
                df.at[idx, "correction_note"] = auto_correct_row(row)
                progress_bar.progress((i + 1) / total)
                time.sleep(0.01)
            progress_bar.empty()
            def summarize_issues(row):
                issues = []
                if row.get("review_fields"):
                    issues.append(f"Missing: {row['review_fields']}")
                if row.get("suspicious_fields"):
                    issues.append(f"Suspicious: {row['suspicious_fields']}")
                if row.get("taxonomy_hierarchy_issues"):
                    issues.append(f"Taxonomy: {row['taxonomy_hierarchy_issues']}")
                return " | ".join(issues)
            df["row_issue_summary"] = df.apply(summarize_issues, axis=1)
            df["needs_review"] = df["row_issue_summary"].apply(lambda x: bool(x))
            # Move correction_note column to the end
            if "correction_note" in df.columns:
                correction_col = df.pop("correction_note")
                df["correction_note"] = correction_col
            st.success("✅ Correction + Summary complete!")
            st.dataframe(df[["Species", "ORDER", "FAMILY", "GENUS", "correction_note", "row_issue_summary"]].head(10))
            to_download = io.BytesIO()
            df.to_excel(to_download, index=False, engine='openpyxl')
            to_download.seek(0)
            st.download_button(
                label="📅 Download Final Cleaned Excel",
                data=to_download,
                file_name="Mammal Inventory - Final Reviewed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
