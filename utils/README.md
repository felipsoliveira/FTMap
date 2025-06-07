# Utilities Directory

This directory contains utility scripts and tools used for development, data generation, and maintenance of the FTMap workflow system.

## Utility Scripts

### Data Generation
- **`generate_complete_ftmap.py`** - Generates complete FTMap analysis with all fragments and hotspots
- **`generate_complete_molecules.py`** - Creates complete molecule PDB files with fragment structures
- **`create_complete_pdb.py`** - Utility for creating complete PDB files with proper formatting

### Maintenance
- **`cleanup_analysis.py`** - Cleans up analysis files and temporary outputs from previous runs

## Usage

### Generate Complete Data
```bash
# Generate complete FTMap analysis
python utils/generate_complete_ftmap.py

# Generate complete molecule structures
python utils/generate_complete_molecules.py

# Create properly formatted PDB files
python utils/create_complete_pdb.py
```

### Maintenance
```bash
# Clean up analysis outputs
python utils/cleanup_analysis.py
```

## Purpose

These utilities were developed to:
1. Generate comprehensive test data for workflow validation
2. Create properly formatted molecular structure files
3. Maintain and clean up the workspace
4. Support development and debugging processes

## Integration with Main Workflow

These utilities complement the main FTMap workflow (`ftmap_workflow/`) by providing:
- Data generation capabilities for testing
- File format conversion and cleanup tools
- Development support utilities

All utilities are designed to work with the standard FTMap workflow directory structure and data formats.
