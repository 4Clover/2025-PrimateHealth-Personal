import numpy as np
import pandas as pd
import os
from typing import Literal
from pandas import DataFrame
from sklearn.preprocessing import StandardScaler

from src import config, utils # local python files

def load_excel(file_name, data_dir=config.DATA_DIR, sheet_name=0):
    """Loads an Excel file from the data directory."""
    file_path = os.path.join(data_dir, file_name)
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Successfully loaded {file_name} (sheet: {sheet_name})")
        return df
    except FileNotFoundError:
        print(f"Error: {file_name} not found in {data_dir}")
        return None
    except Exception as e:
        print(f"Error loading Excel file {file_name}: {e}")
        return None

def load_csv(file_name, data_dir=config.DATA_DIR):
    """Loads a CSV file from the data directory."""
    file_path:str = str(os.path.join(data_dir, file_name))
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {file_name}")
        return df
    except FileNotFoundError:
        print(f"Error: {file_name} not found in {data_dir}")
        return None
    except Exception as e:
        print(f"Error loading CSV file {file_name}: {e}")
        return None

PD_HOW : Literal['inner', 'left', 'right', 'outer', 'cross'] = 'inner'
def join_datasets(df_left, df_right, left_on=None, right_on=None, on=None, how=PD_HOW):
    """Joins two DataFrames. If 'on' is None, uses common columns."""
    if df_left is None or df_right is None:
        print("Cannot join: one or both DataFrames are None.")
        return None
    try:
        if on:
            log_on = on
        elif left_on and right_on:
            log_on = f"left_on={left_on}, right_on={right_on}"
        else: # infer common columns if 'on', 'left_on', 'right_on' are not specified
            log_on = "inferred common columns"
        joined_df = pd.merge(df_left, df_right, how=how, on=on, left_on=left_on, right_on=right_on)
        print(f"Successfully joined datasets on {log_on} using '{how}' join.")
        return joined_df
    except Exception as e:
        print(f"Error joining datasets: {e}")
        return None


def clean_data(df):
    """Performs basic data cleaning on the provided DataFrame."""
    if df is None:
        print("DataFrame for cleaning is None. Skipping cleaning.")
        return None

    print("\n--- Starting Data Cleaning ---")
    df_cleaned = df.copy()

    print("Initial Data Info (before extensive cleaning):")
    df_cleaned.info(verbose = True, show_counts = True)  # verbose for more detail

    print("\nMissing Values Before Cleaning:")
    print(df_cleaned.isnull().sum()[df_cleaned.isnull().sum() > 0])  # show NaN columns

    # ---- CLEANING STEPS ----

    # 1. Handle Missing Values
    # mean/median/mode imputation for numeric, mode for categorical
    for col in df_cleaned.select_dtypes(include = np.number).columns:
        if df_cleaned[col].isnull().any():
            median_val = df_cleaned[col].median()
            df_cleaned[col].fillna(median_val, inplace = True)
            print(f"Filled NaNs in numeric column '{col}' with median ({median_val:.2f}).")

    # Safeguard for non-numerics still present (Project data does not contain this)
    for col in df_cleaned.select_dtypes(include = 'object').columns:
        if df_cleaned[col].isnull().any():
            mode_val = df_cleaned[col].mode()
            if not mode_val.empty:
                df_cleaned[col].fillna(mode_val[0], inplace = True)
                print(f"Filled NaNs in categorical column '{col}' with mode ({mode_val[0]}).")
            else:
                print(f"Warning: No mode found for column '{col}'. NaNs remain.")

        # Convert object columns that look numeric but are stored as strings
        try:
            # Attempt conversion if it seems numeric (e.g., '123', '45.6')
            # set at 10 assuming numbers wont exceed 10 characters of uniq values ie > "1000000000" (1 billion)
            if (df_cleaned[col].astype(str).str.match(r'^-?\d+(\.\d+)?$').all() and
                    df_cleaned[col].nunique() > 10): # heuristic
                df_cleaned[col] = pd.to_numeric(
                    df_cleaned[col], errors = 'coerce')  # coerce errors to NaN then impute again
                print(f"Converted object column '{col}' to numeric.")
                if df_cleaned[col].isnull().any():  # re-impute if conversion created NaNs
                    median_val = df_cleaned[col].median()
                    df_cleaned[col].fillna(median_val, inplace = True)
                    print(f"Filled NaNs in newly numeric column '{col}' with median ({median_val:.2f}).")
        except Exception as e:
            print(f"Could not attempt numeric conversion for column '{col}': {e}")

    # 2. Convert Data Types (unneeded ATP)

    # 3. Remove Duplicates
    initial_rows = len(df_cleaned)
    df_cleaned.drop_duplicates(inplace = True)
    if len(df_cleaned) < initial_rows:
        print(f"Removed {initial_rows - len(df_cleaned)} duplicate rows.")

    print("\nMissing Values After Cleaning:")
    final_nans = df_cleaned.isnull().sum()
    if final_nans.sum() == 0:
        print("No missing values remain after cleaning.")
    else:
        print(final_nans[final_nans > 0])

    print("\nData Info After Cleaning:")
    df_cleaned.info(verbose = True, show_counts = True)

    print("--- Data Cleaning Complete ---")
    utils.save_dataframe(df_cleaned, "final_cleaned_data", subdir = "processed")
    return df_cleaned

