# prediction_script.py (Simplified Test)
import sys
import os
import import_ipynb 
# ... (Your logic to set NOTEBOOK_DIR) ...

# Check the file existence immediately after modifying sys.path
NOTEBOOK_FILENAME = 'breast_cancer_mlp.ipynb' # Ensure this matches your filename

# This will only work if NOTEBOOK_DIR is the current directory OR on sys.path
# Let's check with the absolute path for maximum reliability:
FULL_NOTEBOOK_PATH = os.path.join(os.path.dirname(__file__), NOTEBOOK_FILENAME)

if not os.path.exists(FULL_NOTEBOOK_PATH):
    print(f"🚨 ERROR: The file was not found at the calculated location: {FULL_NOTEBOOK_PATH}")
    sys.exit(1)

# If the file exists, the import should proceed if the notebook is error-free.
try:
    import breast_cancer_mlp 
    print("SUCCESS: Notebook imported!")
    # ... continue ...
except Exception as e:
    # This captures the runtime error (often an ImportError wrapping another exception)
    print(f"🚨 FATAL ERROR DURING NOTEBOOK EXECUTION: {e}")
    print("The notebook executed code that failed. Rerun 'Run All' inside the .ipynb to find the error.")