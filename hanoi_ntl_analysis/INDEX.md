# Hanoi NTL Analysis - Complete Project Index

## 📖 Documentation (Start Here)

### **For Quick Overview** (5 minutes)
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** — Executive summary of everything delivered

### **For Step-by-Step Execution** (10 minutes)
→ **[QUICK_START.md](QUICK_START.md)** — Commands to run, expected times, troubleshooting

### **For Complete Methodology** (30 minutes)
→ **[README.md](README.md)** — Full documentation, dataset selection, validation strategy

### **For Project Details** (20 minutes)
→ **[SETUP_SUMMARY.md](SETUP_SUMMARY.md)** — What was created, feasibility, next steps

### **For Detailed Inventory** (15 minutes)
→ **[DELIVERABLES.md](DELIVERABLES.md)** — Complete file listing, code overview

---

## 📂 Project Structure

```
hanoi_ntl_analysis/
│
├── 📋 DOCUMENTATION (Read these first)
│   ├── PROJECT_SUMMARY.md          ← START HERE (Executive summary)
│   ├── QUICK_START.md              ← Step-by-step execution
│   ├── README.md                   ← Complete methodology
│   ├── SETUP_SUMMARY.md            ← Setup reference
│   └── DELIVERABLES.md             ← Inventory & overview
│
├── 🛠️  CONFIGURATION
│   ├── config.py                   ← All parameters in one file
│   └── requirements.txt            ← Python dependencies (pip install -r)
│
├── 📊 MAIN ANALYSIS
│   └── notebooks/
│       └── 00_hanoi_ntl_analysis.ipynb    ← Execute this! (11 sections)
│
├── 🐍 SUPPORTING SCRIPTS
│   └── scripts/
│       ├── 01_download_viirs.py           ← Download data from GEE
│       ├── ntl_processing.py              ← Core processing functions
│       └── spatial_analysis.py            ← Spatial analysis module
│
├── 💾 DATA DIRECTORIES
│   ├── data/
│   │   ├── viirs_raw/              ← Downloaded VIIRS GeoTIFFs (144 files)
│   │   ├── viirs_processed/        ← Processed annual composites
│   │   └── validation/             ← High-res validation imagery
│   │
│   └── outputs/                    ← Generated results (figures, tables)
│
└── 📄 THIS FILE
    └── INDEX.md                    ← You are here!
```

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies (5 minutes)
```powershell
cd "C:\Users\anhmi\OneDrive\Documents\University\CRP2\hanoi_ntl_analysis"
pip install -r requirements.txt
```

### 2. Authenticate with Google Earth Engine (5 minutes)
```powershell
earthengine authenticate
# Follow browser prompt, return to terminal, paste authorization code
```

### 3. Download Data & Run Analysis (6-10 hours)
```powershell
# Download VIIRS data
python scripts/01_download_viirs.py
# Then download files from Google Drive to data/viirs_raw/
# Then execute notebook
jupyter notebook notebooks/00_hanoi_ntl_analysis.ipynb
```

**For detailed steps**: See [QUICK_START.md](QUICK_START.md)

---

## 📚 Reading Guide by Use Case

### **"I just want to get started"**
1. Read: [QUICK_START.md](QUICK_START.md) (10 min)
2. Run 3 commands above
3. Execute notebook
4. Review outputs

### **"I want to understand the methodology"**
1. Read: [README.md](README.md) (30 min) — Complete explanation
2. Check: [config.py](config.py) (10 min) — Parameters & justifications
3. Review: Notebook [Section 6](notebooks/00_hanoi_ntl_analysis.ipynb) — Threshold justification
4. See: [README.md](README.md) "References" — Peer-reviewed papers

### **"I want to know what's been created"**
1. Read: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (5 min) — Overview
2. Check: [DELIVERABLES.md](DELIVERABLES.md) (15 min) — Complete inventory
3. Review: [SETUP_SUMMARY.md](SETUP_SUMMARY.md) (10 min) — Details

### **"I want to modify/extend the code"**
1. Read: [config.py](config.py) — Understand parameters
2. Review: [scripts/ntl_processing.py](scripts/ntl_processing.py) — Core functions
3. Check: [scripts/spatial_analysis.py](scripts/spatial_analysis.py) — Spatial functions
4. Study: Notebook — See how functions are used
5. Modify & extend as needed

