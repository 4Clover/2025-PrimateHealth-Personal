import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk # treeview
# import seaborn as sns <- supposedly nicer plots, haven't touched it yet

########################################################################################################################
############################################ LOADING AND JOINING OF DATA ###############################################
########################################################################################################################

try:
    demographic = pd.read_excel("E:/primate_research/PFT_demographics.xlsx") # hard coded bc im lazy, ill fix later
    exposure = pd.read_excel("E:/primate_research/predictor_exposure.xlsx") # ''
    print("Data loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    print("Please ensure 'PFT_demographics.xlsx' and 'predictor_exposure.xlsx' "
          "are in the 'data' subdirectory. Script will now exit.")
    exit()

# joining the data, pandas default does like-column join
try:
    combined = pd.merge(demographic, exposure, how='left')
    print(f"Data joined successfully. Combined shape: {combined.shape}")
    # print("Columns after join:", combined.columns)
except Exception as e:
    print(f"Error during merge: {e}")
    print("Please check if the dataframes have common columns to join on (e.g., 'ID').")
    exit()

########################################################################################################################
################################################## DATA CLEANING #######################################################
########################################################################################################################

# remove unneeded columns
id_cols_to_drop = ["ID", "Sex", "StudyID"]

# check of existence
cols_present = [col for col in id_cols_to_drop if col in combined.columns]
if len(cols_present) < len(id_cols_to_drop):
    print(f"Warning: Not all specified ID columns ({id_cols_to_drop}) found in the combined data.")
    print(f"Dropping existing columns: {cols_present}")

# dropping the columns (first line of this section)
combined_no_ids = combined.drop(columns=cols_present)
print(f"ID columns ({cols_present}) removed.")

# selecting numeric values
combined_numeric = combined_no_ids.select_dtypes(include=np.number)

# reference prints
print(f"Selected numeric columns for scaling and PCA: {combined_numeric.columns.tolist()}")
print(f"Shape after selecting numeric columns: {combined_numeric.shape}")

########################################################################################################################
################################################ NaN HANDLING ##########################################################
########################################################################################################################

if combined_numeric.isnull().sum().sum() > 0:
    print(f"\nWarning: Found {combined_numeric.isnull().sum().sum()} NaN values in numeric data.")

    ####### USE 1 OR 2, NOT BOTH ######################################

    # our data does not have any NaNs so this is just for reference

    # 1.    drop NaNs - uncomment following 2 lines
    # combined_numeric = combined_numeric.dropna()
    # print(f"Rows with NaNs dropped. New shape: {combined_numeric.shape}")

    # 2.    impute NaNs with column means
    print("Imputing NaNs with column means.")
    combined_numeric = combined_numeric.fillna(combined_numeric.mean())

    ###################################################################

    # reference prints
    if combined_numeric.isnull().sum().sum() > 0:
        print("Warning: NaNs still present after mean imputation, please check.")
    else:
        print("NaNs imputed successfully.")
else:
    print("No NaN values found in numeric data.")

########################################################################################################################
############################################### DATA FIXING / PCA ######################################################
########################################################################################################################

original_feature_names = combined_numeric.columns.tolist() # names for plotting

# TODO:
# change shown names here for easier viewing, may reference soon to come README
# or a script that will parse the excel names into normal english

if combined_numeric.empty or combined_numeric.shape[1] == 0: # existence check for data
    print("\nError: No numeric data available for scaling and PCA after preprocessing.")
    exit()

# scale the data using StandardScaler, which I believe does what the R scale does (normalizing)
scaler = StandardScaler()
combined_scaled = scaler.fit_transform(combined_numeric)
print("\nData scaled successfully.")


#============================ PCA ================================#
pca = PCA(n_components=None) # 'None' means all components are kept

# apply PCA to the scaled data
pca.fit(combined_scaled)

# calc the principal component scores (the transformed data)
exposure_PCA_scores = pca.transform(combined_scaled)

# reference prints
print("PCA performed successfully.")
print(f"Number of components found: {pca.n_components_}")
#=================================================================#

########################################################################################################################
##################################################### PLOTTING #########################################################
########################################################################################################################

# scree plot to see how each component contributes to variance
plt.figure(figsize=(8, 5))
plt.plot(range(1, pca.n_components_ + 1), pca.explained_variance_ratio_, marker='o', linestyle='--')
plt.title('Scree Plot')
plt.xlabel('Principal Component')
plt.ylabel('Proportion of Variance Explained')
plt.xticks(range(1, pca.n_components_ + 1)) # ticks for each component
plt.grid(True)
plt.show()


#==================================================== BIPLOT ==========================================================#
# *** LLM GENERATED DOCS AND PORTIONS OF CODE ***

