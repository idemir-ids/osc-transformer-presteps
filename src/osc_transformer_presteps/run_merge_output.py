"""Python Script for merging output on cli."""

import pandas as pd
import os

# External modules
import typer

app = typer.Typer(no_args_is_help=True)

def load_file_to_dataframe(file_path):
    """
    Load a CSV or XLSX file into a pandas DataFrame.

    Parameters:
    -----------
    file_path : str
        Path to the file (CSV or XLSX)

    Returns:
    --------
    pd.DataFrame
        DataFrame containing the file data

    Raises:
    -------
    ValueError
        If file extension is not supported
    FileNotFoundError
        If file doesn't exist
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    # Load based on extension
    if file_extension == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Supported types: .csv, .xlsx, .xls")

    return df

def standardize_header(df):
    """
    Standardize DataFrame column headers by converting to uppercase and applying column mapping.

    This function performs two operations:
    1. Converts all column names to uppercase
    2. Renames columns according to a provided mapping dictionary

    The mapping is designed to align TB (Text-Based) format columns 
    with RB (Rule-Based) format columns for data integration.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame with headers to be standardized

    Returns:
    --------
    pd.DataFrame
        DataFrame with standardized column names

    Notes:
    ------
    Default mapping aligns the following formats:

    RB-Header (Rule-Based):
        KPI_ID, KPI_NAME, SRC_FILE, PAGE_NUM, ITEM_IDS, POS_X, POS_Y, 
        RAW_TXT, YEAR, VALUE, SCORE, UNIT, MATCH_TYPE

    TB-Header (Text-Based):
        PDF_NAME, QUESTION, PREDICTED_ANSWER, SCORE, PAGE, CONTEXT, 
        KPI_ID, UNIQUE_PARAGRAPH_ID, PARAGRAPH_RELEVANCE_SCORE(FOR_LABEL=1), 
        PARAGRAPH_RELEVANCE_FLAG, START, END

    Default TB-to-RB mapping:
        - PDF_NAME → SRC_FILE
        - PREDICTED_ANSWER → VALUE
        - PAGE → PAGE_NUM

    """

    MAP_TB_2_RB = {
        'PDF_NAME': 'SRC_FILE',
        'PREDICTED_ANSWER': 'VALUE',
        'PAGE': 'PAGE_NUM',
    }
    df.columns = df.columns.str.upper()
    df = df.rename(columns=MAP_TB_2_RB)
    
    return df

def combine_dataframes(df1, df2, sort_columns=False, drop_duplicates=False, column_order=None):
    """
    Combine two DataFrames with partially overlapping columns.

    Parameters:
    -----------
    df1 : pd.DataFrame
        First DataFrame to combine
    df2 : pd.DataFrame
        Second DataFrame to combine
    sort_columns : bool, default False
        If True, sort column names alphabetically in the result.
        Note: This is ignored if column_order is provided.
    drop_duplicates : bool, default False
        If True, remove duplicate rows from the combined result
    column_order : list, optional
        List of column names to appear first in the result DataFrame.
        Columns not in this list will follow in their original order.
        Example: ['KPI_ID', 'KPI_NAME', 'VALUE']

    Returns:
    --------
    pd.DataFrame
        Combined DataFrame containing all rows from both input DataFrames

    """
    # Concatenate DataFrames vertically
    combined_df = pd.concat([df1, df2], ignore_index=True, sort=False)

    # Optionally remove duplicates
    if drop_duplicates:
        combined_df = combined_df.drop_duplicates().reset_index(drop=True)

    # Handle column ordering
    if column_order is not None:
        # Filter column_order to only include columns that exist in combined_df
        existing_priority_cols = [col for col in column_order if col in combined_df.columns]

        # Get remaining columns (not in column_order) in their original order
        remaining_cols = [col for col in combined_df.columns if col not in existing_priority_cols]

        # Reorder: priority columns first, then remaining columns
        new_column_order = existing_priority_cols + remaining_cols
        combined_df = combined_df[new_column_order]

    elif sort_columns:
        # Sort columns alphabetically if no specific order provided
        combined_df = combined_df[sorted(combined_df.columns)]

    return combined_df


@app.command()
def merge_output(
    file_path1: str = typer.Argument(
        help="Path to the first file (CSV or XLSX) to be combined. "
        "This should be in the current folder or some subfolder."
    ),
    file_path2: str = typer.Argument(
        help="Path to the second file (CSV or XLSX) to be combined. "
        "This should be in the current folder or some subfolder."
    ),
    output_file: str = typer.Option(
        default="combined_output.csv",
        "--output",
        "-o",
        show_default=True,
        help="Path where the combined CSV file should be saved. "
        "Example: 'output/combined_data.csv'"
    ),
) -> None:
    """
    Load two files, standardize their headers, combine them, apply data transformations, and save.

    This command orchestrates the complete data integration pipeline:

    1. Load both files (CSV or XLSX) into DataFrames

    2. Standardize headers (uppercase + column mapping)

    3. Combine the DataFrames with specified column order

    4. Fill null values in MATCH_TYPE column with "TB"

    5. Save the result to a CSV file

    \b
    Notes:
    ------
    - Priority column order: KPI_ID, SRC_FILE, VALUE, SCORE, PAGE_NUM, MATCH_TYPE
    - If any priority columns don't exist in the data, they are skipped
    - MATCH_TYPE column is automatically filled with "TB" where values are null/NaN
    - Both files are processed with the standardize_header function which applies
      uppercase conversion and column mapping

    """
    try:
        # Step 1: Load both files
        typer.echo(f"Loading file 1: {file_path1}")
        df1 = load_file_to_dataframe(file_path1)

        typer.echo(f"Loading file 2: {file_path2}")
        df2 = load_file_to_dataframe(file_path2)

        # Step 2: Standardize headers for both DataFrames
        typer.echo("Standardizing headers...")
        df1 = standardize_header(df1)
        df2 = standardize_header(df2)

        # Step 3: Define priority column order
        PRIORITY_COLUMNS = ['KPI_ID', 'SRC_FILE', 'VALUE', 'SCORE', 'PAGE_NUM', 'MATCH_TYPE']

        # Step 4: Combine DataFrames
        typer.echo("Combining DataFrames...")
        combined_df = combine_dataframes(df1, df2, 
                                        column_order=PRIORITY_COLUMNS,
                                        drop_duplicates=False)

        # Step 5: Fill null values in MATCH_TYPE with "TB"
        if 'MATCH_TYPE' in combined_df.columns:
            combined_df['MATCH_TYPE'] = combined_df['MATCH_TYPE'].fillna('TB')
            typer.echo("Filled null MATCH_TYPE values with 'TB'")

        # Step 6: Save to CSV
        combined_df.to_csv(output_file, index=False)
        typer.secho(f"✓ Combined data saved to: {output_file}", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"Total rows: {len(combined_df)}")
        typer.echo(f"Total columns: {len(combined_df.columns)}")

    except FileNotFoundError as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"✗ Unexpected error: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()