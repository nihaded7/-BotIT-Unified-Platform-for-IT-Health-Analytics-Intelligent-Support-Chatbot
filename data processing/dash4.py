import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("critical_updated_dataset.csv")

st.set_page_config(layout="wide")
st.title("🛡️ Computer Health & Security Dashboard")

# ---- KPIs ----
st.markdown("## 📌 Key Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🖥️ Total Machines", len(df))

with col2:
    critical_pct = (df['Severity_Level'] == "Critical").mean() * 100
    st.metric("🔥 % Critical Machines", f"{critical_pct:.1f}%")

with col3:
    avg_cpu = df["CPU Usage (%)"].mean()
    avg_ram = df["RAM Usage (%)"].mean()
    avg_disk = df["Disk Usage (%)"].mean()
    st.metric("🧠 Avg. CPU/RAM/Disk", f"{avg_cpu:.0f}% / {avg_ram:.0f}% / {avg_disk:.0f}%")

with col4:
    top_severity = df["Severity_Level"].value_counts().idxmax()
    count = df["Severity_Level"].value_counts().max()
    st.metric("❗ Top Severity Level", f"{top_severity} ({count})")

st.markdown("---")

# ---- Charts Section ----
st.markdown("## 📊 Visual Insights")

chart_col1, chart_col2 = st.columns(2)

# Bar Chart - Severity_Level distribution
with chart_col1:
    st.subheader("Machines by Severity Level")
    severity_counts = df["Severity_Level"].value_counts()
    fig_bar, ax = plt.subplots(figsize=(5, 3.5))
    sns.barplot(x=severity_counts.index, y=severity_counts.values, ax=ax, palette="flare")
    ax.set_xlabel("Severity Level", fontweight="bold")
    ax.set_ylabel("Count", fontweight="bold")
    st.pyplot(fig_bar)

# Pie Chart - Network Status
with chart_col2:
    st.subheader("Network Status Breakdown")
    net_counts = df['Network Status'].value_counts()
    fig_pie, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.pie(net_counts, labels=net_counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Network Status", fontsize=10, fontweight="bold")
    st.pyplot(fig_pie)

st.markdown("---")

# ---- Boxplots ----
st.markdown("## 📦 Usage Distributions")

box_col1, box_col2, box_col3 = st.columns(3)

with box_col1:
    fig_cpu, ax = plt.subplots(figsize=(4, 3))
    sns.boxplot(y=df["CPU Usage (%)"], ax=ax, color="skyblue")
    ax.set_title("CPU Usage (%)", fontweight="bold")
    st.pyplot(fig_cpu)

with box_col2:
    fig_ram, ax = plt.subplots(figsize=(4, 3))
    sns.boxplot(y=df["RAM Usage (%)"], ax=ax, color="lightgreen")
    ax.set_title("RAM Usage (%)", fontweight="bold")
    st.pyplot(fig_ram)

with box_col3:
    fig_disk, ax = plt.subplots(figsize=(4, 3))
    sns.boxplot(y=df["Disk Usage (%)"], ax=ax, color="salmon")
    ax.set_title("Disk Usage (%)", fontweight="bold")
    st.pyplot(fig_disk)

st.markdown("---")

# ---- Top Machines ----
st.markdown("## 💻 Top 10 Critical Machines")
top_critical = df.sort_values(by="Critical_Score", ascending=False).head(10)
st.dataframe(top_critical[['Computer ID', 'Critical_Score', 'Severity_Level', 'Problems']])

# Clean column names
df.columns = df.columns.str.strip()

# ---- Patch Analysis ----
st.markdown("---")
st.markdown("## 🧯 Patch Analysis")

patch_col1, patch_col2 = st.columns(2)

# 🔺 Missing Patch Severity Chart
with patch_col1:
    if "Severity" in df.columns:
        st.subheader("Missing Patch Severity")
        severity_patch_counts = df["Severity"].value_counts()
        fig_patch_sev, ax_patch_sev = plt.subplots(figsize=(4, 3))
        sns.barplot(x=severity_patch_counts.index, y=severity_patch_counts.values, ax=ax_patch_sev, palette="OrRd")
        ax_patch_sev.set_xlabel("Severity", fontweight="bold")
        ax_patch_sev.set_ylabel("Count", fontweight="bold")
        ax_patch_sev.set_title("Patch Severity Count", fontsize=10, fontweight="bold")
        ax_patch_sev.tick_params(axis='x', labelrotation=45)
        st.pyplot(fig_patch_sev)
    else:
        st.warning("Column 'Severity' not found.")

# 🔹 Most Frequent Affected Microsoft Product
with patch_col2:
    if "affected microsoft product" in df.columns:
        st.subheader("Top Affected MS Products")
        product_counts = df["affected microsoft product"].value_counts().head(10)
        fig_products, ax_products = plt.subplots(figsize=(4, 3))
        sns.barplot(y=product_counts.index, x=product_counts.values, ax=ax_products, palette="Blues_r")
        ax_products.set_xlabel("Count", fontweight="bold")
        ax_products.set_ylabel("Product", fontweight="bold")
        ax_products.set_title("Top 10 Affected Products", fontsize=10, fontweight="bold")
        st.pyplot(fig_products)
    else:
        st.warning("Column 'affected microsoft product' not found.")

# ---- Advanced Section ----
with st.expander("🧪 Advanced Details"):
    # CVE Vulnerabilities
    if "CVE identifier(s)" in df.columns:
        cve_data = df[["Computer ID", "CVE identifier(s)", "Severity"]].dropna()
        if not cve_data.empty:
            st.markdown("### Vulnerabilities by CVE")
            st.dataframe(cve_data)
        else:
            st.info("✅ CVE column exists, but no vulnerabilities found.")
    else:
        st.warning("⚠️ No 'CVE' column found in the dataset.")

    # Patch Download Links
    if "Download (Link)" in df.columns:
        patch_links = df[['Computer ID', 'Download (Link)']].dropna()
        if not patch_links.empty:
            st.markdown("### 🔗 Patch Download Links")
            for _, row in patch_links.iterrows():
                st.markdown(f"- [{row['Computer ID']}]({row['Download (Link)']})")
        else:
            st.info("✅ Patch URL column exists, but no download links found.")
    else:
        st.warning("⚠️ No 'PatchDownloadURL' column found in the dataset.")

# ---- Upload Section ----
st.markdown("---")
st.markdown("## 🔄 Upload a New Dataset")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    new_df = pd.read_csv(uploaded_file)
    st.success("New file uploaded. You can integrate further analysis here.")
