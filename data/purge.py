import os
from pathlib import Path

def purge(directory: str = "properties"):
    if not os.path.exists(directory):
        print(f"Directory {directory} not found")
        return
    
    pkl_files = [f for f in os.listdir(directory) if f.endswith('.pkl')]
    total_files = len(pkl_files)
    
    if total_files == 0:
        print("No .pkl files found")
        return
    
    print(f"Found {total_files} .pkl files in {directory}")
    
    confirm = input(f"Delete all {total_files} .pkl files? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    deleted_count = 0
    error_count = 0
    
    for pkl_file in pkl_files:
        filepath = os.path.join(directory, pkl_file)
        try:
            os.remove(filepath)
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting {pkl_file}: {e}")
            error_count += 1
    
    print(f"Deleted: {deleted_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    purge()