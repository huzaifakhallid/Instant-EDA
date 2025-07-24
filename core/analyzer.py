import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

# This function takes a DataFrame and returns a dictionary with profiling information
def profile_data(df: pd.DataFrame) -> dict:
    rows =  df.shape[0]
    cols = df.shape[1]

    missing_cells = df.isnull().sum().sum()
    total_cells = rows * cols
    missing_percentage = (missing_cells/total_cells)*100 if total_cells > 0 else 0

    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows/rows)*100 if rows > 0 else 0

    profile = {"Number of Rows": rows, "Number of Columns": cols, "Total Missing Cells": f"{missing_cells} ({missing_percentage:.2f}%)", "Total Duplicate Rows": f"{duplicate_rows} ({duplicate_percentage:.2f}%)"}

    return profile

# This function analyzes each column in the DataFrame and returns a summary DataFrame
def analyze_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_analysis = []

    for col in df.columns:
        dtype = df[col].dtype
        missing_values = df[col].isnull().sum()
        total_rows = len(df)
        missing_percentage = (missing_values / total_rows)*100 if total_rows > 0 else 0

    unique_values = df[col].nunique()

    col_summary = { "Column Name": col, "Data Type": dtype, "Missing Values (%)": f"{missing_percentage:.2f}","Unique Values": unique_values }

    col_analysis.append(col_summary)
    summary_df = pd.DataFrame(col_analysis)

    summary_df = summary_df.set_index("Column Name")

    return summary_df

# This function creates a histogram for a specified column in the DataFrame
def create_histogram(df: pd.DataFrame, column: str) -> Figure:
    fig = px.histogram(df, x=column, title = f"Histogram of {column}", template = "plotly_white")

    return fig

# This function creates a bar plot for the frequency of categories in a specified column
def create_barplot(df: pd.DataFrame, column: str) -> Figure:
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'Count']

    value_counts = value_counts.sort_values(by='Count', ascending=False)

    if len(value_counts) > 20:
        value_counts = value_counts.head(20)
        plot_title = f"Top 20 Most Frequent Categories in {column}"

    else:
        plot_title = f"Frequency of Categories in {column}"

    fig = px.bar(value_counts, x=column, y='Count', title=plot_title, template="plotly_white")

    return fig

# This function creates a correlation heatmap for the numerical columns in the DataFrame
def create_correlation_heatmap(df: pd.DataFrame) -> Figure:
    numerical_df = df.select_dtypes(include = ['int64', 'float64'])
    correlation_matrix = numerical_df.corr()

    fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto", title="Correlation Matrix", template="plotly_white")

    fig.update_layout(title_x=0.5)

    return fig