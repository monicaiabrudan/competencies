import streamlit as st
import pandas as pd
import re

@st.cache_data
def load_data():
    df = pd.read_csv("Pathogen Genomics Competencies and KSA Database 22Feb25.csv")
    return df

df = load_data()

bloom_levels = ["Remember", "Understand", "Apply", "Analyse", "Evaluate", "Create"]

# Reset index and drop empty rows in main column
df = df[df["(Revised) Domains and Topics"].notna()].reset_index(drop=True)

# Identify rows that are section headers
section_mask = df["(Revised) Domains and Topics"].str.match(r"^\d+\.\s")

# Parse sections with their rows
sections_list = []
current_section = None

for i, row in df.iterrows():
    topic = row["(Revised) Domains and Topics"]
    if section_mask[i]:
        # Start new section
        current_section = {"header": topic, "rows": []}
        sections_list.append(current_section)
    else:
        if current_section is not None:
            current_section["rows"].append(row)

# Sidebar: select sections
st.sidebar.header("Step 1: Select Sections")
section_headers = [sec["header"] for sec in sections_list]
selected_sections = st.sidebar.multiselect("Choose sections to assess", options=section_headers)

if not selected_sections:
    st.info("Please select at least one section from the sidebar to proceed.")
    st.stop()

# Display only selected sections with competencies
st.title("Pathogen Genomics Competency Self-Assessment")
selections = {}

for section in sections_list:
    if section["header"] not in selected_sections:
        continue

    st.header(section["header"])

    for i, row in enumerate(section["rows"]):
        topic = row["(Revised) Domains and Topics"]

        available_levels = {level: row[level] if pd.notna(row[level]) else "n/A" for level in bloom_levels}
        available_levels["N/A"] = "Not applicable"

        st.markdown(f"### {topic}")

        options_with_text = [f"{level}: {text}" for level, text in available_levels.items()]
        key = f"radio_{section['header']}_{i}_{topic[:20].replace(' ', '_')}"

        selected = st.radio(
            f"Select your level for: {topic}",
            options_with_text,
            key=key
        )

        selected_level = selected.split(":")[0]
        selected_text = available_levels[selected_level]
        selections[topic] = (selected_level, selected_text)

if st.button("Show Summary", key="show_summary_button"):
    result_df = pd.DataFrame([
        {"Competency": topic, "Selected Level": level, "Description": desc}
        for topic, (level, desc) in selections.items()
    ])
    st.dataframe(result_df)

    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Results as CSV",
        csv,
        "competency_selections.csv",
        "text/csv"
    )
