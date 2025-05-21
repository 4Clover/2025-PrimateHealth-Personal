import os

# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
PROCESSED_DATA_DIR = os.path.join(OUTPUT_DIR, "processed_data")
VERCEL_PUBLIC_DIR = os.path.join(BASE_DIR, "vercel_public")
VERCEL_ASSETS_DIR = os.path.join(VERCEL_PUBLIC_DIR, "assets")


# ---- Analysis Parameters ----
PCA_N_COMPONENTS = 5
# TARGET_VARIABLE = 'response' # If applicable for some analyses

# --- Check that output directories exist ---
def create_output_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(VERCEL_PUBLIC_DIR, exist_ok=True)
    os.makedirs(VERCEL_ASSETS_DIR, exist_ok=True)
