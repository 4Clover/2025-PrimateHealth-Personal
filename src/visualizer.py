import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src import utils, config  # Assuming utils has save_plot
import os


def plot_cca_biplot(cca_model, x_df_original_names, y_df_original_names,
                    x_scores, y_scores,
                    axes_pair = (0, 1),  # CCA components (0-indexed) e.g. (0,1) for CanAxis1 vs CanAxis2
                    report_parts = None, plot_title_prefix = "CCA_Biplot"):
    """
    Generates and saves a CCA biplot similar to R's vegan::biplot output.
    Args:
        cca_model: The fitted scikit-learn CCA object.
        x_df_original_names (list): Column names of the original X variables.
        y_df_original_names (list): Column names of the original Y variables.
        x_scores (pd.DataFrame): Canonical variates for X (samples x n_components).
        y_scores (pd.DataFrame): Canonical variates for Y (samples x n_components).
        axes_pair (tuple): Tuple indicating which two canonical axes to plot (e.g., (0, 1) for 1st and 2nd).
        report_parts (list): List to append HTML for the report.
        plot_title_prefix (str): Prefix for plot filenames and titles.
    """
    if cca_model is None or x_scores is None or y_scores is None:
        print("CCA model or scores are None, cannot generate biplot.")
        if report_parts is not None:
            utils.generate_html_report_section(
                f"{plot_title_prefix} (Axes {axes_pair[0] + 1} vs {axes_pair[1] + 1})",
                ["<p>CCA model or scores not available for biplot.</p>"],
                report_parts
            )
        return

    ax1_idx, ax2_idx = axes_pair
    if ax1_idx >= cca_model.n_components or ax2_idx >= cca_model.n_components:
        msg = f"Error: Requested axes ({ax1_idx + 1}, {ax2_idx + 1}) out of bounds for {cca_model.n_components} components."
        print(msg)
        if report_parts is not None:
            utils.generate_html_report_section(
                f"{plot_title_prefix} (Axes {axes_pair[0] + 1} vs {axes_pair[1] + 1})",
                [f"<p>{msg}</p>"],
                report_parts
            )
        return

    x_loadings = cca_model.x_loadings_
    y_loadings = cca_model.y_loadings_

    fig, axs = plt.subplots(2, 2, figsize = (15, 15))
    fig.suptitle(f'{plot_title_prefix}: Canonical Axes {ax1_idx + 1} and {ax2_idx + 1}', fontsize = 16, y = 0.95)

    # Top-left: Y Scores (Response Samples)
    axs[0, 0].scatter(y_scores.iloc[:, ax1_idx], y_scores.iloc[:, ax2_idx], c = 'red', alpha = 0.7, edgecolors = 'k',
                      s = 30)
    axs[0, 0].set_xlabel(f'Response CanAxis {ax1_idx + 1}')
    axs[0, 0].set_ylabel(f'Response CanAxis {ax2_idx + 1}')
    axs[0, 0].set_title('Response Data (Y) Scores')
    axs[0, 0].axhline(0, color = 'black', lw = 0.5)
    axs[0, 0].axvline(0, color = 'black', lw = 0.5)
    axs[0, 0].grid(True, linestyle = '--', alpha = 0.7)

    # Top-right: X Scores (Exposure Samples)
    axs[0, 1].scatter(x_scores.iloc[:, ax1_idx], x_scores.iloc[:, ax2_idx], c = 'blue', alpha = 0.7, edgecolors = 'k',
                      s = 30)
    axs[0, 1].set_xlabel(f'Exposure CanAxis {ax1_idx + 1}')
    axs[0, 1].set_ylabel(f'Exposure CanAxis {ax2_idx + 1}')
    axs[0, 1].set_title('Exposure Data (X) Scores')
    axs[0, 1].axhline(0, color = 'black', lw = 0.5)
    axs[0, 1].axvline(0, color = 'black', lw = 0.5)
    axs[0, 1].grid(True, linestyle = '--', alpha = 0.7)

    # Helper for loading plots
    def plot_loadings_arrows(ax, loadings, names, color, title, can_axis1_idx, can_axis2_idx):
        for i, name in enumerate(names):
            ax.arrow(0, 0, loadings[i, can_axis1_idx], loadings[i, can_axis2_idx],
                     head_width = 0.03, head_length = 0.05, fc = color, ec = color, length_includes_head = True)
            ax.text(loadings[i, can_axis1_idx] * 1.1, loadings[i, can_axis2_idx] * 1.1,
                    name, color = color, ha = 'center', va = 'center', fontsize = 8)
        ax.set_xlabel(f'CanAxis {can_axis1_idx + 1} Loadings')
        ax.set_ylabel(f'CanAxis {can_axis2_idx + 1} Loadings')
        ax.set_title(title)
        ax.axhline(0, color = 'black', lw = 0.5)
        ax.axvline(0, color = 'black', lw = 0.5)
        # Add correlation circles (simplified)
        lim = np.max(np.abs(loadings[:, [can_axis1_idx, can_axis2_idx]])) * 1.1
        ax.set_xlim([-lim, lim])
        ax.set_ylim([-lim, lim])
        circle1 = plt.Circle((0, 0), 0.5, color = 'gray', fill = False, linestyle = '--')
        circle2 = plt.Circle((0, 0), 1.0, color = 'black', fill = False, linestyle = '-')
        ax.add_artist(circle1)
        ax.add_artist(circle2)
        ax.set_aspect('equal', adjustable = 'box')  # Keep circles circular
        ax.grid(True, linestyle = '--', alpha = 0.7)

    # Bottom-left: Y Loadings (Response Variables)
    plot_loadings_arrows(axs[1, 0], y_loadings, y_df_original_names, 'red', 'Response Variable Loadings', ax1_idx,
                         ax2_idx)

    # Bottom-right: X Loadings (Exposure Variables)
    plot_loadings_arrows(axs[1, 1], x_loadings, x_df_original_names, 'blue', 'Exposure Variable Loadings', ax1_idx,
                         ax2_idx)

    rect_temp : tuple[float, float, float, float] = (0.0, 0.0, 1.0, 0.93)
    plt.tight_layout(rect=rect_temp)  # Adjust for suptitle

    plot_filename_base = f"{plot_title_prefix}_Axes_{ax1_idx + 1}v{ax2_idx + 1}"
    utils.save_plot(fig, plot_filename_base, subdir = "cca/biplots")

    if report_parts is not None:
        html_content = [utils.plot_to_html_img(plot_filename_base, subdir = "cca/biplots",
                                               alt_text = f"CCA Biplot Axes {ax1_idx + 1} vs {ax2_idx + 1}")]
        utils.generate_html_report_section(
            f"CCA Biplot: {plot_title_prefix} (Axes {ax1_idx + 1} vs {ax2_idx + 1})",
            html_content,
            report_parts
        )
    plt.close(fig)  # ensure figure is closed