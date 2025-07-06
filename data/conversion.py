import pickle
import os
from pathlib import Path
from typing import Dict, Any, Optional

class MPTxtExporter:
    def __init__(self, properties_dir: str = "properties"):
        self.properties_dir = properties_dir
    
    def format_value(self, value: Any) -> str:
        if value is None:
            return "None"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            return str(value)
    
    def extract_dos_data(self, dos_obj) -> Dict[str, Any]:
        data = {}
        
        if hasattr(dos_obj, 'magnetic_ordering'):
            data['dos_magnetic_ordering'] = dos_obj.magnetic_ordering
        
        if hasattr(dos_obj, 'total') and dos_obj.total:
            total_data = list(dos_obj.total.values())[0]
            if total_data:
                data['dos_total_task_id'] = str(total_data.task_id) if hasattr(total_data, 'task_id') else "None"
                data['dos_total_band_gap'] = total_data.band_gap if hasattr(total_data, 'band_gap') else None
                data['dos_total_cbm'] = total_data.cbm if hasattr(total_data, 'cbm') else None
                data['dos_total_vbm'] = total_data.vbm if hasattr(total_data, 'vbm') else None
                data['dos_total_efermi'] = total_data.efermi if hasattr(total_data, 'efermi') else None
        
        return data
    
    def extract_bandstructure_data(self, bs_obj) -> Dict[str, Any]:
        data = {}
        
        for method in ['setyawan_curtarolo', 'hinuma', 'latimer_munro']:
            if hasattr(bs_obj, method):
                method_data = getattr(bs_obj, method)
                if method_data:
                    data[f'bs_{method}_task_id'] = str(method_data.task_id) if hasattr(method_data, 'task_id') else "None"
                    data[f'bs_{method}_band_gap'] = method_data.band_gap if hasattr(method_data, 'band_gap') else None
                    data[f'bs_{method}_cbm'] = method_data.cbm if hasattr(method_data, 'cbm') else None
                    data[f'bs_{method}_vbm'] = method_data.vbm if hasattr(method_data, 'vbm') else None
                    data[f'bs_{method}_efermi'] = method_data.efermi if hasattr(method_data, 'efermi') else None
        
        return data
    
    def pkl_to_txt(self, material_id: str) -> bool:
        pkl_path = os.path.join(self.properties_dir, f"{material_id}.pkl")
        txt_path = os.path.join(self.properties_dir, f"{material_id}.txt")
        
        if not os.path.exists(pkl_path):
            return False
        
        try:
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
            
            output_lines = []
            
            output_lines.append(f"material_id: {data['material_id']}")
            output_lines.append(f"band_gap: {self.format_value(data['band_gap'])}")
            output_lines.append(f"efermi: {self.format_value(data['efermi'])}")
            
            if 'dos' in data:
                dos_data = self.extract_dos_data(data['dos'])
                for key, value in dos_data.items():
                    output_lines.append(f"{key}: {self.format_value(value)}")
            
            if 'bandstructure' in data:
                bs_data = self.extract_bandstructure_data(data['bandstructure'])
                for key, value in bs_data.items():
                    output_lines.append(f"{key}: {self.format_value(value)}")
            
            with open(txt_path, 'w') as f:
                f.write('\n'.join(output_lines))
            
            return True
            
        except Exception as e:
            print(f"Error processing {material_id}: {e}")
            return False
    
    def convert_all_to_txt(self):
        pkl_files = [f for f in os.listdir(self.properties_dir) if f.endswith('.pkl')]
        total_files = len(pkl_files)
        
        print(f"Converting {total_files} pkl files to txt...")
        
        success_count = 0
        error_count = 0
        
        for i, pkl_file in enumerate(pkl_files, 1):
            material_id = pkl_file.replace('.pkl', '')
            
            if self.pkl_to_txt(material_id):
                success_count += 1
            else:
                error_count += 1
            
            if i % 1000 == 0:
                print(f"Processed {i}/{total_files} files")
        
        print(f"\nConversion complete:")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
    
    def preview_txt_output(self, material_id: str):
        pkl_path = os.path.join(self.properties_dir, f"{material_id}.pkl")
        
        if not os.path.exists(pkl_path):
            print(f"File not found: {pkl_path}")
            return
        
        try:
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
            
            print(f"Preview for {material_id}:")
            print("=" * 50)
            
            print(f"material_id: {data['material_id']}")
            print(f"band_gap: {self.format_value(data['band_gap'])}")
            print(f"efermi: {self.format_value(data['efermi'])}")
            
            if 'dos' in data:
                dos_data = self.extract_dos_data(data['dos'])
                for key, value in dos_data.items():
                    print(f"{key}: {self.format_value(value)}")
            
            if 'bandstructure' in data:
                bs_data = self.extract_bandstructure_data(data['bandstructure'])
                for key, value in bs_data.items():
                    print(f"{key}: {self.format_value(value)}")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    exporter = MPTxtExporter()
    
    exporter.preview_txt_output("mp-1")
    
    print("\nStarting full conversion...")
    exporter.convert_all_to_txt()

if __name__ == "__main__":
    main()