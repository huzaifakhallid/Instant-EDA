import streamlit as st
import pandas as pd
from core.report import generate_html_report
from core.analyzer import (
    profile_data, 
    analyze_columns, 
    create_histogram, 
    create_barplot,
    create_correlation_heatmap,
    get_health_report,
    detect_outliers,
    create_bivariate_categorical_plot,
    create_numerical_vs_categorical_plot,
    get_ml_suggestions
)

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="InstantEDA",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. App Title and Description ---
main_col1, main_col2 = st.columns([2, 1]) 
with main_col1:
    st.title("Instant EDA 👾")
    st.markdown("""
        Welcome to InstantEDA! This advanced tool automates Exploratory Data Analysis. 
        Just upload your CSV file below to generate a detailed interactive report.
    """)

# --- 3. File Uploader ---
uploaded_file = st.file_uploader(
    "Upload a CSV file to begin analysis.",
    type=["csv"],
    label_visibility="collapsed" 
)

def smart_datetime_converter(df: pd.DataFrame) -> pd.DataFrame:
    """Intelligently convert object columns to datetime if they look like dates."""
    for col in df.select_dtypes(include=['object']).columns:
        # Take a sample of up to 50 non-null values
        sample = df[col].dropna().sample(n=min(50, len(df[col].dropna())))
        
        # If the sample is empty, skip
        if sample.empty:
            continue
            
        # Try converting the sample
        try:
            converted_sample = pd.to_datetime(sample, errors='raise')
            # If a high percentage of the sample are dates, convert the whole column
            if (converted_sample.notna().sum() / len(sample)) > 0.8:
                # Use errors='coerce' on the full column in case of a few bad entries
                df[col] = pd.to_datetime(df[col], errors='coerce')
        except (ValueError, TypeError):
            # If the sample conversion fails, it's definitely not a datetime column
            continue
    return df

# --- 4. Main Application Logic ---
if uploaded_file is not None:
    try:
        # --- Data Loading and Preprocessing ---
        df = pd.read_csv(uploaded_file)
        df = smart_datetime_converter(df)


        st.success("File processed successfully!")
        
        # --- Pre-compute all tabular/text analyses ---
        profile = profile_data(df)
        column_summary = analyze_columns(df)
        health_report = get_health_report(df)
        outlier_report = detect_outliers(df)
        ml_suggestions = get_ml_suggestions(df)
        
        # --- Pre-generate all plots ---
        with st.spinner("Generating all visualizations..."):
            correlation_fig = create_correlation_heatmap(df)
            univariate_figs = {}
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    univariate_figs[col] = create_histogram(df, col)
                else:
                    univariate_figs[col] = create_barplot(df, col)

        # Get column lists for UI selectors
        categorical_cols = df.select_dtypes(include=['object', 'category', 'datetime64[ns]']).columns.tolist()
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # --- 5. Download Button ---
        with main_col2:
            st.write("###  ") 
            st.write("### Download Report")
            
            # Generate the HTML report 
            report_html = generate_html_report(
                profile,
                column_summary,
                health_report,
                outlier_report,
                univariate_figs,
                correlation_fig,
                ml_suggestions
            )
            st.download_button(
                label="📥 Download Full HTML Report",
                data=report_html,
                file_name="InstantEDA_Full_Report.html",
                mime="text/html"
            )

        # --- 6. Tabbed Interface ---
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Overview", "📈 Variable Analysis", "🤖 ML Suggestions", "⚠️ Alerts & Outliers"])
        
        with tab1:
            st.header("Data Preview")
            st.dataframe(df.head())
            st.markdown("---")
            st.header("Data Profile")
            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            p_col1.metric("Number of Rows", profile["Number of Rows"])
            p_col2.metric("Number of Columns", profile["Number of Columns"])
            p_col3.metric("Missing Cells", profile["Total Missing Cells"])
            p_col4.metric("Duplicate Rows", profile["Total Duplicate Rows"])
            st.markdown("---")
            st.header("Column-wise Analysis")
            st.dataframe(column_summary)

        with tab2:
            st.header("Univariate Analysis")
            selected_col_uni = st.selectbox("Select a column:", df.columns, key="univariate")
            if selected_col_uni:
                st.plotly_chart(univariate_figs[selected_col_uni], use_container_width=True)
            st.markdown("---")
            
            st.header("Bivariate Analysis")
            bivariate_type = st.radio("Choose analysis type:", ("Numerical vs Numerical", "Numerical vs Categorical", "Categorical vs Categorical"), horizontal=True, key="biv_radio")
            if bivariate_type == "Numerical vs Numerical":
                st.subheader("Correlation Heatmap")
                st.plotly_chart(correlation_fig, use_container_width=True)
            elif bivariate_type == "Numerical vs Categorical":
                c1, c2 = st.columns(2)
                num_col = c1.selectbox("Select a numerical column:", numerical_cols, key="biv_num")
                cat_col = c2.selectbox("Select a categorical column:", categorical_cols, key="biv_cat_num")
                if num_col and cat_col:
                    fig = create_numerical_vs_categorical_plot(df, num_col, cat_col)
                    st.plotly_chart(fig, use_container_width=True)
            elif bivariate_type == "Categorical vs Categorical":
                c1, c2 = st.columns(2)
                cat_col1 = c1.selectbox("Select first categorical column:", categorical_cols, key="biv_cat1")
                cat_col2 = c2.selectbox("Select second categorical column:", categorical_cols, key="biv_cat2", index=min(1, len(categorical_cols)-1))
                if cat_col1 and cat_col2:
                    if cat_col1 == cat_col2: st.warning("Please select two different columns.")
                    else:
                        fig = create_bivariate_categorical_plot(df, cat_col1, cat_col2)
                        st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.header("Machine Learning Preprocessing Suggestions")
            st.info("These are heuristic-based suggestions. Always validate with domain knowledge.")
            for col_name, details in ml_suggestions.items():
                with st.expander(f"**{col_name}** (Identified as: *{details.get('role', 'Unknown')}*)"):
                    st.markdown(f"**Suggestion:** {details.get('suggestion', 'N/A')}")
                    st.markdown("**Example Code:**")
                    st.code(details.get('code', '# N/A'), language='python')
        
        with tab4:
            st.header("Data Health Report")
            if not any(v for k, v in health_report.items() if v): st.success("No major data health issues detected.")
            else:
                if health_report.get("high_missing_values"): st.warning(f"**High Missing Values (>50%):** {', '.join([f'{col} ({pct})' for col, pct in health_report['high_missing_values']])}")
                if health_report.get("constant_columns"): st.warning(f"**Constant Columns:** {', '.join(health_report['constant_columns'])}")
                if health_report.get("high_cardinality_columns"): st.info(f"**High Cardinality (Potential IDs):** {', '.join(health_report['high_cardinality_columns'])}")
            st.markdown("---")
            st.header("Outlier Report (IQR Method)")
            if not outlier_report: st.success("No significant outliers were detected.")
            else:
                for col_name, details in outlier_report.items():
                    with st.expander(f"**{col_name}** - Found {details['count']} outliers ({details['percentage']})"):
                        st.write(f"Sample Outlier Values: `{details['sample_values']}`")
                        st.write("These values fall outside the 1.5 * IQR range and may warrant investigation.")
                        
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        st.exception(e)

else:
    st.info(" Upload a CSV file to see the magic happen!")