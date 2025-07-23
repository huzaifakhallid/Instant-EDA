import pandas as pd

def profile_data(df: pd.DataFrame) -> dict:
    rows =  df.shape[0]
    columns = df.shape[1]

    missing_cells = df.isnull().sum().sum()
    total_cells = rows * columns
    missing_percentage = (missing_cells/total_cells)*100 if total_cells > 0 else 0

    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows/rows)*100 if rows > 0 else 0

    profile = {"NUmber Of ROws: ": rows, "Number Of Columns: ": columns, "Total Missing Cells:": missing_cells, "Total Cells: ": total_cells, "Missing Percentage: ": missing_percentage, "Duplicate Rows: ": duplicate_rows, "Duplicate Percentage: ": duplicate_percentage}