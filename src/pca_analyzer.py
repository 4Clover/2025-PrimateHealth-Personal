import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from src import utils, config


def perform_pca(df_numeric, n_components = None, report_parts = None):
    """Performs PCA on numeric columns of a DataFrame."""
    if df_numeric is None or df_numeric.empty:
        print("Cannot perform PCA: DataFrame is None or empty.")
        return None, None

    content_html = []

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_numeric)

    # Perform PCA
    if n_components is None:  # Determine optimal number or use all
        pca = PCA()
    else:
        pca = PCA(n_components = n_components)

    principal_components = pca.fit_transform(scaled_data)

    # Explained Variance
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_explained_variance = np.cumsum(explained_variance_ratio)

    content_html.append("<h4>Explained Variance per Component:</h4>")
    ev_df = pd.DataFrame({ 'Principal Component': range(1, len(explained_variance_ratio) + 1),
                           'Explained Variance Ratio': explained_variance_ratio,
                           'Cumulative Explained Variance': cumulative_explained_variance })
    content_html.append(utils.df_to_html_table(ev_df.round(3)))

    # Scree Plot
    plt.figure(figsize = (10, 6))
    plt.plot(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio, marker = 'o', linestyle = '--',
             label = 'Individual EVR')
    plt.plot(range(1, len(cumulative_explained_variance) + 1), cumulative_explained_variance, marker = 'o',
             linestyle = '-', label = 'Cumulative EVR')
    plt.title('Scree Plot - Explained Variance by Principal Components')
    plt.xlabel('Number of Principal Components')
    plt.ylabel('Explained Variance Ratio')
    plt.xticks(range(1, len(explained_variance_ratio) + 1))
    plt.legend()
    plt.grid(True)
    plot_filename_scree = "pca_scree_plot"
    utils.save_plot(plt.gcf(), plot_filename_scree, subdir = "pca")
    content_html.append(utils.plot_to_html_img(plot_filename_scree, subdir = "pca", alt_text = "PCA Scree Plot"))

    # Loadings (if interpretable number of components)
    if pca.n_components_ is not None and pca.n_components_ <= 10:  # Arbitrary limit for readability
        loadings = pd.DataFrame(pca.components_.T, columns = [f'PC{i + 1}' for i in range(pca.n_components_)],
                                index = df_numeric.columns)
        content_html.append(utils.df_to_html_table(loadings.round(3), title = "Component Loadings"))

        plt.figure(figsize = (12, max(6, len(df_numeric.columns) * 0.5)))  # Adjust size for many features
        sns.heatmap(loadings, annot = True, cmap = 'viridis', fmt = ".2f")
        plt.title('PCA Component Loadings')
        plot_filename_loadings = "pca_loadings_heatmap"
        utils.save_plot(plt.gcf(), plot_filename_loadings, subdir = "pca")
        content_html.append(
            utils.plot_to_html_img(plot_filename_loadings, subdir = "pca", alt_text = "PCA Loadings Heatmap"))

    # Create DataFrame of principal components
    pc_cols = [f'PC{i + 1}' for i in range(principal_components.shape[1])]
    pca_df = pd.DataFrame(data = principal_components, columns = pc_cols)
    utils.save_dataframe(pca_df, "principal_components", subdir = "pca")

    if report_parts is not None:
        utils.generate_html_report_section("Principal Component Analysis (PCA)", content_html, report_parts)

    print("PCA performed successfully.")
    return pca_df, pca