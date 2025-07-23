import pandas as pd

# This function takes a DataFrame and returns a dictionary with profiling information
def profile_data(df: pd.DataFrame) -> dict:
    rows =  df.shape[0]
    columns = df.shape[1]

    missing_cells = df.isnull().sum().sum()
    total_cells = rows * columns
    missing_percentage = (missing_cells/total_cells)*100 if total_cells > 0 else 0

    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows/rows)*100 if rows > 0 else 0

    profile = {"NUmber Of ROws: ": rows, "Number Of Columns: ": columns, "Total Missing Cells:": missing_cells, "Total Cells: ": total_cells, "Missing Percentage: ": missing_percentage, "Duplicate Rows: ": duplicate_rows, "Duplicate Percentage: ": duplicate_percentage}

    return profile

# This function analyzes each column in the DataFrame and returns a summary DataFrame
def analyzecolumns(df: pd.DataFrame) -> pd.DataFrame:
    col_analysis = []

    for col in df.columns:
        dtype = df[col].dtype
        missing_values = df[col].isnull().sum()
        total_rows = len(df)
        missing_percentage = (missing_values / total_rows)*100 if total_rows > 0 else 0

    unique_values = df[col].nunique()

    col_summary = {"Column Name": col, "Data Type": dtype, "Missing Values": missing_values, "Missing Percentage": missing_percentage, "Unique Values": unique_values}

    col_analysis.append(col_summary)
    summary_df = pd.DataFrame(col_analysis)

    summary_df = summary_df.set_index("Column Name")

    return summary_df

