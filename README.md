# AZARATH
An open dataset to train GNN models on to predict properties of various materials like bandgaps, Fermi levels, as well as density-of-states and band structure diagrams. Includes over 51k materials, indexed from the Materials Project on 6th July 2025.

## Usage
Simply clone the repository via:

```bash
git clone https://github.com/rolypolytoy/AZARATH.git
```
Every material in the Materials Project has a unique identifier (e.g. mp-10, mp-10239, etc.). In the AZARATH/structures folder, all the .cif files for them are found, with the precursor being its unique identifier. In the AZARATH/properties folder, .pkl (pickle) files with the Band Gap, Band Structure, Fermi Energy, Density of States, and some miscellaneous calculation information is there. The script I used can regenerate these files in under a minute, and you can vary the parameters you call from the Materials Project, but you have to add your own (free) [API key](https://next-gen.materialsproject.org/api) to the file. AZARATH/material_ids.json is a list of all the material IDs, for reference or any additional processing.

All of the data was gathered on the 6th of July 2025, and so this is the most up-to-date, large-scale repository for data that might be easily fed to GNNs or derivative models. 
