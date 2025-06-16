import streamlit as st
import pandas as pd
import io

st.title("🎶 Split Excel File by Artist")
st.write("Upload an Excel file. The app will create a separate tab for each artist.")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Step 1: Read first 15 rows to detect where the actual header is
        preview = pd.read_excel(uploaded_file, header=None, nrows=15)

        header_row_idx = None
        for i, row in preview.iterrows():
            for cell in row:
                if isinstance(cell, str) and 'artist' in cell.lower():
                    header_row_idx = i
                    break
            if header_row_idx is not None:
                break

        if header_row_idx is None:
            st.error("❌ Could not find a header row containing 'Artist'. Please check the file.")
        else:
            # Step 2: Re-read the file using detected header row
            df = pd.read_excel(uploaded_file, header=header_row_idx)
            st.write(f"✅ Detected header row: {header_row_idx + 1}")
            st.write("Preview:", df.head())

            # Step 3: Guess artist column
            artist_col = None
            for col in df.columns:
                if isinstance(col, str) and 'artist' in col.lower():
                    artist_col = col
                    break

            if artist_col:
                st.success(f"Found artist column: **{artist_col}**")

                if st.button("🎵 Split and Download"):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for name, group in df.groupby(artist_col):
                            safe_name = str(name)[:31] if pd.notnull(name) else "Unknown"
                            group.to_excel(writer, sheet_name=safe_name, index=False)
                    output.seek(0)
                    st.download_button("📥 Download New Excel File", data=output, file_name="Artists_Split.xlsx")
            else:
                st.error("❌ No column containing 'Artist' was found in the detected header row.")
    except Exception as e:
        st.error(f"⚠️ Error reading Excel file: {e}")
