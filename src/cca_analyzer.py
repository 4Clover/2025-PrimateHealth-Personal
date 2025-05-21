import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import CCA
import matplotlib.pyplot as plt
from src import utils, config


def perform_cca(x_df, y_df, n_components=None, report_parts=None, max_iter=1000, tol=1e-06): # Added max_iter, tol
    """
    Performs Canonical Correlation Analysis (CCA) between two sets of variables.
    X_df: DataFrame for the first set of variables.
    Y_df: DataFrame for the second set of variables.
    n_components: Number of canonical components to extract.
    max_iter: Maximum number of iterations for the PLS algorithm.
    tol: Tolerance for convergence.
    """
    if x_df is None or y_df is None or x_df.empty or y_df.empty:
        print("Cannot perform CCA: One or both input DataFrames are None or empty.")
        return None, None

    if len(x_df) != len(y_df):
        print("CCA Error: Input DataFrames X and Y must have the same number of rows.")
        return None, None

    content_html = []

    # Standardize the data (important for CCA)
    scaler_x = StandardScaler()
    x_scaled = scaler_x.fit_transform(x_df)

    scaler_y = StandardScaler()
    y_scaled = scaler_y.fit_transform(y_df)

    # Determine n_components if not specified (min of features in X or Y)
    if n_components is None:
        n_components = min(x_scaled.shape[1], y_scaled.shape[1])

    # Perform CCA
    cca = CCA(n_components=n_components, max_iter=max_iter, tol=tol)
    try:
        cca.fit(x_scaled, y_scaled)
    except Exception as e:
        print(f"Error during CCA fitting: {e}")
        content_html.append(
            f"<p>Error during CCA fitting: {e}. CCA might not be suitable if one variable set perfectly predicts the other, or if variables are collinear.</p>")
        if report_parts is not None:
            utils.generate_html_report_section("Canonical Correlation Analysis (CCA)", content_html, report_parts)
        return None, None

    # Get canonical variates (scores)
    x_c, y_c = cca.transform(x_scaled, y_scaled)  # These are the canonical variates

    # Canonical Correlations
    # Sklearn's CCA doesn't directly give correlations, but we can compute them
    # from the transformed variates.
    # Or, an alternative way if you want to calculate manually (more complex):
    # U = x_c, V = y_c. Canonical correlations are corr(U_i, V_i)
    correlations = []
    for i in range(n_components):
        # Ensure x_c and y_c are 2D, even if only one component
        u_i = x_c[:, i] if x_c.ndim > 1 else x_c
        v_i = y_c[:, i] if y_c.ndim > 1 else y_c
        corr = np.corrcoef(u_i, v_i)[0, 1]
        correlations.append(corr)

    correlations_df = pd.DataFrame({ 'Canonical Component': range(1, n_components + 1), 'Correlation': correlations })
    content_html.append(utils.df_to_html_table(correlations_df.round(3), title = "Canonical Correlations"))

    # Plot Canonical Correlations
    plt.figure(figsize = (8, 5))
    plt.bar(range(1, n_components + 1), correlations, color = 'skyblue')
    plt.title('Canonical Correlations')
    plt.xlabel('Canonical Variate Pair')
    plt.ylabel('Correlation Coefficient')
    plt.xticks(range(1, n_components + 1))
    plt.ylim(0, 1.1)  # Correlations are between 0 and 1
    for i, v in enumerate(correlations):
        plt.text(i + 1, v + 0.02, f"{v:.3f}", ha = 'center', va = 'bottom')
    plot_filename_cca_corrs = "cca_correlations"
    utils.save_plot(plt.gcf(), plot_filename_cca_corrs, subdir = "cca")
    content_html.append(utils.plot_to_html_img(plot_filename_cca_corrs, subdir = "cca", alt_text = "CCA Correlations"))

    # Canonical Loadings (weights)
    # x_loadings are how original X variables relate to X's canonical variates
    # y_loadings are how original Y variables relate to Y's canonical variates
    x_loadings = pd.DataFrame(cca.x_loadings_, index = x_df.columns,
                              columns = [f'X_CV{i + 1}' for i in range(n_components)])
    y_loadings = pd.DataFrame(cca.y_loadings_, index = y_df.columns,
                              columns = [f'Y_CV{i + 1}' for i in range(n_components)])

    content_html.append(
        utils.df_to_html_table(x_loadings.round(3), title = "X Variables Loadings on X Canonical Variates"))
    content_html.append(
        utils.df_to_html_table(y_loadings.round(3), title = "Y Variables Loadings on Y Canonical Variates"))

    # Storing transformed data (canonical variates)
    x_c_df = pd.DataFrame(x_c, columns = [f'X_CV{i + 1}' for i in range(n_components)])
    y_c_df = pd.DataFrame(y_c, columns = [f'Y_CV{i + 1}' for i in range(n_components)])
    utils.save_dataframe(x_c_df, "cca_X_canonical_variates", subdir = "cca")
    utils.save_dataframe(y_c_df, "cca_Y_canonical_variates", subdir = "cca")

    if report_parts is not None:
        utils.generate_html_report_section("Canonical Correlation Analysis (CCA)", content_html, report_parts)

    print(f"CCA performed (or attempted) with n_components={cca.n_components}, max_iter={max_iter}.")
    return cca, (x_c_df, y_c_df)