# (Shows data points projected onto the first two PCs, with arrows representing original variables)
def biplot(score, coeff, labels=None, pc_x_idx=0, pc_y_idx=1):
    """
    Creates a Biplot using matplotlib.

    Args:
        score (np.ndarray): PCA scores (transformed data), shape (n_samples, n_components)
        coeff (np.ndarray): PCA loadings (components), shape (n_components, n_features). NOTE: Transposed compared to some definitions.
        labels (list, optional): List of feature names for labeling the arrows. Defaults to None.
        pc_x_idx (int): Index of the principal component for the x-axis (default 0 for PC1).
        pc_y_idx (int): Index of the principal component for the y-axis (default 1 for PC2).
    """
    if score.shape[1] <= max(pc_x_idx, pc_y_idx): # input check
        print(f"Error: Not enough components ({score.shape[1]}) to plot PC{pc_x_idx+1} vs PC{pc_y_idx+1}.")
        return

    #####################################
    # TODO:
    # need to research exact methods here
    #####################################
    xs = score[:, pc_x_idx]
    ys = score[:, pc_y_idx]
    n_features = coeff.shape[1]
    scalex = 1.0 / (xs.max() - xs.min())
    scaley = 1.0 / (ys.max() - ys.min())
    #####################################

    fig, ax = plt.subplots(figsize=(12, 9)) # sizing of plot window

    # Plot Scores (observations)
    ax.scatter(xs * scalex, ys * scaley, s=15, alpha=0.5, label='Observations') # s=size

    # Plot Loadings (variables) as arrows
    # coeff[pc_x_idx, i] is the loading of feature i on PC indexed by pc_x_idx

    '''
    My understanding of the plots:
    
    We are looking at PC1 and PC2 because a large portion of the variance is due to those two components, so we can find trends "easily".
    This does not mean we don't need to or wont look at the other data.
    The dots scattered on the plot are where the data points land based on the new summary scores (the PCs).
    The arrows are how the original columns relate to these new summary scores.
    Short arrows mean low loading (effect) on the two PC's in question.
    Long mean they effect both a lot. 
    Positive direction for the arrows signals positive correlation, and vice versa. 
    This means an arrow that is positive makes the component group "occur more", i.e. if in a vacuum more of that variable would make more of that component.
    '''

    for i in range(n_features):
        ax.arrow(0, 0, coeff[pc_x_idx, i], coeff[pc_y_idx, i],
                 color='r', alpha=0.9, head_width=0.02)
        if labels is not None:
            ax.text(coeff[pc_x_idx, i] * 1.15, coeff[pc_y_idx, i] * 1.15,
                    labels[i], color='g', ha='center', va='center')

    ax.set_xlabel(f"PC{pc_x_idx+1} ({pca.explained_variance_ratio_[pc_x_idx]*100:.2f}%)")
    ax.set_ylabel(f"PC{pc_y_idx+1} ({pca.explained_variance_ratio_[pc_y_idx]*100:.2f}%)")
    ax.set_title("Biplot")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.axhline(0, color='grey', lw=0.5)
    ax.axvline(0, color='grey', lw=0.5)
    ax.legend()
    plt.show()

########################################################################################################################

# Create the biplot using the scores and loadings (components_)
# pca.components_ has shape (n_components, n_features)
print("\nGenerating Biplot (PC1 vs PC2)...")
biplot(exposure_PCA_scores, pca.components_, labels=original_feature_names, pc_x_idx=0, pc_y_idx=1)
print("Biplot generated successfully.")

########################################################################################################################
###################################################### PARSING? ########################################################
########################################################################################################################

# ranking and tabulation function to determine top variables for each component
def get_top_pca_loadings_data(pca_model, feature_names, num_components=3, num_features=5):
    """
    Analyzes PCA loadings to find top contributing variables for each component.

    Args:
        pca_model (sklearn.decomposition.PCA): The fitted PCA object.
        feature_names (list): List of original feature names corresponding to PCA input columns.
        num_components (int): How many principal components to analyze (e.g., 3 for PC1, PC2, PC3).
        num_features (int): How many top contributing features to show for each component.

    Returns:
        list: A list of tuples, where each tuple contains:
              (component_index + 1, rank, feature_name, loading_value, explained_variance_ratio)
              Suitable for populating a table.
        str: A formatted string summarizing the results (alternative output).
    """
    loadings = pca_model.components_
    explained_variance = pca_model.explained_variance_ratio_
    num_actual_components = loadings.shape[0]
    num_components_to_show = min(num_components, num_actual_components)

    output_data = []
    summary_string = "PCA Loading Analysis:\n"
    summary_string += "=" * 30 + "\n"

    for i in range(num_components_to_show):
        component_loadings = loadings[i, :]
        component_variance = explained_variance[i]
        summary_string += (f"\n--- Principal Component {i+1} "
                           f"(Explains {component_variance*100:.2f}% variance) ---\n")

        # loading indices sorted by absolute value, descending
        sorted_indices = np.argsort(np.abs(component_loadings))[::-1]

        summary_string += f"Top {num_features} Contributing Variables:\n"
        rank = 1
        for j in sorted_indices[:num_features]:
            feature_name = feature_names[j]
            loading_value = component_loadings[j]
            summary_string += f"  {rank}. {feature_name}: {loading_value:.4f}\n"
            # Append data for the table
            output_data.append((i + 1, rank, feature_name, loading_value, component_variance))
            rank += 1
        summary_string += "-" * 30 + "\n"


    return output_data, summary_string

########################################################################################################################
############################################# DESKTOP WINDOW CODE ######################################################
########################################################################################################################

