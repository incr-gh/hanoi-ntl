# Hanoi NTL Analysis: 2012-2023 Time Series
## Urban Growth Mapping using NOAA VIIRS Nighttime Lights

### Overview
This project constructs a consistent **12-year time series (2012-2023)** of nighttime lights (NTL) for Hanoi municipality using NOAA VIIRS/DNB data. The analysis characterizes urban expansion through multiple spatial and temporal metrics, with validation using high-resolution satellite imagery.

**Data Source**: [NOAA VIIRS DNB Monthly V1.0 (VCMCFG) - Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG)

---

## Objectives

1. **Construct consistent NTL time series** for Hanoi municipality (2012-2023)
   - 144 monthly VIIRS DNB composites
   - Annual median composites for consistent temporal analysis

2. **Delineate yearly "lit urban areas"** and quantify expansion metrics
   - Threshold-based urban classification (DN > 3.0)
   - Total lit area (km²)
   - Annual growth rates (%)
   - Urban compactness indices

3. **Characterize spatial patterns** of urban growth
   - **Directional analysis**: 8-sector expansion patterns
   - **Ring-wise analysis**: Concentric buffer expansion (0-1km, 1-3km, 3-8km from center)
   - **Centroid-shift analysis**: Track movement of urban center

4. **Lightweight validation** using high-resolution imagery
   - Sentinel-2 NDBI comparison (10m resolution)
   - Landsat 8/9 multi-spectral indices
   - Accuracy metrics (confusion matrix, overall accuracy, Kappa)
   - Uncertainty discussion

---

## Project Structure

```
hanoi_ntl_analysis/
├── config.py                          # Configuration & parameters
├── requirements.txt                   # Python dependencies
├── notebooks/
│   └── 00_hanoi_ntl_analysis.ipynb   # Main analysis notebook
├── scripts/
│   ├── 01_download_viirs.py          # GEE data download script
│   └── ntl_processing.py             # Core processing functions
├── data/
│   ├── viirs_raw/                    # Downloaded VIIRS GeoTIFF files
│   ├── viirs_processed/              # Processed annual composites
│   └── validation/                   # High-res validation data
└── outputs/
    ├── *.png                         # Figures & visualizations
    ├── *.csv                         # Results tables
    └── *.txt                         # Reports
```

---

## Quick Start

### 1. Environment Setup
```bash
cd hanoi_ntl_analysis
pip install -r requirements.txt
```

### 2. Google Earth Engine Authentication
```bash
earthengine authenticate
# Follow browser prompt to authorize your account
```

### 3. Download VIIRS Data
```bash
python scripts/01_download_viirs.py
```
- Exports 144 monthly composites (2012-2023) to your Google Drive
- Files: `VIIRS_DNB_{YEAR}_{MONTH}.tif`
- **Download from Drive and place in `data/viirs_raw/`**

### 4. Run Analysis
Open and execute the Jupyter notebook:
```bash
jupyter notebook notebooks/00_hanoi_ntl_analysis.ipynb
```

---

## Methodology

### Data Selection: VCMCFG (VCMC Fixed Gain)

**Why VCMCFG?**
- **Calibration**: Fixed-gain approach ensures temporal consistency
- **Stability**: Recommended by NOAA for multi-year trend analysis
- **Temporal coverage**: Available for full 2012-2023 period
- **Quality**: Includes cloud masking and stray-light filtering

**Alternative datasets considered**:
- VNCCFG: Better for faint lights, but less stable over time
- VCMSLV: Highest quality, but only available 2015+

### NTL Threshold Selection: DN > 3.0

**Justification** (based on peer-reviewed literature):
1. **NOAA recommendations**: DN > 3 for dense urban cores
2. **Reference studies**:
   - Jing et al. (2016): DN > 3 for urban classification in SE Asia
   - Li et al. (2019): DN > 2-3 for Southeast Asian cities
3. **Hanoi context**: 
   - Tropical monsoon climate → higher atmospheric noise
   - Mix of development patterns → threshold balances sensitivity & specificity
4. **Validation**: Sensitivity analysis tests DN > 1, 2, 3, 5

### Expansion Metrics

#### Total Lit Area (km²)
```
Area = Σ(pixels where DN > threshold) × pixel_size²
```
- Pixel size: 463m (VIIRS native resolution)
- Represents total extent of urban lights

#### Annual Growth Rate (%)
```
Growth_Rate(year) = [(Area_year - Area_year-1) / Area_year-1] × 100
```

#### Compactness Index
```
Compactness = (4π × Area) / Perimeter²
```
- Range: 0-1 (1 = perfectly compact circle)
- Indicates clustering vs. dispersed urban sprawl

### Spatial Analysis

#### Centroid-Shift Analysis
- Find center-of-mass (lit area weighted)
- Track displacement year-over-year
- Indicates direction of urban center migration

#### Ring-wise Analysis
- Concentric buffers from city center
  - Ring 0: Core (< 1 km)
  - Ring 1: Inner (1-3 km)
  - Ring 2: Outer (3-8 km)
- Quantify expansion in each ring
- Identifies inward vs. outward growth pattern