def load_and_prepare_project_data():
    """
    Loads and prepares data according to Project needs:
    1. Loads demographics, exposure, and pedigree Excel files.
    2. Left joins demographics and exposure.
    3. Selects specific columns, dropping "ID", "Sex", "StudyID".
    4. Checks if all remaining columns are numeric.
    Returns the formatted DataFrame and the 'pedigree' DataFrame.
    """
    print("\n--- Starting Project Data Loading and Preparation ---")
    demographics_df = load_excel("PFT_demographics.xlsx")
    exposure_df = load_excel("predictor_exposure.xlsx")
    pedigree_df = load_excel("predictor_pedigree.xlsx") # loaded, not joined

    if demographics_df is None or exposure_df is None:
        print("Error: Could not load 'demographics' or 'exposure' data. Aborting preparation.")
        return None, pedigree_df

    # R's left_join without 'by' uses all common columns.
    # Pandas merge does the same if 'on', 'left_on', 'right_on' are None.
    print("Attempting to join 'demographics' and 'exposure' on common columns...")
    combined_df = join_datasets(demographics_df, exposure_df, how='left')

    if combined_df is None:
        print("Error: Failed to join demographics and exposure. Aborting preparation.")
        return None, pedigree_df

    columns_to_drop = ["ID", "Sex", "StudyID"]
    # drop columns that actually exist to avoid errors
    existing_columns_to_drop = [col for col in columns_to_drop if col in combined_df.columns]
    if not existing_columns_to_drop:
        print(f"Warning: None of the specified columns to drop {columns_to_drop} found in the combined DataFrame.")
        final_cleaned_df = combined_df.copy()
    else:
        print(f"Dropping columns: {existing_columns_to_drop}")
        final_cleaned_df = combined_df.drop(columns=existing_columns_to_drop)

    print("\n--- Checking if all columns in 'thinned_df' are numeric ---")
    if not final_cleaned_df.empty:
        #robust check for numeric types, including integers, floats
        are_all_numeric = final_cleaned_df.apply(lambda s: pd.api.types.is_numeric_dtype(s.dtype)).all()
        if are_all_numeric:
            print("Success: All columns in 'thinned_df' are numeric.")
        else:
            print("Warning: Not all columns in 'thinned_df' are numeric after selection.")
            print("Non-numeric columns found:")
            for col in final_cleaned_df.columns:
                if not pd.api.types.is_numeric_dtype(final_cleaned_df[col].dtype):
                    print(f"  - {col} (dtype: {final_cleaned_df[col].dtype})")
            print("Further cleaning or type conversion might be necessary in the clean_data step.")
    else:
        print("Warning: 'thinned_df' is empty after operations.")

    utils.save_dataframe(final_cleaned_df, "thinned_pre_cleaning", subdir="processed")
    if pedigree_df is not None:
        utils.save_dataframe(pedigree_df, "pedigree_raw", subdir="processed")

    print("--- Project Data Loading and Preparation Complete ---")
    return final_cleaned_df, pedigree_df

def get_exposure_groups(df, prefixes):
    """
    Groups columns in a DataFrame based on a list of prefixes.
    Args:
        df (pd.DataFrame): The input DataFrame.
        prefixes (list): A list of string prefixes (e.g., ['gest_', 'infancy_']).
    Returns:
        dict: A dictionary where keys are prefixes and values are lists of column names.
    """
    exposure_groups = {prefix: [] for prefix in prefixes}
    # Add a group for columns not matching any prefix, if needed
    # exposure_groups['other_exposures'] = []

    for col in df.columns:
        matched = False
        for prefix in prefixes:
            if col.startswith(prefix):
                exposure_groups[prefix].append(col)
                matched = True
                break
        # if not matched and col not in ['Raw_mean', 'Iti_mean', 'Cti_mean', 'BW_zscore', 'AgeAtScreen', 'ID', 'Sex', 'StudyID']: # Example exclusion
        #     # Be careful with what constitutes 'other' exposures.
        #     # This part might need refinement based on exact column names.
        #     if pd.api.types.is_numeric_dtype(df[col]): # Only consider numeric 'other' exposures
        #          exposure_groups['other_exposures'].append(col)
    # Filter out empty groups (if a prefix had no matching columns)
    exposure_groups = {k: v for k, v in exposure_groups.items() if v}
    return exposure_groups

def prepare_data_for_sem(df):
    """
    Prepares data for SEM analysis:
    1. Removes columns where all entries are NAs.
    2. Scales all numeric columns to have mean zero and unit variance.
    """
    print("\n--- Preparing data for SEM ---")
    # 1. Remove columns with all NAs
    df_sem = df.copy()
    cols_before_dropna = df_sem.shape[1]
    df_sem.dropna(axis=1, how='all', inplace=True)
    cols_after_dropna = df_sem.shape[1]
    if cols_before_dropna > cols_after_dropna:
        print(f"Removed {cols_before_dropna - cols_after_dropna} columns with all NA values.")

    # 2. Scale numeric columns
    numeric_cols_sem = df_sem.select_dtypes(include=np.number).columns
    if not numeric_cols_sem.empty:
        scaler = StandardScaler()
        df_sem[numeric_cols_sem] = scaler.fit_transform(df_sem[numeric_cols_sem])
        print(f"Scaled {len(numeric_cols_sem)} numeric columns for SEM (mean 0, variance 1).")
    else:
        print("No numeric columns found to scale for SEM.")

    utils.save_dataframe(df_sem, "data_scaled_for_sem", subdir="processed")
    return df_sem