def display_loadings_popup_table(data, title="Top PCA Loadings"):
    """
    Displays PCA loading data in a sortable Tkinter popup table.

    Args:
        data (list): List of tuples from get_top_pca_loadings_data.
                     Each tuple: (Component, Rank, Variable, Loading, Variance Explained)
        title (str): The title for the popup window.
    """
    if not data: # error check
        print("No data provided to display in popup.")
        return

    root = tk.Tk()
    root.title(title)
    # window sizing
    root.geometry("650x400")

    # treeview frame
    tree_frame = ttk.Frame(root, padding="10")
    tree_frame.pack(expand=True, fill='both')

    # scrollbar
    tree_scroll_y = ttk.Scrollbar(tree_frame)
    tree_scroll_y.pack(side='right', fill='y')
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side='bottom', fill='x')


    # treeview (table library)
    columns = ("Component", "Rank", "Variable", "Loading", "Component Variance")
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                        yscrollcommand=tree_scroll_y.set,
                        xscrollcommand=tree_scroll_x.set)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # table headings
    tree.heading("Component", text="PC", anchor='center')
    tree.heading("Rank", text="Rank", anchor='center')
    tree.heading("Variable", text="Variable Name", anchor='w') # West align text
    tree.heading("Loading", text="Loading", anchor='e') # East align numbers
    tree.heading("Component Variance", text="PC Variance (%)", anchor='e')

    # formatting columns
    tree.column("Component", anchor='center', width=50, stretch=tk.NO)
    tree.column("Rank", anchor='center', width=50, stretch=tk.NO)
    tree.column("Variable", anchor='w', width=250)
    tree.column("Loading", anchor='e', width=100)
    tree.column("Component Variance", anchor='e', width=120)

    def sort_column(tv, col, reverse):
        try:
            # float conversion for sorting, fallback is string
            l = [(float(tv.set(k, col)), k) for k in tv.get_children('')]
        except ValueError:
            l = [(tv.set(k, col).lower(), k) for k in tv.get_children('')] # case-insensitive '.lower'
        l.sort(reverse=reverse)

        # apply sort
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        # reverse the ordering
        tv.heading(col, command=lambda: sort_column(tv, col, not reverse))

    # header can be clicked to sort by column
    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))


    # input of data to table
    for item in data:
        pc_num, rank, var_name, loading, variance = item

        # variance and loading formatting (display only)
        formatted_loading = f"{loading:.4f}"
        formatted_variance = f"{variance*100:.2f}%"

        tree.insert("", tk.END, values=(pc_num, rank, var_name, formatted_loading, formatted_variance))

    # window thing so the scroll bar is usable
    tree.pack(expand=True, fill='both')

    # self-explanatory
    close_button = ttk.Button(root, text="Close", command=root.destroy)
    close_button.pack(pady=10)

    # center the window on the screen
    root.update_idletasks() # obligatory update for OS
    width = root.winfo_width() # window size var 1
    height = root.winfo_height() # window size var 2
    x = (root.winfo_screenwidth() // 2) - (width // 2) # position of popup
    y = (root.winfo_screenheight() // 2) - (height // 2) # position of popup
    root.geometry(f'{width}x{height}+{x}+{y}') # apply previous variables


    # and bobs your uncle! i.e., run the desktop window
    root.mainloop()

########################################################################################################################
############################################## DATA VISUALIZATION ######################################################
########################################################################################################################

if 'pca' in locals() and 'original_feature_names' in locals(): # data presence / asynchronous check
    print("\nAnalyzing PCA loadings...")

    # using the above function to now express the PCA graph in tablular form
    loading_data, summary_text = get_top_pca_loadings_data(
        pca_model=pca,
        feature_names=original_feature_names,
        num_components=3,  # PC1, PC2, PC3
        num_features=10   # top 10 variables
    )

    # Console print of the summary
    print("\n--- PCA Loadings Summary (Console Output) ---")
    print(summary_text)

    # Popup table version of the summary
    print("\nAttempting to display results in a popup window...")
    try:
        display_loadings_popup_table(loading_data, title="Top PCA Contributing Variables")
        print("Popup window closed.")
    except Exception as e:
        print(f"Could not display Tkinter popup window: {e}")
        print("Install tkinter if missing, or check your environment for GUI support.")

else:
    print("\nError: 'pca' object or 'original_feature_names' not found.")
    print("Please ensure the PCA part of the script ran successfully.")

print("\nScript finished.")

########################################################################################################################
########################################################################################################################
########################################################################################################################

''' 
Thoughts on covariance.

I think the variables in PC1 covary since the top 10 variables seem to have early life in common, 
so it stands to reason the inadequate or even amazing numbers (individual monkey) that were recorded 
either point to a strong genetic effect of these interactions or super large doses were experienced. 
It is interesting to note that NO2 and O3 are the two gases present, which either means they consequentially are produced and absorbed at the same rate.
I am struggling somewhat to make sense of this without comparing it to a direct physical reaction by the monkey, i.e. asthma or jumping around. 
Its hard to intuit any of this without a real world reference of the animals and whatnot. 


'''