import streamlit as st
import pandas as pd
from core.analyzer import (
    profile_data, 
    analyze_columns, 
    create_histogram, 
    create_barplot,
    create_correlation_heatmap
)

# --- Page Configuration ---
st.set_page_config(
    page_title="InstantEDA",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- App Title and Description ---
st.title("Instant EDA ")
st.markdown("""
    Welcome to InstantEDA! This tool automates the Exploratory Data Analysis process. 
    Just upload your CSV file below to get started.
""")

# --- Uploader ---
uploaded_file = st.file_uploader(
    "Upload a CSV file to begin analysis.",
    type=["csv"],
    label_visibility="collapsed" 
)

# --- Main App Logic ---
if uploaded_file is not None:
    # --- Read the uploaded data ---
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded and read successfully!")
        
        # --- Organize report into TABS ---
        tab1, tab2, tab3 = st.tabs(["📊 Data Overview", "📈 Univariate Analysis", "📉 Bivariate Analysis"])
        
        # --- TAB 1: Data Overview ---
        with tab1:
            st.header("Data Preview")
            st.dataframe(df.head())
            
            st.header("Data Profile")
            profile = profile_data(df)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Number of Rows", profile["Number of Rows"])
            with col2:
                st.metric("Number of Columns", profile["Number of Columns"])
            with col3:
                st.metric("Missing Cells", profile["Total Missing Cells"])
            with col4:
                st.metric("Duplicate Rows", profile["Total Duplicate Rows"])
            
            st.header("Column-wise Analysis")
            column_summary_df = analyze_columns(df)
            st.dataframe(column_summary_df)

        # --- TAB 2: Univariate Analysis ---
        with tab2:
            st.header("Distribution Analysis")
            
            # Create a select box for the user to choose a column
            selected_column = st.selectbox(
                "Select a column to visualize its distribution:",
                df.columns,
                key="univariate_select" # Add a unique key
            )
            
            if selected_column:
                st.subheader(f"Analysis of '{selected_column}'")
                
                if pd.api.types.is_numeric_dtype(df[selected_column]):
                    fig = create_histogram(df, selected_column)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = create_barplot(df, selected_column)
                    st.plotly_chart(fig, use_container_width=True)

        # --- TAB 3: Bivariate Analysis ---
        with tab3:
            st.header("Correlation Heatmap")
            st.write("Visualizing the correlation between numerical features.")
            
            corr_fig = create_correlation_heatmap(df)
            st.plotly_chart(corr_fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error reading the file: {e}")

else:
    # --- Initial landing page content ---
    st.info(" Upload a CSV file to see the magic happen!")