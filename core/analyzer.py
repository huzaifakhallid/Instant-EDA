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
        dtype = str(df[col].dtype)
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

# This function generates a health report for the DataFrame, identifying columns with high missing values, constant columns, and high cardinality columns
def get_health_report(df: pd.DataFrame) -> dict:
    report = {"high_missing_values": [], "constant_columns": [], "high_cardinality_columns": []}

    total_rows = len(df)

    for col in df.columns:
        missing_percentage = (df[col].isnull().sum() / total_rows) * 100 
        if missing_percentage > 50:
            report["high_missing_values"].append((col, f"{missing_percentage:.2f}%"))

        unique_values_count = df[col].nunique()
        if unique_values_count == 1:
            report["constant_columns"].append(f"'{col}'")


        cardinality_ratio = unique_values_count / total_rows
        if cardinality_ratio > 0.95 and unique_values_count > 1:
            report["high_cardinality_columns"].append(f"'{col}' ({unique_values_count} unique)")


    return report


def get_ml_suggestions(df: pd.DataFrame) -> dict:

    suggestions = {}
    total_rows = len(df)
    
    for col in df.columns:
        col_suggestions = {
            "Role": "Unknown",
            "Suggestion": "No specific suggestion.",
            "Code": "# No code snippet available."
        }
        
        # --- Heuristics for Role Identification ---
        nunique = df[col].nunique()
        dtype = df[col].dtype
        
        # 1. ID Column Heuristic
        if nunique == total_rows or (nunique / total_rows > 0.95 and pd.api.types.is_string_dtype(dtype)):
            col_suggestions["role"] = "Identifier"
            col_suggestions["suggestion"] = "This column has a unique value for almost every row. It's likely an ID and should probably be dropped for most models."
            col_suggestions["code"] = f"df_processed = df.drop(columns=['{col}'])"
        
        # 2. Categorical Column Heuristics
        elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_categorical_dtype(dtype) or (pd.api.types.is_integer_dtype(dtype) and nunique < 25):
            if nunique == 2:
                col_suggestions["role"] = "Binary Categorical"
                col_suggestions["suggestion"] = "This is a binary column. Use Label Encoding or One-Hot Encoding."
                col_suggestions["code"] = (
                    f"# Using scikit-learn's LabelEncoder\n"
                    f"from sklearn.preprocessing import LabelEncoder\n"
                    f"le = LabelEncoder()\n"
                    f"df_processed['{col}'] = le.fit_transform(df['{col}'])"
                )
            else:
                col_suggestions["role"] = "Low-Cardinality Categorical"
                col_suggestions["suggestion"] = "This is a categorical column with a manageable number of unique values. Use One-Hot Encoding."
                col_suggestions["code"] = (
                    f"# Using pandas get_dummies for One-Hot Encoding\n"
                    f"df_processed = pd.get_dummies(df, columns=['{col}'], prefix='{col}')"
                )

        # 3. Numerical Column Heuristics
        elif pd.api.types.is_numeric_dtype(dtype):
            col_suggestions["role"] = "Numerical"
            skewness = df[col].skew()
            if abs(skewness) > 1.5:
                col_suggestions["suggestion"] = (
                    f"This is a numerical feature. It is highly skewed (skewness = {skewness:.2f}). "
                    f"Consider applying a log or Box-Cox transformation to make its distribution more normal."
                )
                col_suggestions["code"] = (
                    f"# Using numpy for log transformation (add 1 to handle zeros)\n"
                    f"import numpy as np\n"
                    f"df_processed['{col}_log'] = np.log1p(df['{col}'])"
                )
            else:
                col_suggestions["suggestion"] = "This is a numerical feature. Standard Scaling (Z-score normalization) is a good default for many algorithms."
                col_suggestions["code"] = (
                    f"# Using scikit-learn's StandardScaler\n"
                    f"from sklearn.preprocessing import StandardScaler\n"
                    f"scaler = StandardScaler()\n"
                    f"df_processed[['{col}']] = scaler.fit_transform(df[['{col}'])"
                )
        
        # 4. Datetime Heuristic
        elif pd.api.types.is_datetime64_any_dtype(dtype):
             col_suggestions["role"] = "Datetime"
             col_suggestions["suggestion"] = "This is a datetime column. Extract useful features like year, month, day of week, etc."
             col_suggestions["code"] = (
                f"# Convert to datetime if not already\n"
                f"df['{col}'] = pd.to_datetime(df['{col}'])\n\n"
                f"# Feature Extraction Examples\n"
                f"df_processed['{col}_year'] = df['{col}'].dt.year\n"
                f"df_processed['{col}_month'] = df['{col}'].dt.month\n"
                f"df_processed['{col}_dayofweek'] = df['{col}'].dt.dayofweek"
             )

        suggestions[col] = col_suggestions
        
    return suggestions

# This function detects outliers in numerical columns of a DataFrame using the IQR method
def detect_outliers(df: pd.DataFrame) -> dict:
    outlier_report = {}
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Find the outliers
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        
        if not outliers.empty:
            outlier_report[col] = {
                "count": len(outliers),
                "percentage": f"{(len(outliers) / len(df) * 100):.2f}%",
                "sample_values": outliers.head(5).tolist() # Show a sample of 5
            }
            
    return outlier_report

def create_bivariate_categorical_plot(df: pd.DataFrame, col1: str, col2: str) -> Figure:
    # Defensive check: Limit cardinality to prevent messy plots
    if df[col1].nunique() > 20 or df[col2].nunique() > 20:
        print(f"Warning: '{col1}' or '{col2}' has too many unique values ({df[col1].nunique()}, {df[col2].nunique()}). Plot may be cluttered.")
        pass
        
    fig = px.histogram(
        df,
        x=col1,
        color=col2,
        barmode='group', # Creates grouped bars instead of stacked
        title=f"Interaction between '{col1}' and '{col2}'",
        template="plotly_white"
    )
    fig.update_layout(title_x=0.5)
    return fig


def create_numerical_vs_categorical_plot(df: pd.DataFrame, num_col: str, cat_col: str) -> Figure:
    # Defensive check: Limit cardinality of the categorical column
    if df[cat_col].nunique() > 20:
        print(f"Warning: '{cat_col}' has too many unique values ({df[cat_col].nunique()}). Plot may be cluttered.")
        pass

    fig = px.box(
        df,
        x=cat_col,
        y=num_col,
        color=cat_col, # Color by the categorical variable
        title=f"Distribution of '{num_col}' across '{cat_col}' categories",
        template="plotly_white"
    )
    fig.update_layout(title_x=0.5)
    return fig