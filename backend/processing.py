import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-GUI backend for servers
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import numpy as np

# Set style for better-looking charts
plt.style.use('default')
sns.set_palette("husl")

# =========================
# Main Processing Function
# =========================
def process_data(df, cleaning_options):
    """
    Cleans, analyses, and generates dashboard visuals from a DataFrame.
    Args:
        df (pd.DataFrame): Uploaded dataset
        cleaning_options (dict): Cleaning steps chosen by user
    Returns:
        dict: KPIs, charts (as base64 images), and processed data preview
    """

    # 0️⃣ Basic validation
    if not isinstance(df, pd.DataFrame):
        raise ValueError("process_data expects a pandas DataFrame")
    
    if df.empty:
        raise ValueError("Dataset is empty")

    # 1️⃣ Apply Cleaning
    df = apply_cleaning(df, cleaning_options)

    # 2️⃣ Problem detection & scoring (COMPLETE LOGIC)
    df = detect_problems_and_score(df)

    # 3️⃣ KPIs
    kpis = calculate_kpis(df)

    # 3.b️⃣ Top critical machines
    top_critical = get_top_critical_machines(df, cleaning_options)

    # 4️⃣ Generate Charts
    charts = generate_charts(df)

    # 5️⃣ Return all results
    return {
        "kpis": kpis,
        "charts": charts,
        "data_preview": df.head(20).to_dict(orient="records"),
        "top_critical": top_critical,
        "total_rows": len(df),
        "columns_available": list(df.columns)
    }


# =========================
# Cleaning Logic
# =========================
def apply_cleaning(df, opts):
    """Apply data cleaning based on user options"""
    df_cleaned = df.copy()
    
    if opts.get("drop_na"):
        df_cleaned.dropna(inplace=True)
    
    if opts.get("fill_na") == "mean":
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
    elif opts.get("fill_na") == "median":
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
    elif opts.get("fill_na") == "mode":
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                mode_val = df_cleaned[col].mode()
                if not mode_val.empty:
                    df_cleaned[col].fillna(mode_val.iloc[0], inplace=True)
    
    if opts.get("remove_duplicates"):
        df_cleaned.drop_duplicates(inplace=True)
    
    return df_cleaned


