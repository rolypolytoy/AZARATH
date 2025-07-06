import json
import os
import time
import pickle
from pathlib import Path
from tqdm import tqdm
from mp_api.client import MPRester

API_KEY = "bPPHCDUmGEU3ijZ3lnG8FGRK7TKaZxZe"
DATA_DIR = Path("data")
BATCH_SIZE = 1000

def setup_directories():
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "structures").mkdir(exist_ok=True)
    (DATA_DIR / "properties").mkdir(exist_ok=True)

def find_materials():
    with MPRester(API_KEY) as mpr:
        materials = mpr.materials.summary.search(
            has_props=["dos", "electronic_structure", "bandstructure"],
            fields=["material_id"]
        )
        material_ids = [mat.material_id for mat in materials]
    
    with open(DATA_DIR / "material_ids.json", "w") as f:
        json.dump(material_ids, f)
    
    return material_ids

def download_batch(material_ids_batch):
    with MPRester(API_KEY) as mpr:
        materials = mpr.materials.summary.search(
            material_ids=material_ids_batch,
            fields=["material_id", "structure", "band_gap", "dos", "efermi", 
                   "bandstructure", "es_source_calc_id", "task_ids"]
        )
        
        for mat in materials:
            if mat.dos is None or mat.band_gap is None or mat.efermi is None or mat.bandstructure is None:
                continue
                
            structure_file = DATA_DIR / "structures" / f"{mat.material_id}.cif"
            mat.structure.to(filename=str(structure_file))
            
            properties = {
                "material_id": mat.material_id,
                "band_gap": mat.band_gap,
                "efermi": mat.efermi,
                "dos": mat.dos,
                "bandstructure": mat.bandstructure,
                "es_source_calc_id": mat.es_source_calc_id,
                "task_ids": mat.task_ids
            }
            
            properties_file = DATA_DIR / "properties" / f"{mat.material_id}.pkl"
            with open(properties_file, "wb") as f:
                pickle.dump(properties, f)

def download_all_materials(material_ids):
    for i in tqdm(range(0, len(material_ids), BATCH_SIZE)):
        batch = material_ids[i:i + BATCH_SIZE]
        download_batch(batch)
        time.sleep(0.1)

def main():
    setup_directories()
    material_ids = find_materials()
    download_all_materials(material_ids)

if __name__ == "__main__":
    main()