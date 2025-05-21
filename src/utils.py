import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from src import config

def save_plot(fig, filename_base, subdir=""):
    """Saves a matplotlib figure to the configured image directory."""
    save_dir = os.path.join(config.IMAGE_DIR, subdir)
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, f"{filename_base}.png")
    fig.savefig(filepath, bbox_inches='tight')
    print(f"Plot saved to {filepath}")
    plt.close(fig)

    # save for Vercel site
    vercel_save_dir = os.path.join(config.VERCEL_ASSETS_DIR, subdir)
    os.makedirs(vercel_save_dir, exist_ok=True)
    vercel_filepath = os.path.join(vercel_save_dir, f"{filename_base}.png")
    fig.savefig(vercel_filepath, bbox_inches='tight')
    print(f"Plot also saved for Vercel to {vercel_filepath}")
    plt.close(fig)


def save_dataframe(df, filename_base, subdir=""):
    """Saves a pandas DataFrame to CSV in the processed_data directory."""
    save_dir = os.path.join(config.PROCESSED_DATA_DIR, subdir)
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, f"{filename_base}.csv")
    df.to_csv(filepath, index=False)
    print(f"DataFrame saved to {filepath}")

    # save for Vercel site -- loaded via JS
    vercel_save_dir = os.path.join(config.VERCEL_ASSETS_DIR, subdir)
    os.makedirs(vercel_save_dir, exist_ok=True)
    vercel_filepath = os.path.join(vercel_save_dir, f"{filename_base}.csv")
    df.to_csv(vercel_filepath, index=False)
    print(f"DataFrame also saved for Vercel to {vercel_filepath}")

def generate_html_report_section(title, content_html_list, report_parts):
    """Appends a section to a list of HTML parts for the final report."""
    section_html = f"<h2>{title}</h2>\n"
    for content in content_html_list:
        section_html += f"<div>{content}</div>\n"
    report_parts.append(section_html)

def df_to_html_table(df, title=""):
    """Converts a Pandas DataFrame to an HTML table string."""
    html = ""
    if title:
        html += f"<h3>{title}</h3>"
    html += df.to_html(classes='table table-striped', border=0, na_rep='-')
    return html

def plot_to_html_img(filename_base, subdir="", alt_text="Plot"):
    """Generates an HTML img tag for a saved plot via relative pathing of the Vercel dir."""
    # vercel_public/index.html -> assets/subdir/filename.png
    relative_path = f"assets/{subdir}/{filename_base}.png" if subdir else f"assets/{filename_base}.png"
    return f'<img src="{relative_path}" alt="{alt_text}" style="max-width:100%; height:auto;">'