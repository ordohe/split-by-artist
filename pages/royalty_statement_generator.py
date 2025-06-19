import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="royalty statement generator")

st.title("📄 royalty statement generator")
st.write("🚨this feature is still being worked on")

uploaded_file = st.file_uploader("Upload file", type=["xlsx", "xls", "csv"])

def detect_header_row(file, file_type):
    if file_type == "excel":
        preview = pd.read_excel(file, header=None, nrows=15)
    else:
        preview = pd.read_csv(file, header=None, nrows=15)
    for i, row in preview.iterrows():
        if any(isinstance(cell, str) and "title" in cell.lower() for cell in row):
            return i
    return None

def load_data(file, header_row_idx, file_type):
    if file_type == "excel":
        return pd.read_excel(file, header=header_row_idx)
    else:
        return pd.read_csv(file, header=header_row_idx)

if uploaded_file:
    file_type = "csv" if uploaded_file.name.endswith(".csv") else "excel"
    header_row_idx = detect_header_row(uploaded_file, file_type)

    if header_row_idx is None:
        st.error("❌ Could not detect header row with 'Title'. Please check your file.")
    else:
        df = load_data(uploaded_file, header_row_idx, file_type)
        st.success(f"✅ Header detected at row {header_row_idx + 1}")
        st.dataframe(df.head())

        # Try to find key columns
        title_col = next((col for col in df.columns if "title" in str(col).lower()), None)
        customer_col = next((col for col in df.columns if "customer" in str(col).lower()), None)
        extended_col = next((col for col in df.columns if "extended" in str(col).lower()), None)

        if not all([title_col, customer_col, extended_col]):
            st.error("❌ Could not find necessary columns ('Title', 'Customer Name', 'Extended').")
        else:
            summary = df.groupby([title_col, customer_col])[extended_col].sum().reset_index()
            summary.rename(columns={title_col: "Title", customer_col: "Customer", extended_col: "Total USD"}, inplace=True)
            st.subheader("📊 Royalty Summary")
            st.dataframe(summary)

            # Downloadable Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                summary.to_excel(writer, index=False, sheet_name="Royalty Statement")
            output.seek(0)
            st.download_button("📥 Download Royalty Statement", data=output, file_name="royalty_statement.xlsx")
