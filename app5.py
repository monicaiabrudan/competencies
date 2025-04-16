import streamlit as st
import pandas as pd
import re

# Load CSV file
@st.cache_data
def load_data():
    df = pd.read_csv("/Users/ma14/Documents/2024 WCS/Competencies/Pathogen Genomics Competencies and KSA Database 22Feb25.csv")
    return df

df = load_data()

# Define Bloom's taxonomy levels + N/A option
bloom_levels = ["Remember", "Understand", "Apply", "Analyse", "Evaluate", "Create"]

# Filter out rows with actual content (not domain titles)
df = df[df["(Revised) Domains and Topics"].notna()].reset_index(drop=True)

st.title("Pathogen Genomics Competency Self-Assessment")
st.write("Select your level of competency for each item below:")

# Store user selections
selections = {}

for i, row in df.iterrows():
    topic = row["(Revised) Domains and Topics"]

    # Skip Bloom's levels for rows that are headers (e.g., start with number and period)
    if re.match(r"^\d+\.\s", topic):
        st.markdown(f"## {topic}")
        continue

    # Include all Bloom levels, using 'n/A' if missing
    available_levels = {level: row[level] if pd.notna(row[level]) else "n/A" for level in bloom_levels}

    # Always add an explicit "N/A" option
    available_levels["N/A"] = "Not applicable"

    st.markdown(f"### {topic}")

    options_with_text = [f"{level}: {text}" for level, text in available_levels.items()]

    selected = st.radio(
        f"Select your level for: {topic}",
        options_with_text,
        key=f"radio_{i}"
    )

    selected_level = selected.split(":")[0]  # Extract level name only
    selected_text = available_levels[selected_level]
    selections[topic] = (selected_level, selected_text)

# Show summary and download option
if st.button("Show Summary"):
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
