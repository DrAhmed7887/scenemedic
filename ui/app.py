"""Streamlit demo UI — upload script, view Realism Report."""
import streamlit as st

st.set_page_config(page_title="SceneMedic", layout="wide")
st.title("SceneMedic — Clinical Realism Audit")
st.caption("Physician-built multi-agent technical advisor for medical film & TV.")

uploaded = st.file_uploader("Upload script (PDF)", type=["pdf"])
if uploaded:
    st.info("Wire this to the deployed Agent Engine endpoint.")
    st.write("File:", uploaded.name)