# =========================
# COMPLETE Problem Detection + Scoring (Your Original Logic)
# =========================
def detect_problems_and_score(df):
    """Detect problems and calculate critical scores using COMPLETE logic"""
    df_scored = df.copy()
    
    # Find potential column names for different metrics
    cpu_cols = find_usage_columns(df_scored, ['cpu', 'processor', 'processor usage'])
    ram_cols = find_usage_columns(df_scored, ['ram', 'memory', 'memory usage'])
    disk_cols = find_usage_columns(df_scored, ['disk', 'storage', 'disk usage', 'storage usage'])
    network_cols = find_usage_columns(df_scored, ['network', 'network status'])
    patch_cols = find_usage_columns(df_scored, ['missingpatchs', 'missingpatchskb', 'patch'])
    severity_cols = find_usage_columns(df_scored, ['severity', 'risk level'])
    cve_cols = find_usage_columns(df_scored, ['cve', 'cve identifier'])
    
    # Use found columns or create defaults
    cpu_col = cpu_cols[0] if cpu_cols else "CPU Usage (%)"
    ram_col = ram_cols[0] if ram_cols else "RAM Usage (%)"
    disk_col = disk_cols[0] if disk_cols else "Disk Usage (%)"
    network_col = network_cols[0] if network_cols else "Network Status"
    patch_col = patch_cols[0] if patch_cols else "MissingPatchsKB"
    severity_col = severity_cols[0] if severity_cols else "Severity"
    cve_col = cve_cols[0] if cve_cols else "CVE identifier(s)"
    
    # Create columns if they don't exist (for testing)
    if cpu_col not in df_scored.columns:
        df_scored[cpu_col] = np.random.randint(20, 95, len(df_scored))
    if ram_col not in df_scored.columns:
        df_scored[ram_col] = np.random.randint(30, 98, len(df_scored))
    if disk_col not in df_scored.columns:
        df_scored[disk_col] = np.random.randint(40, 99, len(df_scored))
    if network_col not in df_scored.columns:
        df_scored[network_col] = np.random.choice(['Online', 'Offline', 'Unstable'], len(df_scored))
    if patch_col not in df_scored.columns:
        df_scored[patch_col] = np.random.choice(['Release Notes', '5002768', '5002754'], len(df_scored))
    if severity_col not in df_scored.columns:
        df_scored[severity_col] = np.random.choice(['Critical', 'Important', 'Moderate', 'Low'], len(df_scored))
    
    # Ensure we have a Computer ID column
    if 'Computer ID' not in df_scored.columns:
        if 'ID' in df_scored.columns:
            df_scored['Computer ID'] = df_scored['ID']
        elif 'Computer' in df_scored.columns:
            df_scored['Computer ID'] = df_scored['Computer']
        else:
            df_scored['Computer ID'] = [f"PC_{i+1:03d}" for i in range(len(df_scored))]
    
    # Coerce numeric columns and handle errors
    for col in [cpu_col, ram_col, disk_col]:
        df_scored[col] = pd.to_numeric(df_scored[col], errors="coerce")
        col_vals = df_scored[col].replace([np.inf, -np.inf], np.nan)
        fill_value = col_vals.median()
        if pd.isna(fill_value):
            fill_value = 0
        df_scored[col] = col_vals.fillna(fill_value)
    
    # ========================================
    # COMPLETE PROBLEM DETECTION (Your Logic)
    # ========================================
    
    # 1. Hardware Issues
    df_scored["High_CPU"] = df_scored[cpu_col] > 85
    df_scored["High_RAM"] = df_scored[ram_col] > 80
    df_scored["High_Disk"] = df_scored[disk_col] > 90
    
    # 2. Network Issues
    df_scored["Network_Offline"] = df_scored[network_col].str.lower().isin(['offline', 'disconnected'])
    df_scored["Network_Unstable"] = df_scored[network_col].str.lower().isin(['unstable', 'poor'])
    
    # 3. Security Patch Issues
    df_scored["Missing_Patch"] = (
        (df_scored[patch_col].notna()) & 
        (df_scored[patch_col].str.lower() != 'release notes') &
        (df_scored[patch_col].str.lower() != 'unknown')
    )
    
    # 4. Security Vulnerability Issues
    df_scored["Critical_Vulnerability"] = df_scored[severity_col].str.lower().str.contains('critical')
    df_scored["Important_Vulnerability"] = df_scored[severity_col].str.lower().str.contains('important')
    df_scored["Moderate_Vulnerability"] = df_scored[severity_col].str.lower().str.contains('moderate')
    df_scored["Low_Vulnerability"] = df_scored[severity_col].str.lower().str.contains('low')
    
    # 5. CVE Issues
    df_scored["Has_CVE"] = (
        (df_scored[cve_col].notna()) & 
        (df_scored[cve_col].str.lower() != 'unknown') &
        (df_scored[cve_col].str.contains('CVE-'))
    )
    
    # ========================================
    # COMPLETE CRITICAL SCORING (Your Logic)
    # ========================================
    
    # Initialize scores
    df_scored["Critical_Score"] = 0
    
    # Hardware scoring
    df_scored.loc[df_scored["High_CPU"], "Critical_Score"] += 2
    df_scored.loc[df_scored["High_RAM"], "Critical_Score"] += 1.5
    df_scored.loc[df_scored["High_Disk"], "Critical_Score"] += 2
    
    # Network scoring
    df_scored.loc[df_scored["Network_Offline"], "Critical_Score"] += 3
    df_scored.loc[df_scored["Network_Unstable"], "Critical_Score"] += 2
    
    # Security patch scoring
    df_scored.loc[df_scored["Missing_Patch"], "Critical_Score"] += 2
    
    # Vulnerability scoring
    df_scored.loc[df_scored["Critical_Vulnerability"], "Critical_Score"] += 3
    df_scored.loc[df_scored["Important_Vulnerability"], "Critical_Score"] += 2
    df_scored.loc[df_scored["Moderate_Vulnerability"], "Critical_Score"] += 1
    df_scored.loc[df_scored["Low_Vulnerability"], "Critical_Score"] += 0.5
    
    # CVE scoring
    df_scored.loc[df_scored["Has_CVE"], "Critical_Score"] += 1
    
    # ========================================
    # SEVERITY CLASSIFICATION (Your Logic)
    # ========================================
    
    # Define severity levels based on your original logic
    df_scored["Severity_Level"] = pd.cut(
        df_scored["Critical_Score"],
        bins=[-1, 3, 5, 7, 100],
        labels=["Low", "Medium", "High", "Critical"]
    )
    
    # ========================================
    # PROBLEMS SUMMARY
    # ========================================
    
    # Create detailed problems list
    problems_list = []
    for _, row in df_scored.iterrows():
        issues = []
        
        if row["High_CPU"]:
            issues.append("High CPU usage")
        if row["High_RAM"]:
            issues.append("High RAM usage")
        if row["High_Disk"]:
            issues.append("Disk almost full")
        if row["Network_Offline"]:
            issues.append("Network disconnected")
        if row["Network_Unstable"]:
            issues.append("Network unstable")
        if row["Missing_Patch"]:
            issues.append("Missing security patch")
        if row["Critical_Vulnerability"]:
            issues.append("Critical vulnerability")
        if row["Important_Vulnerability"]:
            issues.append("Important vulnerability")
        if row["Moderate_Vulnerability"]:
            issues.append("Moderate vulnerability")
        if row["Has_CVE"]:
            issues.append("CVE identified")
        
        problems_list.append("; ".join(issues) if issues else "No issues detected")
    
    df_scored["Problems"] = problems_list
    
    # Count total problems per machine
    df_scored["Total_Problems"] = (
        df_scored["High_CPU"].astype(int) +
        df_scored["High_RAM"].astype(int) +
        df_scored["High_Disk"].astype(int) +
        df_scored["Network_Offline"].astype(int) +
        df_scored["Network_Unstable"].astype(int) +
        df_scored["Missing_Patch"].astype(int) +
        df_scored["Critical_Vulnerability"].astype(int) +
        df_scored["Important_Vulnerability"].astype(int) +
        df_scored["Moderate_Vulnerability"].astype(int) +
        df_scored["Has_CVE"].astype(int)
    )
    
    # Store column names for later use
    df_scored.attrs['cpu_col'] = cpu_col
    df_scored.attrs['ram_col'] = ram_col
    df_scored.attrs['disk_col'] = disk_col
    df_scored.attrs['network_col'] = network_col
    df_scored.attrs['patch_col'] = patch_col
    df_scored.attrs['severity_col'] = severity_col
    df_scored.attrs['cve_col'] = cve_col
    
    return df_scored


