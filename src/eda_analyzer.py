import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src import utils, config


def perform_univariate_analysis(df, column, report_parts):
    """Performs and visualizes univariate analysis for a single column."""
    if df is None or column not in df.columns:
        print(f"Column {column} not found or DataFrame is None.")
        return

    content_html = [f"<h4>Analysis for Column: {column}</h4>"]

    # Summary Statistics
    summary_stats = df[column].describe().to_frame().transpose()
    content_html.append(utils.df_to_html_table(summary_stats, title = "Summary Statistics"))

    # Distribution Plot (Histogram/KDE for numeric, Bar plot for categorical)
    plt.figure(figsize = (10, 6))
    if pd.api.types.is_numeric_dtype(df[column]):
        sns.histplot(df[column], kde = True)
        plt.title(f'Distribution of {column}')
        plot_filename = f"dist_{column.replace(' ', '_').lower()}"
        utils.save_plot(plt.gcf(), plot_filename, subdir = "eda/univariate")
        content_html.append(
            utils.plot_to_html_img(plot_filename, subdir = "eda/univariate", alt_text = f"Distribution of {column}"))

        # Box Plot for Outliers
        plt.figure(figsize = (8, 5))
        sns.boxplot(x = df[column])
        plt.title(f'Box Plot of {column} (Outlier Check)')
        plot_filename_box = f"boxplot_{column.replace(' ', '_').lower()}"
        utils.save_plot(plt.gcf(), plot_filename_box, subdir = "eda/univariate")
        content_html.append(
            utils.plot_to_html_img(plot_filename_box, subdir = "eda/univariate", alt_text = f"Box Plot of {column}"))

    elif pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_categorical_dtype(df[column]):
        df[column].value_counts().plot(kind = 'bar')
        plt.title(f'Frequency of Categories in {column}')
        plt.ylabel('Frequency')
        plot_filename = f"bar_{column.replace(' ', '_').lower()}"
        utils.save_plot(plt.gcf(), plot_filename, subdir = "eda/univariate")
        content_html.append(
            utils.plot_to_html_img(plot_filename, subdir = "eda/univariate", alt_text = f"Bar Chart of {column}"))

    utils.generate_html_report_section(f"Univariate Analysis: {column}", content_html, report_parts)


def perform_multivariate_analysis(df, numeric_cols, report_parts):
    """Performs and visualizes multivariate analysis (correlation matrix)."""
    if df is None or not numeric_cols:
        print("DataFrame is None or no numeric columns specified.")
        return

    content_html = []
    df_numeric = df[numeric_cols].copy()

    # Correlation Matrix
    correlation_matrix = df_numeric.corr()
    content_html.append(utils.df_to_html_table(correlation_matrix.round(2), title = "Correlation Matrix"))

    plt.figure(figsize = (12, 10))
    sns.heatmap(correlation_matrix, annot = True, cmap = 'coolwarm', fmt = ".2f", linewidths = .5)
    plt.title('Correlation Matrix Heatmap')
    plot_filename = "correlation_heatmap"
    utils.save_plot(plt.gcf(), plot_filename, subdir = "eda/multivariate")
    content_html.append(
        utils.plot_to_html_img(plot_filename, subdir = "eda/multivariate", alt_text = "Correlation Heatmap"))

    # Pair Plot (optional, can be slow for many variables)
    # if len(numeric_cols) <= 5: # Limit to avoid overly large plots
    #     plt.figure() # sns.pairplot creates its own figure
    #     pairplot_fig = sns.pairplot(df_numeric)
    #     pairplot_fig.fig.suptitle('Pair Plot of Numeric Variables', y=1.02)
    #     plot_filename_pair = "pairplot_numeric"
    #     utils.save_plot(pairplot_fig.fig, plot_filename_pair, subdir="eda/multivariate")
    #     content_html.append(utils.plot_to_html_img(plot_filename_pair, subdir="eda/multivariate", alt_text="Pair Plot"))
    # else:
    #     content_html.append("<p>Pair plot skipped due to large number of numeric variables.</p>")

    utils.generate_html_report_section("Multivariate Analysis", content_html, report_parts)