### **"I want publication-ready results"**
1. Review: [README.md](README.md) "Validation Strategy" — Section 4
2. Run: Notebook [Section 10](notebooks/00_hanoi_ntl_analysis.ipynb)
3. Implement: High-resolution imagery validation
4. Document: Uncertainty sources (already identified in README)
5. Export: Figures & tables for submission

---

## 🎯 What Each File Does

### **Documentation Files**
| File | Purpose | Read Time | Start Here? |
|------|---------|-----------|------------|
| PROJECT_SUMMARY.md | Executive summary of everything | 5 min | ✅ YES |
| QUICK_START.md | Step-by-step execution guide | 10 min | ✅ YES |
| README.md | Complete methodology & justifications | 30 min | For details |
| SETUP_SUMMARY.md | Setup reference & what was created | 10 min | For details |
| DELIVERABLES.md | Detailed inventory of files | 15 min | For inventory |
| INDEX.md | This file (you are here) | 5 min | Navigation |

### **Code Files**
| File | Purpose | Lines | When to Use |
|------|---------|-------|------------|
| config.py | Configuration & parameters | 90 | Before running (review) |
| requirements.txt | Python dependencies | 17 | Once at start (pip install) |
| 01_download_viirs.py | Download VIIRS from GEE | 150 | After GEE auth (execute) |
| ntl_processing.py | Core NTL functions | 350 | Called by notebook |
| spatial_analysis.py | Spatial analysis functions | 350 | Called by notebook |
| 00_hanoi_ntl_analysis.ipynb | Main analysis notebook | 1000+ | Execute sections 1-11 |

---

## 📊 Analysis Workflow

```
1. SETUP
   ├─ pip install -r requirements.txt
   ├─ earthengine authenticate
   └─ [Create directories] ✅ Done

2. DATA ACQUISITION
   ├─ python scripts/01_download_viirs.py
   ├─ [Download from Google Drive]
   └─ [Place in data/viirs_raw/] ← YOUR ACTION

3. ANALYSIS EXECUTION
   ├─ Section 1-2: Import & setup
   ├─ Section 3-4: Load VIIRS data
   ├─ Section 5-6: Threshold justification
   ├─ Section 7-8: Processing
   ├─ Section 9: Results & visualization
   ├─ Section 10: Validation
   └─ Section 11: Summary

4. REVIEW OUTPUTS
   ├─ outputs/*.png              [Figures]
   ├─ outputs/*.csv              [Data tables]
   ├─ outputs/*.txt              [Reports]
   └─ data/viirs_processed/*.tif [GeoTIFF products]

5. VALIDATION (Optional)
   ├─ Download Sentinel-2 & Landsat 8
   ├─ Compute NDBI
   ├─ Compare accuracy
   └─ Document findings
```

---

## 🎓 Key Concepts Explained

### **NTL Threshold: DN > 3.0**
**Why?** Selected based on:
- Peer-reviewed literature (Jing et al. 2016, Li et al. 2019)
- Hanoi-specific factors (tropical monsoon, mixed development)
- Balances sensitivity vs. specificity
- Tested via sensitivity analysis (DN > 1, 2, 3, 5)

**Where documented?**
- [README.md](README.md) — "NTL Threshold Selection" section
- [config.py](config.py) — Inline comments with justification
- [Notebook](notebooks/00_hanoi_ntl_analysis.ipynb) — Section 6

### **VIIRS Dataset: VCMCFG**
**Why?** Selected over alternatives because:
- Full 2012-2023 coverage
- Fixed-gain calibration (temporal consistency)
- NOAA-recommended for trend analysis
- Better than VNCCFG, cheaper than VCMSLV

**Where documented?**
- [README.md](README.md) — "Why VCMCFG" section
- [Notebook](notebooks/00_hanoi_ntl_analysis.ipynb) — Section 4
- [SETUP_SUMMARY.md](SETUP_SUMMARY.md) — Comparison table

### **Expansion Metrics**
- **Lit Area**: Total pixels > threshold × pixel size² (km²)
- **Growth Rate**: (Area_year - Area_year-1) / Area_year-1 × 100 (%)
- **Compactness**: 4π × Area / Perimeter² (0-1, where 1 = circle)

**Where documented?**
- [README.md](README.md) — "Expansion Metrics" section
- [scripts/ntl_processing.py](scripts/ntl_processing.py) — Function docstrings
- [Notebook](notebooks/00_hanoi_ntl_analysis.ipynb) — Sections 8-9

---

## 🔍 File Locations Reference