def find_usage_columns(df, keywords):
    """Find columns that match usage keywords"""
    found_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in keywords):
            found_cols.append(col)
    return found_cols


# =========================
# Enhanced KPI Calculation
# =========================
def calculate_kpis(df):
    """Calculate comprehensive key performance indicators"""
    kpis = {}
    
    try:
        kpis["total_machines"] = len(df)
        
        # Severity distribution
        kpis["critical_pct"] = round((df['Severity_Level'] == "Critical").mean() * 100, 1)
        kpis["high_pct"] = round((df['Severity_Level'] == "High").mean() * 100, 1)
        kpis["medium_pct"] = round((df['Severity_Level'] == "Medium").mean() * 100, 1)
        kpis["low_pct"] = round((df['Severity_Level'] == "Low").mean() * 100, 1)
        
        # Hardware metrics
        cpu_col = df.attrs.get('cpu_col', 'CPU Usage (%)')
        ram_col = df.attrs.get('ram_col', 'RAM Usage (%)')
        disk_col = df.attrs.get('disk_col', 'Disk Usage (%)')
        
        kpis["avg_cpu"] = round(df[cpu_col].mean(), 1)
        kpis["avg_ram"] = round(df[ram_col].mean(), 1)
        kpis["avg_disk"] = round(df[disk_col].mean(), 1)
        kpis["max_cpu"] = round(df[cpu_col].max(), 1)
        kpis["max_ram"] = round(df[ram_col].max(), 1)
        kpis["max_disk"] = round(df[disk_col].max(), 1)
        
        # Problem counts
        kpis["machines_with_problems"] = int(df["Total_Problems"].sum())
        kpis["avg_problems_per_machine"] = round(df["Total_Problems"].mean(), 1)
        
        # Security metrics
        kpis["machines_missing_patches"] = int(df["Missing_Patch"].sum())
        kpis["critical_vulnerabilities"] = int(df["Critical_Vulnerability"].sum())
        kpis["important_vulnerabilities"] = int(df["Important_Vulnerability"].sum())
        kpis["machines_with_cve"] = int(df["Has_CVE"].sum())
        
        # Network metrics
        kpis["offline_machines"] = int(df["Network_Offline"].sum())
        kpis["unstable_connections"] = int(df["Network_Unstable"].sum())
        
        # Critical score metrics
        kpis["avg_critical_score"] = round(df["Critical_Score"].mean(), 1)
        kpis["max_critical_score"] = round(df["Critical_Score"].max(), 1)
        
    except Exception as e:
        # Fallback KPIs if something goes wrong
        kpis["total_machines"] = len(df)
        kpis["error"] = f"KPI calculation error: {str(e)}"
    
    return kpis


