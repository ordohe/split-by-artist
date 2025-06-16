import streamlit as st
import pandas as pd
import io

st.title("🎶 split excel file by artist")
st.write("upload an excel file. the app will create a separate tab for each artist.")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Preview:", df.head())

        # Guess the artist column
        artist_col = None
        for col in df.columns:
            if 'artist' in col.lower():
                artist_col = col
                break

        if artist_col:
            st.success(f"Found artist column: **{artist_col}**")
            
            if st.button("Split and Download"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for name, group in df.groupby(artist_col):
                        safe_name = str(name)[:31] if pd.notnull(name) else "Unknown"
                        group.to_excel(writer, sheet_name=safe_name, index=False)
                output.seek(0)
                st.download_button("📥 Download New Excel File", data=output, file_name="Artists_Split.xlsx")
        else:
            st.error("No column containing 'Artist' was found.")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
