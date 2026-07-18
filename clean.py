import shutil
from pathlib import Path

def flatten_directory(target_path):
    # Convert string path to a Path object
    root = Path(target_path).resolve()
    
    # Iterate through every item inside the subdirectories
    # rglob("*") finds everything recursively
    for item in root.rglob("*"):
        
        # Skip if the item is already in the root directory 
        # (we don't want to move a file into itself)
        if item.parent == root:
            continue
            
        # Define the new path in the outermost directory
        destination = root.parent / item.name
        
        # Check if it already exists in the destination
        if destination.exists():
            # Since you mentioned overlaps are identical, we just skip
            print(f"Skipping {item.name}: already exists in root.")
            continue

        is_csv = item.is_file() and item.suffix.lower() == ".csv"
        is_dir = item.is_dir()

        if item.name != "experiment_params.json":
            if not item.name[0].isdigit():
                continue
            
            if not (is_csv or is_dir):
                continue
        
        try:
            # Move the file or directory
            shutil.move(str(item), str(destination))
            print(f"Moved: {item.name}")
        except Exception as e:
            print(f"Error moving {item.name}: {e}")

    # Optional: Clean up empty subdirectories
    # for folder in root.iterdir():
    #     if folder.is_dir() and not any(folder.iterdir()):
    #         folder.rmdir()
    #         print(f"Removed empty folder: {folder.name}")

if __name__ == "__main__":
    # Change 'your_directory_here' to the path of your main folder
    parent = "/Users/tapaswinikodavanti/Desktop/Research/neurorule-syn-0.95/0.95/"
    # parent = "/Users/tapaswinikodavanti/Desktop/Research/neurorule-data-12/baseline-solutions/ID/0.80/"

    for i in range(1, 8):
        # directory = f"baseline-solutions/ID+synthetic/0.80/{i}/uci_diabetes_test"
        directory = f"{i}/uci_diabetes_test"
        flatten_directory(f"{parent}{directory}")