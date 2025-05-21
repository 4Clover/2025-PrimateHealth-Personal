# main_pipeline.py
import pandas as pd
import numpy as np  # Ensure numpy is imported for select_dtypes and other uses
import os
import semopy  # For SEM variable parsing, if used in main

from src import config
from src import dataloader, eda_analyzer, pca_analyzer, cca_analyzer, sem_modeler, utils, visualizer


def generate_final_html_report(report_parts, filename = "analysis_report.html"):
    """Combines all HTML parts into a single report file."""
    html_start = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Analysis Report</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <style>
                body { font-family: sans-serif; margin: 20px; }
                h1, h2, h3 { color: #333; }
                h2 { border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 30px; }
                .table { margin-top: 15px; margin-bottom: 15px; font-size: 0.9em; }
                img { border: 1px solid #ddd; margin-top:10px; margin-bottom:10px; display: block; max-width: 100%; height: auto; }
                .container { max-width: 1200px; } /* Increased width for larger plots */
                .dataframe_div table { width: auto !important; }
                .sem-model-spec { background-color: #f5f5f5; border: 1px solid #ccc; padding: 10px; white-space: pre-wrap; font-family: monospace;}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Comprehensive Data Analysis Report</h1>
    """
    html_end = """
           </div>
       </body>
       </html>
    """

    full_html_content = html_start + "\n".join(report_parts) + html_end
    report_filepath = os.path.join(config.REPORT_DIR, filename)
    with open(report_filepath, 'w', encoding = 'utf-8') as f:
        f.write(full_html_content)
    print(f"HTML report generated: {report_filepath}")

    vercel_report_filepath = os.path.join(config.VERCEL_PUBLIC_DIR, "index.html")
    with open(vercel_report_filepath, 'w', encoding = 'utf-8') as f:
        f.write(full_html_content)
    print(f"HTML report for Vercel generated: {vercel_report_filepath}")


def main():
    config.create_output_dirs()
    report_html_parts = []

    # --- 1. Load Raw Data ---
    demographics_df_raw = dataloader.load_excel("PFT_demographics.xlsx")
    exposure_df_raw = dataloader.load_excel("predictor_exposure.xlsx")
    # pedigree_df_raw = data_loader.load_excel_dataset("predictor_pedigree.xlsx") # Loaded but not used in this CCA flow

    if demographics_df_raw is None or exposure_df_raw is None:
        return

    combined_df_raw = pd.merge(demographics_df_raw, exposure_df_raw, how = 'left')
    utils.generate_html_report_section(
        "Raw Data Loading",
        [utils.df_to_html_table(combined_df_raw.head(), "Initial Combined DataFrame (Head)")],
        report_html_parts
    )

    # --- 2. Preprocessing Combined Data ---
    current_df = combined_df_raw.copy()
    report_html_parts.append("<h2>Data Preprocessing</h2>")

    # 2a. Remove columns with zero variance
    initial_cols = current_df.shape[1]
    # Calculate variance, ensure it's > 0, and Handle NaN columns
    numeric_cols_for_variance_check = current_df.select_dtypes(include = np.number).columns
    non_numeric_cols = current_df.select_dtypes(exclude = np.number).columns

    if not numeric_cols_for_variance_check.empty:
        numeric_variances = current_df[numeric_cols_for_variance_check].var(skipna = True)
        numeric_cols_with_variance = numeric_variances[
            (numeric_variances > 0) & (~numeric_variances.isna())].index.tolist()
        df_processed = pd.concat([current_df[non_numeric_cols], current_df[numeric_cols_with_variance]], axis = 1)
    else:
        df_processed = current_df[non_numeric_cols].copy()  # No numeric columns to check

    cols_removed_variance = initial_cols - df_processed.shape[1]
    report_html_parts.append(f"<p>Removed {cols_removed_variance} numeric columns with zero or NA variance.</p>")
    utils.save_dataframe(df_processed, "df_after_variance_filter", subdir = "processed")

    # 2b. Response Variables
    response_vars_names = ['Raw_mean', 'Iti_mean', 'Cti_mean']
    missing_responses = [rv for rv in response_vars_names if rv not in df_processed.columns]
    if missing_responses:
        return
    df_responses_cca = df_processed[response_vars_names].copy()
    report_html_parts.append(f"<p>Selected response variables for CCA: {', '.join(response_vars_names)}</p>")

    report_html_parts.append("<h2>Predictor Group Definitions</h2>")

    life_stage_prefixes = ["gest_", "neonatal_", "infancy_", "postnatal_", "PFTpre_7d_",
                           "PFTpre_30d_"]
    demographic_predictor_cols_names = ['AgeAtScreen', 'Age_Bin', 'BodyWeight', 'BW_Bin', 'BW_zscore', 'FRC', 'Cg',
                                        'Ettube', 'EC150']

    # Special exposure variables
    special_assignment_vars = ['BW_zscore', 'AgeAtScreen']
    actual_special_assignment_vars = [v for v in special_assignment_vars if
                                      v in df_processed.columns and pd.api.types.is_numeric_dtype(df_processed[v])]
    if actual_special_assignment_vars:
        report_html_parts.append(
            f"<p>Special variables for assignment (if available and numeric): {', '.join(actual_special_assignment_vars)}</p>")

    # 'demographics' predictor group DataFrame
    df_demographics_predictors = None
    actual_demographic_cols = [col for col in demographic_predictor_cols_names if col in df_processed.columns]
    if actual_demographic_cols:
        # only numeric columns
        df_demographics_predictors_numeric = df_processed[actual_demographic_cols].select_dtypes(include = np.number)
        if not df_demographics_predictors_numeric.empty:
            df_demographics_predictors = df_demographics_predictors_numeric
            report_html_parts.append(
                f"<p>Created 'demographics' predictor group with {len(df_demographics_predictors.columns)} numeric variables: {', '.join(df_demographics_predictors.columns)}</p>")
        else:
            report_html_parts.append(
                "<p>No numeric demographic predictor variables found for 'demographics' group.</p>")
    else:
        report_html_parts.append("<p>'Demographics' predictor group: No specified columns found.</p>")

    # life-stage predictor group DataFrames
    # dictionaries: group_name -> DataFrame_of_predictors
    lifespan_predictor_dfs = { }
    candidate_cols_for_lifespan_groups = df_processed.select_dtypes(include = np.number).columns.difference(
        response_vars_names + demographic_predictor_cols_names
        # Exclude responses and demo vars to avoid overlap for these groups
    ).tolist()
    df_candidate_lifespan_exposures = df_processed[candidate_cols_for_lifespan_groups]

    lifespan_exposure_groups_col_names = dataloader.get_exposure_groups(df_candidate_lifespan_exposures,
                                                                         life_stage_prefixes)

    for group_name_prefix, cols_in_group in lifespan_exposure_groups_col_names.items():
        if cols_in_group:
            # Select only numeric columns (safeguard)
            df_group = df_processed[cols_in_group].select_dtypes(include = np.number)
            if not df_group.empty:
                lifespan_predictor_dfs[group_name_prefix] = df_group
                report_html_parts.append(
                    f"<p>Created '{group_name_prefix}' life-stage predictor group with {len(df_group.columns)} numeric variables.</p>")
            else:
                report_html_parts.append(
                    f"<p>No numeric variables found for life-stage group '{group_name_prefix}'.</p>")

    # --- 3. CCA for each group ---
    report_html_parts.append("<h2>CCA Analyses and Biplots</h2>")

    # Helper function for running CCA and plotting biplots
    def run_cca_and_plot(title_prefix, df_exposures, df_responses, exposure_names_for_plot, response_names_for_plot,
                         report_parts_list):
        report_parts_list.append(f"<h4>{title_prefix}</h4>")

        if df_exposures.empty or df_exposures.shape[1] == 0:
            report_parts_list.append("<p>No exposure variables provided. Skipping CCA.</p>")
            return None, None
        if df_responses.empty:
            report_parts_list.append("<p>No response variables provided. Skipping CCA.</p>")
            return None, None

        # Align samples
        temp_df_aligned = pd.concat([df_exposures, df_responses], axis = 1).dropna()

        min_samples_needed = max(df_exposures.shape[1], df_responses.shape[1]) + 1  # heuristic
        if temp_df_aligned.empty or len(temp_df_aligned) < min_samples_needed:
            report_parts_list.append(
                f"<p>Not enough data rows ({len(temp_df_aligned)}) after NaN removal for CCA. Required at least {min_samples_needed} samples. Skipping.</p>")
            return None, None

        df_exposures_aligned = temp_df_aligned[df_exposures.columns]
        df_responses_aligned = temp_df_aligned[df_responses.columns]

        cca_model, (X_c, Y_c) = cca_analyzer.perform_cca(
            df_exposures_aligned, df_responses_aligned, report_parts = report_parts_list, max_iter = 1000
        )

        if cca_model and X_c is not None:
            visualizer.plot_cca_biplot(
                cca_model, exposure_names_for_plot, response_names_for_plot,
                X_c, Y_c, axes_pair = (0, 1),  # Axes 1 vs 2
                report_parts = report_parts_list, plot_title_prefix = title_prefix
            )
            if cca_model.n_components >= 3:
                visualizer.plot_cca_biplot(
                    cca_model, exposure_names_for_plot, response_names_for_plot,
                    X_c, Y_c, axes_pair = (0, 2),  # Axes 1 vs 3
                    report_parts = report_parts_list, plot_title_prefix = title_prefix
                )
        return cca_model, (X_c, Y_c)

    # 3a. CCA for each Life-Stage Group
    report_html_parts.append("<h3>CCAs for Life-Stage Exposure Groups (Assignment Logic)</h3>")
    for life_stage_name, df_life_stage_exposures_base in lifespan_predictor_dfs.items():
        report_html_parts.append(f"<h4>Analysis for Life-Stage Group: {life_stage_name}</h4>")

        # Run 1: WITH actual_special_assignment_vars
        title_run1 = f"CCA_{life_stage_name}_with_SpecialVars"
        cols_for_run1 = df_life_stage_exposures_base.columns.tolist()
        if actual_special_assignment_vars:
            # Add special vars (avoid duplicates)
            cols_for_run1.extend([v for v in actual_special_assignment_vars if v not in cols_for_run1])

        df_exposures_run1 = df_processed[cols_for_run1].copy()  # Select from df_processed to ensure consistency

        run_cca_and_plot(title_run1, df_exposures_run1, df_responses_cca,
                         df_exposures_run1.columns.tolist(), response_vars_names, report_html_parts)

        # Run 2: WITHOUT actual_special_assignment_vars (just the life-stage group)
        title_run2 = f"CCA_{life_stage_name}_without_SpecialVars"
        run_cca_and_plot(title_run2, df_life_stage_exposures_base, df_responses_cca,
                         df_life_stage_exposures_base.columns.tolist(), response_vars_names, report_html_parts)

        report_html_parts.append(
            f"<p><b>Interpretation of {life_stage_name}:</b> `BW_zscore` and `AgeAtScreen` influence?</p>"
        )

    # 3b. CCA for the 'demographics' group
    report_html_parts.append("<h3>CCA for 'Demographics' Exposure Group</h3>")
    if df_demographics_predictors is not None and not df_demographics_predictors.empty:
        title_demo_run = "CCA_Demographics_Group"
        run_cca_and_plot(title_demo_run, df_demographics_predictors, df_responses_cca,
                         df_demographics_predictors.columns.tolist(), response_vars_names, report_html_parts)
    else:
        report_html_parts.append("<p>'Demographics' predictor group is empty or not defined. Skipping CCA.</p>")

    # --- 4. SEM Preparation and Modeling (Instruction 3 from previous prompt) ---
    report_html_parts.append("<h2>Structural Equation Modeling (SEM)</h2>")
    generate_final_html_report(report_html_parts)
    print("\n--- Analysis Pipeline Complete ---")

if __name__ == '__main__':
    main()