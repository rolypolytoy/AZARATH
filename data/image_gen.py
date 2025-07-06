import glob
import subprocess
import shutil
from pathlib import Path
import time
import os

def generate_all_images():
    start_time = time.time()
    
    gnuplot_files = glob.glob("data/*/*.gnuplot")
    total_files = len(gnuplot_files)
    
    print(f"Found {total_files} gnuplot files to process")
    
    if not shutil.which("gnuplot"):
        print("Error: gnuplot not found. Install it first.")
        return
    
    processed = 0
    for gnuplot_file in gnuplot_files:
        try:
            generate_image(gnuplot_file)
            processed += 1
            if processed % 50 == 0:
                print(f"Processed {processed}/{total_files} files")
        except Exception as e:
            print(f"Error processing {gnuplot_file}: {e}")
    
    end_time = time.time()
    print(f"Generated {processed} images in {end_time - start_time:.3f} seconds")

def generate_image(gnuplot_file):
    gnuplot_path = Path(gnuplot_file)
    material_dir = gnuplot_path.parent
    original_dir = Path.cwd()
    
    os.chdir(material_dir)
    subprocess.run(["gnuplot", gnuplot_path.name], check=True)
    os.chdir(original_dir)

if __name__ == "__main__":
    generate_all_images()