#### Directional (Sectoral) Analysis
- Divide city into 8 octants (45° sectors)
- Calculate lit area in each sector
- Identify preferential expansion directions
- (N, NE, E, SE, S, SW, W, NW)

---

## Validation Strategy

### Comparison with High-Resolution Imagery

**Data sources** (2022 validation year):
1. **Sentinel-2 MSI** (10m, freely available)
   - Compute NDBI: (SWIR - NIR) / (SWIR + NIR)
   - NDBI > 0.1 indicates built-up areas

2. **Landsat 8/9 OLI** (30m)
   - NDBI from bands 6 & 5
   - NDVI for vegetation filtering

**Accuracy metrics**:
- Confusion Matrix (TP, TN, FP, FN)
- Overall Accuracy = (TP + TN) / Total
- Producer's Accuracy (sensitivity)
- User's Accuracy (precision)
- Kappa coefficient

**Expected results**: > 85% overall agreement acceptable for NTL studies

### Uncertainty Sources

1. **Spatial resolution**: VIIRS 463m vs. actual boundaries
2. **Temporal mismatch**: Monthly composites may mask short-term variation
3. **Threshold selection**: Tested via sensitivity analysis
4. **Atmospheric effects**: Seasonal cloud cover (monsoon season)
5. **Sensor artifacts**: Stray light, gain variations (mitigated by VCMCFG)

---

## Key Parameters (config.py)

| Parameter | Value | Justification |
|-----------|-------|---|
| Study Period | 2012-2023 | Full VIIRS availability |
| Analysis Region | Hanoi Municipality | Administrative boundary |
| NTL Threshold | DN > 3.0 | Urban core classification |
| Sensitivity Tests | DN > 1, 2, 3, 5 | Robustness assessment |
| Pixel Size | 463 m | VIIRS native resolution |
| Output CRS | EPSG:32648 (UTM 48N) | Local projection for Hanoi |
| Ring Widths | 1, 2, 5 km | Ring-wise analysis |
| Directional Sectors | 8 octants | Comprehensive directional analysis |

---

## Expected Outputs

### Figures
- `hanoi_ntl_timeseries.png` — Lit area, growth rate, compactness trends
- `hanoi_ntl_2023_comparison.png` — Raw DNB vs. urban mask side-by-side
- `spatial_analysis_maps.png` — Ring and sectoral expansion patterns
- `validation_accuracy_matrix.png` — Confusion matrix & metrics
- Annual comparison figures (2012, 2015, 2018, 2023)

### Data Tables
- `time_series_metrics.csv` — Year, lit area, growth rate, compactness, centroid
- `spatial_analysis_results.csv` — Ring and sector breakdown by year
- `validation_report.txt` — Accuracy metrics and uncertainty discussion
- `sensitivity_analysis.csv` — Results for multiple thresholds

### GeoTIFF Products
- `annual_composite_{year}.tif` — Processed VIIRS DNB data
- `urban_mask_{year}.tif` — Binary urban classification (DN > 3)

---

## References

### Key Literature
1. **Jing, X., Shao, X., Cao, C., et al. (2016)**. "Validation of the VIIRS Day/Night Band against litterae-derived lights in China." Remote Sensing, 8(2), 142.

2. **Li, X., Ge, X., Chen, H., et al. (2019**). "Assessing the relationship between nighttime light intensity and population density in three megacities." Science of The Total Environment, 684, 102-113.

3. **Elvidge, C. D., Baugh, K., Zhizhin, M., et al. (2017)** "VIIRS night-time lights." International Journal of Remote Sensing, 38(21), 5860-5879.

4. **NASA Earth Observatory Black Marble** https://earthobservatory.nasa.gov/images/category/nighttime-lights

### Data Documentation
- **NOAA VIIRS DNB**: https://ncc.nesdis.noaa.gov/products/black-marble-monthly-nighttime-lights
- **Google Earth Engine Catalog**: https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG

---

## Requirements

- **Python** ≥ 3.8
- **Google Earth Engine** API (with authenticated account)
- **Key libraries**: geopandas, rasterio, xarray, rioxarray, scikit-image, scipy

See `requirements.txt` for complete list.

---

## Troubleshooting

### GEE Authentication Issues
```bash
earthengine authenticate
# If still failing, clear cache:
rm -rf ~/.config/earthengine/
earthengine authenticate
```

### Missing VIIRS Data
- Verify files downloaded from Google Drive to `data/viirs_raw/`
- Check filename format: `VIIRS_DNB_{YEAR}_{MONTH}.tif`
- Ensure GeoTIFF files are valid: `gdalinfo VIIRS_DNB_2023_01.tif`

### Memory Issues with Large Rasters
- Process one year at a time instead of full time series
- Use xarray with dask for chunked processing
- Reduce spatial resolution if needed

---

## Contact & Citation

**Project**: Hanoi NTL Time Series Analysis (2012-2023)  
**Data Source**: NOAA VIIRS DNB Monthly V1.0 via Google Earth Engine  
**Analysis Period**: January 2024

For questions or issues, see the main project notebook.

---

**Last Updated**: January 9, 2026