def get_top_critical_machines(df, cleaning_options):
    """Get top critical machines for display"""
    try:
        top_n = int(cleaning_options.get("top_n", 5))
        
        # Get column names from attrs
        cpu_col = df.attrs.get('cpu_col', 'CPU Usage (%)')
        ram_col = df.attrs.get('ram_col', 'RAM Usage (%)')
        disk_col = df.attrs.get('disk_col', 'Disk Usage (%)')
        network_col = df.attrs.get('network_col', 'Network Status')
        patch_col = df.attrs.get('patch_col', 'MissingPatchsKB')
        severity_col = df.attrs.get('severity_col', 'Severity')
        cve_col = df.attrs.get('cve_col', 'CVE identifier(s)')
        
        # Select and sort by critical score
        display_cols = [
            'Computer ID', 'Critical_Score', 'Severity_Level', 'Total_Problems',
            'Problems', cpu_col, ram_col, disk_col, network_col, patch_col, 
            severity_col, cve_col
        ]
        
        # Filter to only include columns that exist
        available_cols = [col for col in display_cols if col in df.columns]
        
        top_critical = (
            df[available_cols]
            .sort_values("Critical_Score", ascending=False)
            .head(top_n)
            .to_dict(orient="records")
        )
        
        return top_critical
        
    except Exception as e:
        return [{"error": f"Failed to get critical machines: {str(e)}"}]


