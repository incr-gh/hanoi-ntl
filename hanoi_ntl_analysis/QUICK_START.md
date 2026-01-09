# Quick Start Guide: Hanoi NTL Analysis

## Step 1: Navigate to Project Directory
```powershell
cd "C:\Users\anhmi\OneDrive\Documents\University\CRP2\hanoi_ntl_analysis"
```

## Step 2: Install Dependencies (One-time)
```powershell
pip install -r requirements.txt
```

Expected output: All 17 packages installed successfully
- pandas, numpy, geopandas, rasterio, xarray, scipy, scikit-image, matplotlib, etc.

## Step 3: Set Up Google Earth Engine Authentication (One-time)
```powershell
earthengine authenticate
```

- Opens browser window automatically
- Sign in with Google account
- Grant permissions
- Return to terminal (authorization code copied)
- Paste code and press Enter

## Step 4: Download VIIRS Data
```powershell
python scripts/01_download_viirs.py
```

**What this does**:
- Submits 144 export tasks to Google Earth Engine
- Each task: one month of VIIRS DNB data (2012-2023)
- Exports to your Google Drive in folder `hanoi_ntl_analysis`
- Creates log file: `data/gee_export_log.csv`

**Time**: ~2-5 minutes to submit all tasks (depends on GEE server load)

**Next**:
- Monitor progress at: https://code.earthengine.google.com/tasks
- Download all files from Google Drive
- Place in: `data/viirs_raw/` folder

## Step 5: Run Analysis Notebook
```powershell
jupyter notebook notebooks/00_hanoi_ntl_analysis.ipynb
```

Or use VS Code:
1. Open file in VS Code
2. Install Jupyter extension if needed
3. Click "Run Cell" for each cell sequentially
4. Execute all sections 1-11

**Execution order**:
1. ✅ Section 1: Import libraries
2. ✅ Section 2: GEE authentication
3. ✅ Section 3: Load VIIRS data
4. ✅ Section 4: Dataset selection explanation
5. ✅ Section 5: Extract sample imagery
6. ✅ Section 6: Threshold justification
7. ✅ Section 7: Comparison visualizations
8. ✅ Section 8: Time series processing
9. ✅ Section 9: Results & visualization
10. ✅ Section 10: Validation strategy
11. ✅ Section 11: Workflow summary

## Step 6: Review Results
```powershell
# View generated files
dir outputs/
dir data/viirs_processed/
```

Expected outputs:
- `outputs/hanoi_ntl_timeseries.png` — Main results plot
- `outputs/hanoi_ntl_2023_comparison.png` — DNB vs. urban mask
- `outputs/time_series_metrics.csv` — Results table
- `data/viirs_processed/*.tif` — Processed VIIRS data

---

## Alternative: Running Specific Cells Only

If you want to test without full execution:

### Just test threshold sensitivity
```python
# In notebook, run sections 1-2, then jump to section 6-7
```

### Just download and inspect data
```python
# Run section 1-3 only, skip to section 5
```

### Skip data download (use test data)
```python
# Section 8 includes example with synthetic data for testing
```

---

## Troubleshooting

### GEE Authentication Fails
```powershell
# Clear cache and retry
Remove-Item $env:USERPROFILE\.config\earthengine\ -Recurse -Force
earthengine authenticate
```

### VIIRS files not found
```powershell
# Check if files downloaded from Google Drive
# Verify folder: data/viirs_raw/
# Files should be named: VIIRS_DNB_2023_01.tif, VIIRS_DNB_2023_02.tif, etc.

# List files to verify
dir data/viirs_raw/ | Measure-Object
# Should show 144 files for complete 2012-2023 dataset
```

### Jupyter notebook won't open
```powershell
# Ensure Jupyter is installed
pip install jupyter

# Try alternative: Open with VS Code Jupyter extension
code notebooks/00_hanoi_ntl_analysis.ipynb
```

### Memory issues
```python
# Process one year at a time instead of full time series
# Edit notebook: change 'years = range(2012, 2024)' to 'years = [2023]'
# Or use xarray with dask for chunked processing
```

---

## Expected Runtime

| Task | Time |
|------|------|
| Installation | 5-10 min |
| GEE authentication | 2-5 min |
| Data download (submit jobs) | 2-5 min |
| Data download (from GEE to Drive) | 30-60 min (depends on GEE server) |
| Download from Drive to computer | 10-30 min |
| Notebook execution (Sections 1-7) | 5-10 min |
| Full analysis (Sections 1-11) | 30-60 min |
| Validation (optional) | 1-2 hours |
| **TOTAL** | **6-10 hours** |

---

## Key Files to Check

### Configuration
```
config.py  # Review parameters here before running
```

### Main analysis
```
notebooks/00_hanoi_ntl_analysis.ipynb  # Execute this file
```

### Helper functions
```
scripts/ntl_processing.py       # Core processing
scripts/spatial_analysis.py     # Ring/directional analysis
scripts/01_download_viirs.py    # GEE download
```

### Documentation
```
README.md          # Full methodology
SETUP_SUMMARY.md   # Setup reference
DELIVERABLES.md    # What was created
```

---

## Data File Organization

After running full pipeline:

```
hanoi_ntl_analysis/
│
├── data/
│   ├── viirs_raw/                  # Downloaded VIIRS GeoTIFFs (144 files)
│   │   ├── VIIRS_DNB_2012_01.tif
│   │   ├── VIIRS_DNB_2012_02.tif
│   │   └── ...
│   ├── viirs_processed/            # Processed annual composites
│   │   ├── annual_composite_2012.tif
│   │   ├── urban_mask_2012.tif
│   │   └── ...
│   ├── validation/                 # High-res validation data
│   │   └── sentinel2_2022.tif
│   └── gee_export_log.csv
│
├── outputs/
│   ├── hanoi_ntl_timeseries.png
│   ├── hanoi_ntl_2023_comparison.png
│   ├── spatial_analysis_maps.png
│   ├── time_series_metrics.csv
│   ├── spatial_analysis_results.csv
│   └── validation_report.txt
│
└── notebooks/
    └── [generated plots + analysis results]
```

---

## Using Results

### Time Series Metrics
```python
import pandas as pd
df = pd.read_csv('outputs/time_series_metrics.csv')
print(df)
# Year | Lit Area (km²) | Growth Rate (%) | Compactness | Centroid (lat, lon)
```

### Plotting Results
```python
import matplotlib.pyplot as plt
img = plt.imread('outputs/hanoi_ntl_timeseries.png')
plt.imshow(img)
plt.axis('off')
plt.tight_layout()
plt.savefig('hanoi_results.pdf')
```

### Validation Accuracy
```python
# Check accuracy metrics from validation report
with open('outputs/validation_report.txt') as f:
    print(f.read())
```

---

## Support & References

- **Google Earth Engine**: https://earthengine.google.com
- **VIIRS Data**: https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG
- **Sentinel-2**: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR
- **Landsat 8/9**: https://developers.google.com/earth-engine/datasets/catalog/USGS_LANDSAT_LC09_C02_T1_L2

---

## Tips for Success

✅ **Do**:
- Read README.md first for full context
- Check config.py to understand parameters
- Execute cells sequentially in notebook
- Save outputs before modifying code
- Keep VIIRS files organized in data/viirs_raw/

❌ **Don't**:
- Delete downloaded VIIRS files
- Modify config parameters without understanding impact
- Run all notebook cells at once (execute sequentially)
- Process all 12 years if testing (use 1-2 years first)

---

**Happy analyzing! Questions? See README.md or SETUP_SUMMARY.md**

---

Created: January 9, 2026
