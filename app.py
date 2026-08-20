import io
from pathlib import Path

import streamlit as st
from pypdf import PdfReader, PdfWriter


st.set_page_config(
    page_title="PDF Unlocker",
    page_icon="🔓",
    layout="centered",
)

st.title("🔓 PDF Unlocker")
st.caption(
    "Unlock a password-protected PDF and download a copy with a new name."
)

st.info(
    "Privacy: this app processes the PDF in memory and does not intentionally "
    "save uploaded or converted PDFs to disk, databases, or cloud storage."
)

uploaded_file = st.file_uploader(
    "Choose a password-protected PDF",
    type=["pdf"],
    accept_multiple_files=False,
)

if uploaded_file is not None:

    original_name = Path(uploaded_file.name).stem

    st.write(f"**Selected:** `{uploaded_file.name}`")

    password = st.text_input(
        "PDF password",
        type="password",
        placeholder="Enter the PDF password",
    )

    default_name = f"{original_name}-unlocked"

    output_name = st.text_input(
        "Output filename",
        value=default_name,
        help="The .pdf extension is added automatically.",
    )

    # Prevent paths such as ../../something.pdf
    output_name = Path(output_name.strip()).name

    if not output_name:
        output_name = default_name

    if not output_name.lower().endswith(".pdf"):
        output_name += ".pdf"

    unlock = st.button(
        "🔓 Unlock PDF",
        type="primary",
        use_container_width=True,
    )

    if unlock:

        if not password:
            st.warning("Please enter the PDF password.")

        else:

            try:
                # Read the uploaded PDF directly into memory.
                # Nothing is written to disk.
                pdf_bytes = uploaded_file.getvalue()

                reader = PdfReader(io.BytesIO(pdf_bytes))

                # Decrypt the PDF if it is encrypted.
                if reader.is_encrypted:

                    decrypt_result = reader.decrypt(password)

                    if not decrypt_result:
                        st.error(
                            "❌ Incorrect password, or this PDF uses an "
                            "encryption method that could not be unlocked."
                        )
                        st.stop()

                # Create the unlocked PDF entirely in memory.
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                # Preserve document metadata when possible.
                if reader.metadata:

                    metadata = {
                        key: value
                        for key, value in reader.metadata.items()
                        if key and value is not None
                    }

                    if metadata:
                        writer.add_metadata(metadata)

                # Write output to RAM, not disk.
                output = io.BytesIO()

                writer.write(output)

                output.seek(0)

                unlocked_pdf = output.getvalue()

                st.success("✅ PDF unlocked successfully.")

                st.download_button(
                    label=f"⬇️ Download {output_name}",
                    data=unlocked_pdf,
                    file_name=output_name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )

            except ImportError as exc:

                st.error(
                    "❌ A required PDF encryption dependency is missing. "
                    "Please make sure requirements.txt contains "
                    "`pypdf[crypto]` and redeploy the app."
                )

                st.caption(f"Technical error: {type(exc).__name__}")

            except Exception as exc:

                st.error(
                    "❌ Unable to process this PDF. "
                    "It may be corrupted, unsupported, or use an "
                    "encryption method that this app cannot handle."
                )

                st.caption(f"Technical error: {type(exc).__name__}")
