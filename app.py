import streamlit as st
import pandas as pd
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

# --- Page Configuration ---
st.set_page_config(
    page_title="InstantEDA",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- App Title and Description ---
st.title("Instant EDA 👾")
st.markdown("""
    Welcome to InstantEDA! This advanced tool automates Exploratory Data Analysis. 
    Just upload your CSV file below to generate a detailed interactive report.
""")

# --- Uploader ---
uploaded_file = st.file_uploader(
    "Upload a CSV file to begin analysis.",
    type=["csv"],
    label_visibility="collapsed" 
)

# --- Main App Logic ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        # Attempt to convert object columns to datetime if possible
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except (ValueError, TypeError):
                continue # If conversion fails, just leave it as object
                
        st.success("File uploaded and processed successfully!")
        
        # --- Pre-compute all analyses ---
        health_report = get_health_report(df)
        outlier_report = detect_outliers(df)
        ml_suggestions = get_ml_suggestions(df)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # --- Organize report into TABS ---
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Overview", "📈 Variable Analysis", "🤖 ML Suggestions", "⚠️ Alerts & Outliers"])
        
        # --- TAB 1: Data Overview ---
        with tab1:
            st.header("Data Preview")
            st.dataframe(df.head())
            st.markdown("---")
            
            st.header("Data Profile")
            profile = profile_data(df)
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Number of Rows", profile["Number of Rows"])
            with col2: st.metric("Number of Columns", profile["Number of Columns"])
            with col3: st.metric("Missing Cells", profile["Total Missing Cells"])
            with col4: st.metric("Duplicate Rows", profile["Total Duplicate Rows"])
            st.markdown("---")

            st.header("Column-wise Analysis")
            column_summary_df = analyze_columns(df)
            st.dataframe(column_summary_df)

        # --- TAB 2: Variable Analysis ---
        with tab2:
            st.header("Univariate Analysis")
            selected_column_uni = st.selectbox("Select a column for univariate analysis:", df.columns, key="univariate")
            if selected_column_uni:
                if pd.api.types.is_numeric_dtype(df[selected_column_uni]):
                    fig = create_histogram(df, selected_column_uni)
                else:
                    fig = create_barplot(df, selected_column_uni)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.header("Bivariate Analysis")
            
            bivariate_type = st.radio("Choose a bivariate analysis type:", 
                                      ("Numerical vs. Numerical", "Numerical vs. Categorical", "Categorical vs. Categorical"),
                                      horizontal=True)
            
            if bivariate_type == "Numerical vs. Numerical":
                st.subheader("Correlation Heatmap")
                corr_fig = create_correlation_heatmap(df)
                st.plotly_chart(corr_fig, use_container_width=True)
            
            elif bivariate_type == "Numerical vs. Categorical":
                st.subheader("Numerical Distribution by Category")
                col_num = st.selectbox("Select a numerical column:", numerical_cols, key="biv_num")
                col_cat = st.selectbox("Select a categorical column:", categorical_cols, key="biv_cat_num")
                if col_num and col_cat:
                    fig = create_numerical_vs_categorical_plot(df, col_num, col_cat)
                    st.plotly_chart(fig, use_container_width=True)

            elif bivariate_type == "Categorical vs. Categorical":
                st.subheader("Interaction between two Categorical Variables")
                col_cat1 = st.selectbox("Select the first categorical column:", categorical_cols, key="biv_cat1")
                col_cat2 = st.selectbox("Select the second categorical column:", categorical_cols, key="biv_cat2")
                if col_cat1 and col_cat2 and col_cat1 != col_cat2:
                    fig = create_bivariate_categorical_plot(df, col_cat1, col_cat2)
                    st.plotly_chart(fig, use_container_width=True)
                elif col_cat1 == col_cat2:
                    st.warning("Please select two different columns.")

        # --- TAB 3: Machine Learning Suggestions ---
        with tab3:
            st.header("Machine Learning Preprocessing Suggestions")
            st.info("These are heuristic-based suggestions for feature engineering. Always validate with domain knowledge.")
            
            for col_name, details in ml_suggestions.items():
                with st.expander(f"**{col_name}** (Identified as: *{details['role']}*)"):
                    st.markdown(f"**Suggestion:** {details['suggestion']}")
                    st.markdown("**Example Code:**")
                    st.code(details['code'], language='python')
        
        # --- TAB 4: Alerts & Outliers ---
        with tab4:
            st.header("Data Health Report")
            if not any(health_report.values()):
                st.success("No major data health issues detected. Good job!")
            if health_report["high_missing_values"]:
                st.warning(f"**High Missing Values (>50%):** {', '.join(health_report['high_missing_values'])}")
            if health_report["constant_columns"]:
                st.warning(f"**Constant Columns:** {', '.join(health_report['constant_columns'])}")
            if health_report["high_cardinality_columns"]:
                st.info(f"**High Cardinality (Potential IDs):** {', '.join(health_report['high_cardinality_columns'])}")

            st.markdown("---")
            st.header("Outlier Report (IQR Method)")
            if not outlier_report:
                st.success("No significant outliers were detected based on the IQR method.")
            else:
                for col_name, details in outlier_report.items():
                    with st.expander(f"**{col_name}** - Found {details['count']} outliers ({details['percentage']})"):
                        st.write(f"Sample Outlier Values: `{details['sample_values']}`")
                        st.write("These values fall outside the 1.5 * IQR range and may warrant further investigation.")
                        
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        st.exception(e) # This will print the full traceback for debugging

else:
    st.info("👆 Upload a CSV file to see the magic happen!")