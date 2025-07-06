# AZARATH

AZARATH enables a new class of materials prediction models that can generate complete electronic property profiles, not just scalar values. This represents a significant step toward AI-driven materials discovery workflows. Built from 51,037 materials using the latest Materials Project API, AZARATH provides zero-friction access to complex electronic properties, accessible in the easy-to-use .gnuplot and .txt formats.

## Improvements

GNNs can predict scalar properties with reasonable accuracy, but there are very few options that can directly predict density-of-states (DOS) and band structure, directly from atomic coordinates. To rectify this, we've made AZARATH with a few key improvements over existing datasets, to facilitate rapid research in this field:

- Density of States and Band Structure: We provide 51,037 materials with several scalar values highly important to DOS and band structure, to provide the basis for a pretraining stage for a GNN. Then, we provide over 3,999 direct examples of density-of-states diagrams and band structure diagrams.

- Preprocessing: Materials Project's API packages its files as .pkl (pickle) files, which takes up incredible amounts of space and require custom parsing to use. We've already preprocessed all the .pkl data into .txt and .gnuplot formats, to provide extremely easy facilitation of such research. We've also provided scripts to rapidly convert the .gnuplot files to images.

- Infrastructure: We provide all our scripts, including what we used for downloading, cleaning, parsing, and management. Simply insert your free API key to materials project, pick the parameters that you want it to return, and create massive datasets of your own. 

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

The process is relatively simple, and all scripts we used are provided here. All of this is open source under the MIT License, and we hope this helps the creation of more custom datasets, and powerful GNNs. 
