"""
Spatial Analysis: Ring-wise, Directional, and Centroid-shift Analysis
Performs detailed characterization of urban growth patterns
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import ndimage
from skimage.measure import label, regionprops
import sys

# Ensure project root is on path so `config` imports reliably
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RING_WIDTHS, SECTORAL_DIVISIONS
from ntl_processing import find_centroid, calculate_lit_area

def compute_centroid_shift(centroids_by_year):
    """
    Compute centroid displacement over time.
    
    Parameters:
    -----------
    centroids_by_year : dict
        {year: (row, col)} mapping
        
    Returns:
    --------
    displacement_df : DataFrame
        Year-to-year displacement metrics
    """
    years = sorted(centroids_by_year.keys())
    results = []
    
    for i in range(1, len(years)):
        year1 = years[i-1]
        year2 = years[i]
        
        c1 = centroids_by_year[year1]
        c2 = centroids_by_year[year2]
        
        if c1 is None or c2 is None:
            continue
        
        # Compute displacement (in pixels, then meters)
        dy = c2[0] - c1[0]
        dx = c2[1] - c1[1]
        
        # Convert to meters (assuming 463m pixel size)
        pixel_size_m = 463
        displacement_m = np.sqrt((dy * pixel_size_m)**2 + (dx * pixel_size_m)**2)
        
        # Compute direction (bearing from north)
        # atan2(dx, dy) gives angle from north (0°) clockwise
        bearing = (np.arctan2(dx, dy) * 180 / np.pi) % 360
        
        results.append({
            'year_from': year1,
            'year_to': year2,
            'displacement_m': displacement_m,
            'bearing_degrees': bearing,
            'direction': get_direction_name(bearing)
        })
    
    return pd.DataFrame(results)

def get_direction_name(bearing):
    """Convert bearing (0-360°) to compass direction."""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    idx = int((bearing + 11.25) / 22.5) % 16
    return directions[idx]

def analyze_ring_expansion(urban_mask, centroid, ring_widths=[1000, 2000, 5000], 
                          pixel_size_m=463, year=None):
    """
    Analyze expansion patterns by concentric rings.
    
    Returns:
    --------
    ring_stats : DataFrame
        Area and percentage in each ring
    """
    if centroid is None:
        return None
    
    cy, cx = centroid
    h, w = urban_mask.shape
    
    # Create distance map from centroid
    y, x = np.ogrid[:h, :w]
    distances = np.sqrt((y - cy)**2 + (x - cx)**2) * pixel_size_m
    
    results = []
    total_area = calculate_lit_area(urban_mask, pixel_size_m)
    
    # Core area
    core_mask = distances < ring_widths[0]
    core_lit = urban_mask * core_mask
    core_area = calculate_lit_area(core_lit, pixel_size_m)
    
    results.append({
        'ring': 'Core',
        'distance_m': f'< {ring_widths[0]}',
        'area_km2': core_area,
        'percent_of_total': (core_area / total_area * 100) if total_area > 0 else 0
    })
    
    # Concentric rings
    prev_dist = ring_widths[0]
    for ring_width in ring_widths[1:]:
        ring_dist = prev_dist + ring_width
        ring_mask = (distances >= prev_dist) & (distances < ring_dist)
        ring_lit = urban_mask * ring_mask
        ring_area = calculate_lit_area(ring_lit, pixel_size_m)
        
        results.append({
            'ring': f'Ring {prev_dist/1000:.0f}-{ring_dist/1000:.0f}km',
            'distance_m': f'{prev_dist:.0f}-{ring_dist:.0f}',
            'area_km2': ring_area,
            'percent_of_total': (ring_area / total_area * 100) if total_area > 0 else 0
        })
        prev_dist = ring_dist
    
    df = pd.DataFrame(results)
    if year:
        df['year'] = year
    
    return df

def analyze_directional_expansion(urban_mask, centroid, num_sectors=8, 
                                  pixel_size_m=463, year=None):
    """
    Analyze expansion patterns by compass direction (sectors).
    
    Returns:
    --------
    sector_stats : DataFrame
        Area in each directional sector
    """
    if centroid is None:
        return None
    
    cy, cx = centroid
    h, w = urban_mask.shape
    
    # Create angle map
    y, x = np.ogrid[:h, :w]
    angles = np.arctan2(x - cx, y - cy) * 180 / np.pi
    angles = (angles + 180) % 360  # Convert to 0-360
    
    results = []
    total_area = calculate_lit_area(urban_mask, pixel_size_m)
    
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    angle_step = 360 / num_sectors
    
    for sector in range(num_sectors):
        angle_min = sector * angle_step
        angle_max = angle_min + angle_step
        
        if angle_max > 360:
            sector_mask = (angles >= angle_min) | (angles < (angle_max % 360))
        else:
            sector_mask = (angles >= angle_min) & (angles < angle_max)
        
        sector_lit = urban_mask * sector_mask
        sector_area = calculate_lit_area(sector_lit, pixel_size_m)
        
        # Map sector number to direction name
        dir_idx = int(sector * 16 / num_sectors) % 16
        direction = directions[dir_idx]
        
        results.append({
            'sector': sector,
            'direction': direction,
            'angle_min': angle_min,
            'angle_max': angle_max,
            'area_km2': sector_area,
            'percent_of_total': (sector_area / total_area * 100) if total_area > 0 else 0
        })
    
    df = pd.DataFrame(results)
    if year:
        df['year'] = year
    
    return df

def visualize_ring_analysis(ring_results_by_year):
    """Create visualization of ring-wise expansion over time."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Stacked area plot
    df = pd.concat(ring_results_by_year, ignore_index=True)
    pivot_df = df.pivot_table(values='area_km2', index='year', columns='ring')
    
    ax = axes[0]
    pivot_df.plot(kind='area', stacked=True, ax=ax, alpha=0.7)
    ax.set_xlabel('Year')
    ax.set_ylabel('Lit Area (km²)')
    ax.set_title('Ring-wise Urban Expansion Over Time')
    ax.legend(title='Ring', loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Percentage stacked bar
    ax = axes[1]
    pivot_pct = df.pivot_table(values='percent_of_total', index='year', columns='ring')
    pivot_pct.plot(kind='bar', stacked=True, ax=ax, alpha=0.7)
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage of Total Lit Area (%)')
    ax.set_title('Ring Distribution Evolution')
    ax.legend(title='Ring', loc='upper right', fontsize=8)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def visualize_directional_analysis(sector_results_by_year, year=None):
    """Create polar/rose diagram of directional expansion."""
    df = pd.concat(sector_results_by_year, ignore_index=True)
    
    if year:
        df = df[df['year'] == year]
    else:
        # Use most recent year
        df = df[df['year'] == df['year'].max()]
    
    # Create polar plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Convert angles to radians
    angles_rad = np.radians(df['angle_min'].values)
    width = np.radians(360 / len(df))
    
    # Create bar chart
    bars = ax.bar(angles_rad, df['area_km2'].values, width=width, 
                   alpha=0.7, edgecolor='black')
    
    # Color by direction
    colors = plt.cm.hsv(np.linspace(0, 1, len(df)))
    for bar, color in zip(bars, colors):
        bar.set_facecolor(color)
    
    # Set labels
    ax.set_theta_offset(np.pi / 2)  # North at top
    ax.set_theta_direction(-1)  # Clockwise
    ax.set_xticks(angles_rad)
    ax.set_xticklabels(df['direction'].values)
    ax.set_ylabel('Lit Area (km²)')
    ax.set_title(f'Directional Urban Expansion Pattern ({df.iloc[0]["year"]})')
    
    return fig

if __name__ == '__main__':
    print("""
    Spatial Analysis Module
    
    Functions available:
    - compute_centroid_shift(): Year-to-year centroid displacement
    - analyze_ring_expansion(): Area by concentric rings
    - analyze_directional_expansion(): Area by compass direction (sectors)
    - visualize_ring_analysis(): Create ring visualization
    - visualize_directional_analysis(): Create polar plot
    
    Import and use in main analysis notebook:
    from spatial_analysis import *
    """)
