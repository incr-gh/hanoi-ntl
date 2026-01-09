"""
Configuration for Hanoi NTL Analysis Project
"""

# Geographic bounds for Hanoi municipality (WGS84)
# Based on official Hanoi administrative boundaries
HANOI_BOUNDS = {
    'north': 21.1537,
    'south': 20.8403,
    'east': 105.8863,
    'west': 104.6762,
}

# Alternative: GeoJSON polygon for precise boundary
# Use this if available: Hanoi_municipality_boundary.geojson

# VIIRS DNB Analysis Parameters
ANALYSIS_YEARS = list(range(2012, 2024))  # 2012-2023 inclusive
STUDY_PERIOD = (2012, 2023)

# NTL THRESHOLD JUSTIFICATION
# Based on literature review and Hanoi context:
# - DNB values range from 0-80 nanoWatts/cm²/sr in raw data
# - Urban lit areas typically > 2-3 in annual composites
# - Threshold selection: DN > 3 (conservatively captures urban lights, filters noise)
# References:
#   1. Jing et al. (2016): DN > 1 for lights detection, DN > 3 for urban areas
#   2. NASA's NOAA VIIRS documentation: DN > 2-5 recommended for urban mapping
#   3. Hanoi context: tropical monsoon with atmospheric interference requires higher threshold
#   4. Sensitivity analysis: test DN > 1, 2, 3, 5 to assess robustness

NTL_THRESHOLD = 3.0  # Primary threshold for urban lit area detection
NTL_SENSITIVITY_THRESHOLDS = [1.0, 2.0, 3.0, 5.0]  # For sensitivity analysis

# Spatial analysis parameters
MINIMUM_CLUSTER_SIZE = 9  # pixels (3x3) to filter noise
RING_WIDTHS = [1000, 2000, 5000]  # meters from city center
SECTORAL_DIVISIONS = 8  # octants for directional analysis

# Output settings
OUTPUT_CRS = 'EPSG:32648'  # UTM Zone 48N (appropriate for Hanoi)
OUTPUT_RESOLUTION = 463  # meters (VIIRS native resolution ~500m)

# Validation
VALIDATION_SOURCES = {
    'sentinel2': True,      # Use Sentinel-2 for comparison
    'landsat8': True,       # Use Landsat 8/9 for comparison
    'period': 2022,         # Latest year available for all sources
}

# Visualization
FIGURE_DPI = 300
CMAP_NTL = 'hot'  # Colormap for NTL visualization
CMAP_BINARY = 'RdYlBu_r'  # For binary urban mask
