import pickle
import numpy as np
from pathlib import Path
import time
import os
import glob

def process_all_materials():
    start_time = time.time()
    
    pkl_files = glob.glob("data/*/mp-*.pkl")
    total_files = len(pkl_files)
    
    print(f"Found {total_files} pickle files to process")
    
    processed = 0
    for pkl_file in pkl_files:
        try:
            analyze_material(pkl_file)
            processed += 1
            if processed % 100 == 0:
                print(f"Processed {processed}/{total_files} files")
        except Exception as e:
            print(f"Error processing {pkl_file}: {e}")
    
    end_time = time.time()
    print(f"Processed {processed} materials in {end_time - start_time:.3f} seconds")

def analyze_material(file_path):
    material_id = Path(file_path).stem
    
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    
    if data['full_dos'] is None or data['full_bandstructure'] is None:
        return
    
    dos = data['full_dos']
    bs = data['full_bandstructure']
    
    write_text_summary(data, material_id)
    write_gnuplot_files(dos, bs, material_id)
    
    os.remove(file_path)

def write_text_summary(data, material_id):
    material_dir = Path(f"data/{material_id}")
    with open(material_dir / f"{material_id}.txt", "w") as f:
        f.write(f"Material: {material_id}\n")
        f.write("="*50 + "\n\n")
        f.write(f"Band Gap: {data['band_gap']:.4f} eV\n")
        f.write(f"Fermi Energy: {data['efermi']:.4f} eV\n")
        f.write(f"Is Metal: {data['full_bandstructure'].is_metal()}\n\n")
        
        dos = data['full_dos']
        f.write("DOS Information:\n")
        f.write(f"  Energy points: {len(dos.energies)}\n")
        f.write(f"  Energy range: {dos.energies.min():.2f} to {dos.energies.max():.2f} eV\n")
        f.write(f"  Fermi energy (DOS): {dos.efermi:.4f} eV\n")
        f.write(f"  Spin channels: {len(dos.densities)}\n\n")
        
        bs = data['full_bandstructure']
        f.write("Band Structure Information:\n")
        f.write(f"  K-points: {len(bs.kpoints)}\n")
        f.write(f"  Bands: {bs.nb_bands}\n")
        f.write(f"  Fermi energy (BS): {bs.efermi:.4f} eV\n")
        f.write(f"  Spin channels: {len(bs.bands)}\n")
        f.write(f"  High symmetry points: {list(bs.labels_dict.keys())}\n")
        
        try:
            cbm = bs.get_cbm()
            vbm = bs.get_vbm()
            f.write(f"\nBand edges:\n")
            if vbm and 'energy' in vbm:
                f.write(f"  VBM: {vbm['energy']:.4f} eV\n")
            else:
                f.write(f"  VBM: N/A\n")
            if cbm and 'energy' in cbm:
                f.write(f"  CBM: {cbm['energy']:.4f} eV\n")
            else:
                f.write(f"  CBM: N/A\n")
            
            try:
                direct_gap = bs.get_direct_band_gap()
                f.write(f"  Direct gap: {direct_gap:.4f} eV\n")
            except:
                f.write(f"  Direct gap: N/A\n")
        except:
            f.write(f"\nBand edges: N/A (metallic system)\n")

def write_gnuplot_files(dos, bs, material_id):
    material_dir = Path(f"data/{material_id}")
    
    energies = dos.energies
    densities = dos.densities[1] if 1 in dos.densities else list(dos.densities.values())[0]
    
    mask = (energies >= -10) & (energies <= 10)
    dos_in_range = densities[mask]
    max_dos = np.max(dos_in_range) if len(dos_in_range) > 0 else np.max(densities)
    
    with open(material_dir / f"{material_id}_dos.gnuplot", "w") as f:
        f.write(f"set title '{material_id} - Density of States'\n")
        f.write("set xlabel 'Energy (eV)'\nset ylabel 'DOS (states/eV)'\nset grid\n")
        f.write(f"set xrange [-10:10]\nset yrange [0:{max_dos * 1.1:.3f}]\n")
        f.write(f"set xzeroaxis lt -1\nset terminal png size 800,600\n")
        f.write(f"set output '{material_id}_dos_gnuplot.png'\n")
        f.write(f"plot '-' using 1:2 with lines title 'DOS'\n")
        for e, d in zip(energies, densities):
            f.write(f"{e:.6f} {d:.6f}\n")
        f.write("e\n")
    
    bands = bs.bands[1] if 1 in bs.bands else list(bs.bands.values())[0]
    kpoint_distances = bs.distance
    
    with open(material_dir / f"{material_id}_bands.gnuplot", "w") as f:
        f.write(f"set title '{material_id} - Band Structure'\n")
        f.write("set xlabel 'k-path'\nset ylabel 'Energy (eV)'\nset grid y\n")
        f.write(f"set yrange [-5:5]\nset terminal png size 800,600\n")
        f.write(f"set output '{material_id}_bands_gnuplot.png'\n")
        f.write("plot ")
        for band_idx in range(bands.shape[0]):
            if band_idx > 0:
                f.write(", ")
            f.write(f"'-' using 1:2 with lines notitle")
        f.write("\n")
        
        for band_idx in range(bands.shape[0]):
            for i, dist in enumerate(kpoint_distances):
                f.write(f"{dist:.6f} {bands[band_idx, i] - bs.efermi:.6f}\n")
            f.write("e\n")

if __name__ == "__main__":
    process_all_materials()