# =========================
# Enhanced Chart Generation
# =========================
def generate_charts(df):
    """Generate comprehensive dashboard charts"""
    charts = {}
    
    try:
        # Set figure size and style
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        # 1. Severity Level Distribution (Pie Chart with fixed colors)
        if 'Severity_Level' in df.columns:
            fig, ax = plt.subplots(figsize=(8, 8))
            sev_counts = df["Severity_Level"].value_counts(dropna=False)
            if not sev_counts.empty:
                # Map severity levels to consistent colors
                severity_colors = {
                    "Low": "#2ecc71",       # Green
                    "Medium": "#f39c12",    # Yellow
                    "High": "#e67e22",      # Orange
                    "Critical": "#e74c3c"   # Red
                }
                # Apply mapping, default to grey if unknown
                colors = [severity_colors.get(level, "grey") for level in sev_counts.index]

                wedges, texts, autotexts = ax.pie(
                    sev_counts.values,
                    labels=sev_counts.index,
                    autopct='%1.1f%%',
                    startangle=140,
                    colors=colors,
                    textprops={'fontsize': 12, 'fontweight': 'bold'}
                )
                ax.set_title("Machine Severity Distribution", fontsize=16, fontweight='bold', pad=20)
                plt.tight_layout()
                charts["severity_distribution"] = fig_to_base64(fig)


        # 2. Critical Score Distribution
        if 'Critical_Score' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.hist(df['Critical_Score'], bins=20, color='#9b59b6', alpha=0.7, edgecolor='black')
            ax.set_title("Critical Score Distribution", fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel("Critical Score", fontweight='bold')
            ax.set_ylabel("Number of Machines", fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Add vertical lines for thresholds
            ax.axvline(x=3, color='#2ecc71', linestyle='--', linewidth=2, label='Low Threshold')
            ax.axvline(x=5, color='#f39c12', linestyle='--', linewidth=2, label='Medium Threshold')
            ax.axvline(x=7, color='#e74c3c', linestyle='--', linewidth=2, label='High Threshold')
            ax.legend()
            
            plt.tight_layout()
            charts["critical_score_distribution"] = fig_to_base64(fig)

        # 3. Problem Types Analysis
        if 'Total_Problems' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Count different problem types
            problem_types = {
                'High CPU': df['High_CPU'].sum() if 'High_CPU' in df.columns else 0,
                'High RAM': df['High_RAM'].sum() if 'High_RAM' in df.columns else 0,
                'High Disk': df['High_Disk'].sum() if 'High_Disk' in df.columns else 0,
                'Network Issues': (df['Network_Offline'].sum() + df['Network_Unstable'].sum()) if 'Network_Offline' in df.columns else 0,
                'Missing Patches': df['Missing_Patch'].sum() if 'Missing_Patch' in df.columns else 0,
                'Critical Vulns': df['Critical_Vulnerability'].sum() if 'Critical_Vulnerability' in df.columns else 0,
                'Important Vulns': df['Important_Vulnerability'].sum() if 'Important_Vulnerability' in df.columns else 0,
                'CVE Issues': df['Has_CVE'].sum() if 'Has_CVE' in df.columns else 0
            }
            
            # Filter out zero values
            problem_types = {k: v for k, v in problem_types.items() if v > 0}
            
            if problem_types:
                colors = plt.cm.Set3(np.linspace(0, 1, len(problem_types)))
                bars = ax.bar(problem_types.keys(), problem_types.values(), color=colors)
                ax.set_title("Problem Types Distribution", fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel("Problem Type", fontweight='bold')
                ax.set_ylabel("Number of Machines Affected", fontweight='bold')
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                charts["problem_types_analysis"] = fig_to_base64(fig)

        # 4. Resource Usage Comparison
        cpu_col = df.attrs.get('cpu_col', 'CPU Usage (%)')
        ram_col = df.attrs.get('ram_col', 'RAM Usage (%)')
        disk_col = df.attrs.get('disk_col', 'Disk Usage (%)')
        
        if all(col in df.columns for col in [cpu_col, ram_col, disk_col]):
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create box plot for all three resources
            data_to_plot = [df[cpu_col], df[ram_col], df[disk_col]]
            labels = ['CPU Usage (%)', 'RAM Usage (%)', 'Disk Usage (%)']
            colors = ['#3498db', '#2ecc71', '#e74c3c']
            
            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_title("Resource Usage Comparison", fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel("Usage Percentage (%)", fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            charts["resource_comparison"] = fig_to_base64(fig)

        # 5. Security Vulnerability Analysis
        if 'Critical_Vulnerability' in df.columns or 'Important_Vulnerability' in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            vuln_counts = {}
            if 'Critical_Vulnerability' in df.columns:
                vuln_counts['Critical'] = df['Critical_Vulnerability'].sum()
            if 'Important_Vulnerability' in df.columns:
                vuln_counts['Important'] = df['Important_Vulnerability'].sum()
            if 'Moderate_Vulnerability' in df.columns:
                vuln_counts['Moderate'] = df['Moderate_Vulnerability'].sum()
            if 'Low_Vulnerability' in df.columns:
                vuln_counts['Low'] = df['Low_Vulnerability'].sum()
            
            if vuln_counts:
                colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']
                bars = ax.bar(vuln_counts.keys(), vuln_counts.values(), color=colors[:len(vuln_counts)])
                ax.set_title("Security Vulnerability Distribution", fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel("Vulnerability Level", fontweight='bold')
                ax.set_ylabel("Number of Machines", fontweight='bold')
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                charts["security_vulnerability_analysis"] = fig_to_base64(fig)

    except Exception as e:
        charts["error"] = f"Chart generation error: {str(e)}"
    
    return charts


# =========================
# Helper: Convert Matplotlib fig → base64 string
# =========================
def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    try:
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return img_base64
    except Exception as e:
        plt.close(fig)
        return None
