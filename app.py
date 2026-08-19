import streamlit as st
import pandas as pd
import io
import zipfile
import os
import math
from datetime import datetime
import openpyxl

# -----------------------------
# Streamlit Page Settings
# -----------------------------
st.set_page_config(
    page_title="File Splitter",
    page_icon="✂️",
    layout="centered"
)

st.title("✂️ Large File Splitter")
st.write(
    "Upload a CSV or Excel file. "
    "The file will be split into multiple files with a maximum of 5,000 rows each."
)

# -----------------------------
# Settings
# -----------------------------
ROWS_PER_FILE = 5000
FILE_DATE = datetime.now().strftime("%Y%m%d")

# -----------------------------
# Upload File
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload your file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    file_name = uploaded_file.name
    file_extension = os.path.splitext(file_name)[1].lower()
    base_name = os.path.splitext(file_name)[0]

    try:

        # -----------------------------
        # Read File
        # -----------------------------
        if file_extension == ".csv":
            df = pd.read_csv(uploaded_file)

        elif file_extension == ".xlsx":
            df = pd.read_excel(uploaded_file)

        else:
            st.error("Only CSV and XLSX files are supported.")
            st.stop()

        total_rows = len(df)
        total_files = math.ceil(total_rows / ROWS_PER_FILE)

        # -----------------------------
        # File Information
        # -----------------------------
        st.success("File loaded successfully!")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rows", f"{total_rows:,}")
        col2.metric("Rows per File", f"{ROWS_PER_FILE:,}")
        col3.metric("Number of Output Files", total_files)

        # -----------------------------
        # Data Preview
        # -----------------------------
        with st.expander("Preview First 10 Rows"):
            st.dataframe(
                df.head(10),
                use_container_width=True
            )

        # -----------------------------
        # Split Button
        # -----------------------------
        if st.button(
            "Split File",
            type="primary",
            use_container_width=True
        ):

            if total_rows == 0:
                st.warning("The uploaded file contains no data.")
                st.stop()

            zip_buffer = io.BytesIO()

            progress_bar = st.progress(0)
            status_text = st.empty()

            # -----------------------------
            # Create ZIP File
            # -----------------------------
            with zipfile.ZipFile(
                zip_buffer,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zip_file:

                for i in range(total_files):

                    start_row = i * ROWS_PER_FILE
                    end_row = start_row + ROWS_PER_FILE

                    chunk = df.iloc[start_row:end_row]

                    part_number = i + 1

                    # -----------------------------
                    # CSV Output
                    # -----------------------------
                    if file_extension == ".csv":

                        output_buffer = io.StringIO()

                        chunk.to_csv(
                            output_buffer,
                            index=False
                        )

                        output_filename = (
                            f"{FILE_DATE}_{base_name}_part_{part_number}.csv"
                        )

                        zip_file.writestr(
                            output_filename,
                            output_buffer.getvalue().encode("utf-8-sig")
                        )

                    # -----------------------------
                    # Excel Output
                    # -----------------------------
                    elif file_extension == ".xlsx":

                        output_buffer = io.BytesIO()

                        with pd.ExcelWriter(
                            output_buffer,
                            engine="openpyxl"
                        ) as writer:

                            chunk.to_excel(
                                writer,
                                index=False,
                                sheet_name="Data"
                            )

                        output_filename = (
                            f"{FILE_DATE}_{base_name}_part_{part_number}.xlsx"
                        )

                        zip_file.writestr(
                            output_filename,
                            output_buffer.getvalue()
                        )

                    # -----------------------------
                    # Update Progress
                    # -----------------------------
                    progress = int(
                        ((i + 1) / total_files) * 100
                    )

                    progress_bar.progress(progress)

                    status_text.write(
                        f"Creating file {i + 1} of {total_files}..."
                    )

            # -----------------------------
            # Complete
            # -----------------------------
            zip_buffer.seek(0)

            st.success(
                f"Done! {total_files} files have been created."
            )

            st.download_button(
                label="📦 Download All Split Files as ZIP",
                data=zip_buffer,
                file_name=f"{FILE_DATE} {base_name}_split_files.zip",
                mime="application/zip",
                use_container_width=True
            )

    except Exception as e:

        st.error("An error occurred while processing the file:")
        st.exception(e)
