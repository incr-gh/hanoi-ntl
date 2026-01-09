"""
Core NTL processing and analysis functions
"""

import numpy as np
import rasterio
from rasterio.mask import mask
from pathlib import Path
from scipy import ndimage
from skimage.measure import label, regionprops
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def read_viirs_tif(filepath):
    """Read VIIRS GeoTIFF and return data with metadata."""
    with rasterio.open(filepath) as src:
        data = src.read(1)  # Read first band (avg_dnb)
        meta = src.meta.copy()
        bounds = src.bounds
    return data, meta, bounds

def create_urban_mask(viirs_data, threshold=3.0):
    """
    Create binary urban mask from VIIRS DNB data.
    
    Parameters:
    -----------
    viirs_data : ndarray
        VIIRS DNB values
    threshold : float
        DN threshold for urban classification
        
    Returns:
    --------
    urban_mask : ndarray
        Binary mask (1 = urban lit, 0 = not urban)
    """
    # Create initial mask
    mask = viirs_data >= threshold
    
    # Remove small isolated pixels (morphological cleaning)
    from scipy.ndimage import binary_opening
    urban_mask = binary_opening(mask, structure=np.ones((3, 3)))
    
    return urban_mask.astype(np.uint8)

def calculate_lit_area(urban_mask, pixel_size_m=463):
    """
    Calculate lit area in km².
    
    Parameters:
    -----------
    urban_mask : ndarray
        Binary urban mask
    pixel_size_m : float
        Pixel size in meters (VIIRS native ~463m)
        
    Returns:
    --------
    area_km2 : float
        Total lit area in square kilometers
    """
    pixel_count = np.sum(urban_mask)
    pixel_area_km2 = (pixel_size_m / 1000) ** 2
    area_km2 = pixel_count * pixel_area_km2
    return area_km2

def calculate_compactness(urban_mask):
    """
    Calculate urban compactness using isoperimetric ratio.
    Compactness = 4π * Area / Perimeter²
    Values closer to 1 indicate more compact shapes.
    
    Parameters:
    -----------
    urban_mask : ndarray
        Binary urban mask
        
    Returns:
    --------
    compactness : float
        Isoperimetric compactness ratio (0-1)
    """
    # Label connected components (skimage.measure.label returns the labeled array)
    labeled = label(urban_mask)
    regions = regionprops(labeled)
    if len(regions) == 0:
        return 0.0
    regions = sorted(regions, key=lambda x: x.area, reverse=True)
    largest_region = regions[0]
    
    area = largest_region.area
    perimeter = largest_region.perimeter
    
    if perimeter == 0:
        return 1.0
    
    compactness = (4 * np.pi * area) / (perimeter ** 2)
    return min(compactness, 1.0)  # Cap at 1.0

def find_centroid(urban_mask):
    """
    Find centroid of lit urban area.
    
    Parameters:
    -----------
    urban_mask : ndarray
        Binary urban mask
        
    Returns:
    --------
    centroid : tuple
        (row, col) coordinates of centroid
    """
    y, x = np.where(urban_mask > 0)
    if len(x) == 0:
        return None
    centroid = (np.mean(y), np.mean(x))
    return centroid

def analyze_directional_expansion(urban_mask, centroid, num_sectors=8):
    """
    Analyze expansion patterns in different directions (sectors).
    
    Parameters:
    -----------
    urban_mask : ndarray
        Binary urban mask
    centroid : tuple
        (row, col) centroid coordinates
    num_sectors : int
        Number of directional sectors (8 for octants)
        
    Returns:
    --------
    sector_areas : dict
        Area in each sector
    """
    if centroid is None:
        return {}
    
    cy, cx = centroid
    labeled, _ = label(urban_mask)
    h, w = urban_mask.shape
    
    sector_areas = {}
    angle_step = 360 / num_sectors
    
    # Create angle map
    y, x = np.ogrid[:h, :w]
    angles = np.arctan2(y - cy, x - cx) * 180 / np.pi
    angles = (angles + 180) % 360  # Convert to 0-360
    
    for sector in range(num_sectors):
        angle_min = sector * angle_step
        angle_max = angle_min + angle_step
        
        if angle_max > 360:
            sector_mask = (angles >= angle_min) | (angles < (angle_max % 360))
        else:
            sector_mask = (angles >= angle_min) & (angles < angle_max)
        
        sector_lit = urban_mask * sector_mask
        sector_areas[f'Sector_{sector}'] = np.sum(sector_lit)
    
    return sector_areas

def analyze_ring_expansion(urban_mask, centroid, ring_widths=[1000, 2000, 5000], pixel_size_m=463):
    """
    Analyze expansion patterns by concentric rings.
    
    Parameters:
    -----------
    urban_mask : ndarray
        Binary urban mask
    centroid : tuple
        (row, col) centroid coordinates
    ring_widths : list
        Ring widths in meters
    pixel_size_m : float
        Pixel size in meters
        
    Returns:
    --------
    ring_areas : dict
        Area in each ring
    """
    if centroid is None:
        return {}
    
    cy, cx = centroid
    h, w = urban_mask.shape
    
    # Create distance map from centroid
    y, x = np.ogrid[:h, :w]
    distances = np.sqrt((y - cy)**2 + (x - cx)**2) * pixel_size_m
    
    ring_areas = {}
    prev_dist = 0
    
    for ring_width in ring_widths:
        ring_dist = prev_dist + ring_width
        ring_mask = (distances >= prev_dist) & (distances < ring_dist)
        ring_lit = urban_mask * ring_mask
        ring_areas[f'Ring_{prev_dist}-{ring_dist}m'] = np.sum(ring_lit)
        prev_dist = ring_dist
    
    # Include core area (within first ring_width)
    core_mask = distances < ring_widths[0]
    core_lit = urban_mask * core_mask
    ring_areas['Core'] = np.sum(core_lit)
    
    return ring_areas

def sensitivity_analysis(viirs_data, thresholds=[1.0, 2.0, 3.0, 5.0], pixel_size_m=463):
    """
    Perform sensitivity analysis across multiple thresholds.
    
    Parameters:
    -----------
    viirs_data : ndarray
        VIIRS DNB values
    thresholds : list
        List of DN thresholds to test
    pixel_size_m : float
        Pixel size in meters
        
    Returns:
    --------
    sensitivity_df : DataFrame
        Results for each threshold
    """
    results = []
    
    for threshold in thresholds:
        mask = create_urban_mask(viirs_data, threshold)
        area = calculate_lit_area(mask, pixel_size_m)
        compactness = calculate_compactness(mask)
        
        results.append({
            'threshold': threshold,
            'lit_area_km2': area,
            'compactness': compactness,
            'pixel_count': np.sum(mask)
        })
    
    return pd.DataFrame(results)

def export_geotiff(data, meta, output_path):
    """Export array as GeoTIFF."""
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(data, 1)
    logger.info(f"Exported: {output_path}")
