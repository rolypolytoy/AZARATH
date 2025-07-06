import pickle
import os
import multiprocessing as mp
from pathlib import Path
from tqdm import tqdm
import concurrent.futures
import ujson as json
from typing import Dict, Any, List, Tuple
import gc

def extract_mp_data(data: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        'material_id': str(data['material_id']).replace('MPID(', '').replace(')', ''),
        'band_gap': data['band_gap'],
        'efermi': data['efermi'],
        'magnetic_ordering': None
    }
    
    if 'dos' in data and hasattr(data['dos'], 'magnetic_ordering'):
        result['magnetic_ordering'] = data['dos'].magnetic_ordering
    
    if 'dos' in data and hasattr(data['dos'], 'total'):
        dos_total = data['dos'].total
        if dos_total and '1' in dos_total:
            dos_data = dos_total['1']
            result.update({
                'dos_task_id': str(dos_data.task_id).replace('MPID(', '').replace(')', ''),
                'dos_band_gap': dos_data.band_gap,
                'dos_cbm': dos_data.cbm,
                'dos_vbm': dos_data.vbm,
                'dos_efermi': dos_data.efermi
            })
    
    if 'bandstructure' in data:
        bs = data['bandstructure']
        for method in ['setyawan_curtarolo', 'hinuma', 'latimer_munro']:
            if hasattr(bs, method):
                method_data = getattr(bs, method)
                result.update({
                    f'bs_{method}_task_id': str(method_data.task_id).replace('MPID(', '').replace(')', ''),
                    f'bs_{method}_band_gap': method_data.band_gap,
                    f'bs_{method}_cbm': method_data.cbm,
                    f'bs_{method}_vbm': method_data.vbm,
                    f'bs_{method}_efermi': method_data.efermi
                })
    
    return result

def process_pkl_file(pkl_path: str) -> Tuple[bool, str]:
    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        
        parsed_data = extract_mp_data(data)
        mpid = parsed_data['material_id']
        
        txt_path = f"properties/{mpid}.txt"
        
        formatted_output = []
        for key, value in parsed_data.items():
            if value is not None:
                formatted_output.append(f"{key}={value}")
            else:
                formatted_output.append(f"{key}=null")
        
        with open(txt_path, 'w') as f:
            f.write('\n'.join(formatted_output))
        
        os.remove(pkl_path)
        return True, mpid
        
    except Exception as e:
        return False, f"Error processing {pkl_path}: {str(e)}"

def process_batch(pkl_files: List[str]) -> Tuple[int, int, List[str]]:
    success_count = 0
    error_count = 0
    errors = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures = {executor.submit(process_pkl_file, pkl_file): pkl_file for pkl_file in pkl_files}
        
        for future in concurrent.futures.as_completed(futures):
            success, result = future.result()
            if success:
                success_count += 1
            else:
                error_count += 1
                errors.append(result)
    
    return success_count, error_count, errors

def get_pkl_files_fast(directory: str) -> List[str]:
    return [str(p) for p in Path(directory).rglob('*.pkl')]

def chunked(lst: List[Any], chunk_size: int):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def main():
    properties_dir = "properties"
    chunk_size = 1000
    
    print("Discovering pkl files...")
    pkl_files = get_pkl_files_fast(properties_dir)
    total_files = len(pkl_files)
    
    print(f"Found {total_files:,} pkl files")
    print(f"Processing in chunks of {chunk_size:,}")
    print(f"Using {mp.cpu_count()} CPU cores")
    
    total_success = 0
    total_errors = 0
    all_errors = []
    
    chunks = list(chunked(pkl_files, chunk_size))
    
    with tqdm(total=total_files, desc="Processing files", unit="files") as pbar:
        for i, chunk in enumerate(chunks, 1):
            pbar.set_description(f"Processing chunk {i}/{len(chunks)}")
            
            success, errors, error_list = process_batch(chunk)
            
            total_success += success
            total_errors += errors
            all_errors.extend(error_list)
            
            pbar.update(len(chunk))
            pbar.set_postfix({
                'success': total_success,
                'errors': total_errors,
                'rate': f"{total_success/(i*chunk_size)*100:.1f}%"
            })
            
            if i % 10 == 0:
                gc.collect()
    
    print(f"\nCompleted: {total_success:,} successful, {total_errors:,} errors")
    
    if all_errors:
        print(f"Writing error log...")
        with open('processing_errors.log', 'w') as f:
            f.write('\n'.join(all_errors))

if __name__ == "__main__":
    main()