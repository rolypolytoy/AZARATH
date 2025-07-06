# AZARATH
An open dataset to train GNN models on to predict properties of various materials like bandgaps, Fermi levels, as well as density-of-states and band structure diagrams. Includes over 51k materials, indexed from the Materials Project on 6th July 2025.

## Usage
Simply clone the repository via:

```bash
git clone https://github.com/rolypolytoy/AZARATH.git
```

## Structure
Exactly 51,037 unique materials were parsed from the Materials Project on the 6th of July 2025, with their .cif files, Band Gaps, Fermi Energy, Density-of-States information and Band Structure information. In data/properties you'll find 51,037 plaintext (*.txt) files in the following format:

```txt
material_id: mp-10
band_gap: 0.0
efermi: 5.53250946
dos_magnetic_ordering: NM
dos_total_task_id: mp-1669854
dos_total_band_gap: 0.0
dos_total_cbm: 5.5156
dos_total_vbm: 5.5736
dos_total_efermi: 5.56634891
bs_setyawan_curtarolo_task_id: mp-1608106
bs_setyawan_curtarolo_band_gap: 0.0
bs_setyawan_curtarolo_cbm: None
bs_setyawan_curtarolo_vbm: None
bs_setyawan_curtarolo_efermi: 5.53250946
bs_hinuma_task_id: mp-2171776
bs_hinuma_band_gap: 0.0
bs_hinuma_cbm: None
bs_hinuma_vbm: None
bs_hinuma_efermi: 5.53250946
bs_latimer_munro_task_id: mp-2323758
bs_latimer_munro_band_gap: 0.0
bs_latimer_munro_cbm: None
bs_latimer_munro_vbm: None
bs_latimer_munro_efermi: 5.53250946
```

The respective cifs are in data/structures. In data/data, you'll find a subset of 3,999 with full-resolution .gnuplot files of the DOS and Band Structure information, along with the .cif and .txt files for them. 

The larger dataset's intent is to provide an easy to set-up dataset for pretraining DFT-substitute models on, with the crystal structure as the input. The up-to-date information and scripting for the MP API we've provided should allow the creation of custom datasets with the arguments you want. The smaller dataset exists to either finetune or create specialized models capable of directly generating DOS and band structure diagrams from crystal data. 

## Process
We first used the [Materials Project API](https://next-gen.materialsproject.org/api) to collect the raw .pkl files with the arguments we wanted. We then identified what data structures it used and parsed the information we wanted, and converted it as-is. You can use image.py to mass convert all the .gnuplots to images, but .gnuplot files are superior numerically, when you're, for example, pretraining GNNs.

The process is relatively simple, and all scripts we used are provided here. All of this is open source under the MIT License, and we hope this helps the creation of more custom datasets. 
