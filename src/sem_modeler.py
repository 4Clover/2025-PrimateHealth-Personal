import pandas as pd
import semopy
from src import utils, config
import os  # for graphviz path if needed


def define_sem_model_spec(model_description_string):
    """
    Takes a model description string in semopy format.
    Example:
    model_spec = '''
        # measurement model
        eta1 =~ y1 + y2 + y3
        eta2 =~ y4 + y5 + y6
        # structural model
        eta1 ~ xi1 + xi2
        eta2 ~ eta1
        # residual correlations (optional)
        y1 ~~ y2
    '''
    """
    return model_description_string


def fit_sem_model(df, model_spec, report_parts = None):
    """Fits an SEM model using semopy."""
    if df is None or df.empty:
        print("Cannot fit SEM: DataFrame is None or empty.")
        return None
    if not model_spec:
        print("Cannot fit SEM: Model specification is empty.")
        return None

    content_html = []
    try:
        model = semopy.Model(model_spec)
        # Ensure all variables in model_spec are in df columns
        model_vars = model.vars['observed'] | model.vars['latent']
        for var in model.vars['observed']:  # Only observed vars need to be in df
            if var not in df.columns:
                msg = f"Error: Variable '{var}' from model specification not found in DataFrame columns."
                print(msg)
                content_html.append(f"<p>{msg}</p>")
                if report_parts is not None:
                    utils.generate_html_report_section("Structural Equation Modeling (SEM)", content_html, report_parts)
                return None

        # Optimization can sometimes fail, especially with complex models or small N
        # You might need to try different optimizers or starting values
        # common optimizers: 'SLSQP' (default), 'COBYLA', 'trust-constr'
        results = model.fit(data = df, obj = 'MLW')  # MLW is common for continuous data

        # Inspect results
        stats = semopy.calc_stats(model)
        content_html.append(utils.df_to_html_table(stats.round(3), title = "SEM Fit Statistics"))

        estimates = model.inspect()
        content_html.append(utils.df_to_html_table(estimates.round(3), title = "SEM Parameter Estimates"))

        # Visualization (requires Graphviz)
        try:
            img_filename = "sem_model_diagram"
            g = semopy.semplot(model, os.path.join(config.IMAGE_DIR, "sem", f"{img_filename}.png"), plot_covs = True)
            # Also save to Vercel assets
            semopy.semplot(model, os.path.join(config.VERCEL_ASSETS_DIR, "sem", f"{img_filename}.png"),
                           plot_covs = True)

            content_html.append(utils.plot_to_html_img(img_filename, subdir = "sem", alt_text = "SEM Model Diagram"))
            print(f"SEM diagram saved to {config.IMAGE_DIR}/sem/{img_filename}.png and for Vercel.")
        except Exception as e:
            err_msg = f"Could not generate SEM plot. Ensure Graphviz is installed and in PATH. Error: {e}"
            print(err_msg)
            content_html.append(f"<p>{err_msg}</p>")

        if report_parts is not None:
            utils.generate_html_report_section("Structural Equation Modeling (SEM)", content_html, report_parts)

        print("SEM model fitted successfully.")
        return model, results, stats

    except Exception as e:
        error_msg = f"Error fitting SEM model: {e}"
        print(error_msg)
        content_html.append(f"<p>{error_msg}</p>")
        if report_parts is not None:
            utils.generate_html_report_section("Structural Equation Modeling (SEM)", content_html, report_parts)
        return None, None, None