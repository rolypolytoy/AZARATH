import json
import os
import time
import pickle
from pathlib import Path
from tqdm import tqdm
from mp_api.client import MPRester
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import glob

API_KEY = "bPPHCDUmGEU3ijZ3lnG8FGRK7TKaZxZe"
DATA_DIR = Path("data")
BATCH_SIZE = 10000
MAX_WORKERS = 8
TARGET_FILES = 5000

deleted_count = 0

def cleanup_large_files():
    global deleted_count
    while True:
        try:
            pkl_files = list(Path(".").rglob("*.pkl"))
            for pkl_file in pkl_files:
                if pkl_file.exists():
                    file_size_mb = pkl_file.stat().st_size / (1024 * 1024)
                    if file_size_mb > 50:
                        print(f"Deleting large file: {pkl_file} ({file_size_mb:.1f} MB)")
                        pkl_file.unlink()
                        deleted_count += 1
        except Exception as e:
            print(f"Error in cleanup: {e}")
        
        time.sleep(60)

def start_cleanup_thread():
    cleanup_thread = threading.Thread(target=cleanup_large_files, daemon=True)
    cleanup_thread.start()
    return cleanup_thread

def setup_directories():
    DATA_DIR.mkdir(exist_ok=True)

def find_materials():
    with MPRester(API_KEY) as mpr:
        materials = mpr.materials.summary.search(
            has_props=["dos", "electronic_structure", "bandstructure"],
            fields=["material_id", "es_source_calc_id"]
        )
        material_data = [{"material_id": mat.material_id, "calc_id": mat.es_source_calc_id} for mat in materials]
    
    with open(DATA_DIR / "material_ids.json", "w") as f:
        json.dump(material_data, f)
    return material_data

def process_single_material(material_item):
    material_id = material_item["material_id"]
    calc_id = material_item["calc_id"]
    
    try:
        with MPRester(API_KEY) as mpr:
            material_dir = DATA_DIR / material_id
            material_dir.mkdir(exist_ok=True)
            
            summary_data = mpr.materials.summary.search(
                material_ids=[material_id],
                fields=["material_id", "structure", "band_gap", "dos", "efermi",
                        "bandstructure", "es_source_calc_id", "task_ids"]
            )[0]
            
            if summary_data.dos is None or summary_data.band_gap is None or summary_data.efermi is None or summary_data.bandstructure is None:
                return f"Skipped {material_id}: incomplete data"
            
            structure_file = material_dir / f"{material_id}.cif"
            summary_data.structure.to(filename=str(structure_file))
            
            try:
                full_dos = mpr.get_dos_by_material_id(material_id)
                full_bandstructure = mpr.get_bandstructure_by_material_id(material_id)
            except:
                full_dos = None
                full_bandstructure = None
            
            all_data = {
                "material_id": material_id,
                "band_gap": summary_data.band_gap,
                "efermi": summary_data.efermi,
                "summary_dos": summary_data.dos,
                "summary_bandstructure": summary_data.bandstructure,
                "full_dos": full_dos,
                "full_bandstructure": full_bandstructure,
                "es_source_calc_id": summary_data.es_source_calc_id,
                "task_ids": summary_data.task_ids
            }
            
            properties_file = material_dir / f"{material_id}.pkl"
            with open(properties_file, "wb") as f:
                pickle.dump(all_data, f)
                
            return f"Success: {material_id}"
            
    except Exception as e:
        return f"Failed {material_id}: {e}"

def download_batch(material_data_batch):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_material, item) for item in material_data_batch]
        
        for future in as_completed(futures):
            result = future.result()
            if "Failed" in result:
                print(result)

def download_all_materials(material_data):
    global deleted_count
    
    total_to_process = TARGET_FILES + deleted_count
    material_subset = material_data[:total_to_process]
    
    print(f"Processing {len(material_subset)} materials (target: {TARGET_FILES}, deleted: {deleted_count})")
    
    for i in tqdm(range(0, len(material_subset), BATCH_SIZE)):
        batch = material_subset[i:i + BATCH_SIZE]
        download_batch(batch)
        time.sleep(0.05)

def main():
    setup_directories()
    start_cleanup_thread()
    material_data = find_materials()
    download_all_materials(material_data)

if __name__ == "__main__":
    main()