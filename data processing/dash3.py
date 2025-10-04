import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Streamlit Page Config ----------
st.set_page_config(page_title="Computer Health Dashboard", layout="wide")

# ---------- Load Data ----------
df = pd.read_csv("critical_updated_dataset.csv")

# ---------- Title ----------
st.title("🖥️ Computer Health & Security Dashboard")
st.markdown("---")

# ---------- Key Metrics ----------
st.markdown("### 🔍 Overview")

col1, col2 = st.columns(2)
col1.metric("💻 Total Machines", len(df))
col2.metric("🚨 Critical Machines", df[df["Severity_Level"] == "Critical"].shape[0])

st.markdown("---")

# ---------- Severity Level Pie Chart ----------
st.markdown("### 📊 Severity Level Distribution")
fig1, ax1 = plt.subplots(figsize=(4, 4))  # smaller pie chart

colors = {
    "Critical": "#ff4b4b",
    "Important": "#ffa600",
    "Moderate": "#59d985",
    "Low": "#4b9cff"
}
severity_counts = df["Severity_Level"].value_counts()
pie_colors = [colors.get(level, "#cccccc") for level in severity_counts.index]

ax1.pie(severity_counts, labels=severity_counts.index, autopct="%1.1f%%", startangle=90, colors=pie_colors)
ax1.axis('equal')
st.pyplot(fig1)

st.markdown("---")

# ---------- Top Issues Bar Chart ----------
st.markdown("### 🛠️ Top 10 Most Common Issues")
all_issues = ";".join(df['Problems'].dropna()).split(";")
issue_counts = pd.Series([i.strip() for i in all_issues]).value_counts().head(10)

fig2, ax2 = plt.subplots(figsize=(6, 4))
issue_counts.plot(kind="bar", ax=ax2, color="#4b9cff")
ax2.set_xlabel("Issue", fontweight="bold")
ax2.set_ylabel("Occurrences", fontweight="bold")
ax2.set_title("Most Frequent Issues", fontweight="bold")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig2)

st.markdown("---")

# ---------- Additional Chart: Critical Score Distribution ----------
st.markdown("### 📈 Distribution of Critical Scores")
fig3, ax3 = plt.subplots(figsize=(6, 4))
df['Critical_Score'].hist(bins=10, color="#ff4b4b", edgecolor='black', ax=ax3)
ax3.set_xlabel("Critical Score", fontweight="bold")
ax3.set_ylabel("Number of Machines", fontweight="bold")
ax3.set_title("Critical Score Distribution", fontweight="bold")
st.pyplot(fig3)

st.markdown("---")

# ---------- Top 10 Most Critical Machines ----------
st.markdown("### 🔥 Top 10 Most Critical Machines")
top_critical = df.sort_values(by="Critical_Score", ascending=False).head(10)
st.dataframe(top_critical[['Computer ID', 'Critical_Score', 'Severity_Level', 'Problems']], use_container_width=True)

st.markdown("---")

# ---------- File Upload ----------
st.markdown("### 📁 Upload a New Dataset to Analyze")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    new_df = pd.read_csv(uploaded_file)
    st.success("✅ New file uploaded.")
    st.write("You can now use the new dataset for analysis or replace the existing one.")