### **Configuration**
```
config.py
└─ HANOI_BOUNDS, NTL_THRESHOLD, RING_WIDTHS, etc.
```

### **Data Download**
```
scripts/01_download_viirs.py
└─ Run this to get VIIRS data from Google Earth Engine
```

### **Core Processing**
```
scripts/ntl_processing.py
├─ create_urban_mask()
├─ calculate_lit_area()
├─ calculate_compactness()
├─ find_centroid()
├─ analyze_ring_expansion()
├─ analyze_directional_expansion()
├─ sensitivity_analysis()
└─ export_geotiff()
```

### **Spatial Analysis**
```
scripts/spatial_analysis.py
├─ compute_centroid_shift()
├─ analyze_ring_expansion()
├─ analyze_directional_expansion()
└─ visualize_* functions
```

### **Main Analysis**
```
notebooks/00_hanoi_ntl_analysis.ipynb
├─ Section 1: Setup
├─ Section 2: GEE Auth
├─ Section 3-5: Data Load
├─ Section 6: Threshold Justification
├─ Section 7-9: Analysis
├─ Section 10: Validation
└─ Section 11: Summary
```

### **Results**
```
outputs/
├─ *.png                      [Figures: 300 DPI]
├─ *.csv                      [Data tables]
└─ *.txt                      [Reports]
```

---

## ✅ Verification Checklist

Before you start:
- [ ] Read [QUICK_START.md](QUICK_START.md)
- [ ] Have Google account for Earth Engine
- [ ] Python 3.8+ installed
- [ ] ~5 GB disk space available

After installation:
- [ ] `pip install -r requirements.txt` completes without errors
- [ ] `earthengine authenticate` succeeds
- [ ] `python scripts/01_download_viirs.py` runs without errors

After data download:
- [ ] `data/viirs_raw/` contains 144 GeoTIFF files
- [ ] Files named like: `VIIRS_DNB_2023_01.tif`
- [ ] Notebook opens without import errors

After analysis:
- [ ] `outputs/` contains PNG figures
- [ ] CSV data tables have results
- [ ] Visualizations look correct

---

## 🎯 Success Criteria

Your analysis is successful when:

✅ **Data Phase**
- 144 VIIRS monthly composites downloaded
- Files organized in `data/viirs_raw/`

✅ **Processing Phase**
- Notebook runs all sections without errors
- Urban masks created for each year
- Metrics calculated (area, growth, compactness)

✅ **Analysis Phase**
- Time series shows clear urbanization trend
- Spatial analysis identifies growth direction
- Centroid moves in expected direction

✅ **Validation Phase**
- Sentinel-2 NDBI comparison performed
- Accuracy metrics calculated (> 85% expected)
- Uncertainties documented

✅ **Deliverables Phase**
- Figures saved as PNG (300 DPI)
- Results tables exported as CSV
- Report written with findings

---

## 🆘 Help & Support

### **If installation fails**
→ Check [QUICK_START.md](QUICK_START.md) "Troubleshooting" section

### **If GEE authentication fails**
→ See [README.md](README.md) "Troubleshooting" section

### **If notebook errors**
→ Verify data files in `data/viirs_raw/` are present

### **If you want to modify parameters**
→ Edit [config.py](config.py) and review docstrings

### **If you want to add new analysis**
→ Import functions from `scripts/` modules into notebook

### **If you're unsure about methodology**
→ Read [README.md](README.md) "Methodology" section with references

---

## 📞 Quick Reference

**Most important files to remember:**
1. **Start**: [QUICK_START.md](QUICK_START.md)
2. **Execute**: [notebooks/00_hanoi_ntl_analysis.ipynb](notebooks/00_hanoi_ntl_analysis.ipynb)
3. **Configure**: [config.py](config.py)
4. **Understand**: [README.md](README.md)

**Most important commands:**
```powershell
pip install -r requirements.txt      # One-time setup
earthengine authenticate              # One-time auth
python scripts/01_download_viirs.py   # Download data
jupyter notebook notebooks/*.ipynb     # Run analysis
```

---

## 📜 Document Last Updated

**Date**: January 9, 2026  
**Status**: ✅ Complete & Ready for Execution  
**Total Size**: 3000+ lines of code + 650+ lines of documentation

---

## 🎉 You're All Set!

Everything is ready. Start with [QUICK_START.md](QUICK_START.md) and follow the 3-step setup.

Questions? Check the appropriate documentation file in the table above.

Good luck with your analysis! 🚀

