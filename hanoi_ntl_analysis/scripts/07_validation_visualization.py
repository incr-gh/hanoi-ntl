"""
Validation Visualization: Side-by-side comparison of VIIRS masks vs Landsat NDBI.

Generates comprehensive figures showing:
  - Raw Landsat NDBI with color scale
  - VIIRS urban mask overlay
  - Joint classification (agreement/disagreement)
  - Histograms of NDBI distribution
"""
import sys
from pathlib import Path
import logging
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.gridspec import GridSpec

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import NTL_THRESHOLD

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def match_spatial_extent(viirs_arr, landsat_arr):
    """Resample Landsat (30m) to VIIRS (463m) grid via block averaging."""
    downsample = 15  # ~463m / 30m ≈ 15
    
    h, w = landsat_arr.shape
    new_h = h // downsample
    new_w = w // downsample
    
    landsat_ds = np.zeros((new_h, new_w), dtype=np.float32)
    for i in range(new_h):
        for j in range(new_w):
            block = landsat_arr[i*downsample:(i+1)*downsample, j*downsample:(j+1)*downsample]
            landsat_ds[i, j] = np.nanmean(block)
    
    logger.info(f"Resampled Landsat from {landsat_arr.shape} to {landsat_ds.shape}")
    
    # Crop to common extent
    h = min(viirs_arr.shape[0], landsat_ds.shape[0])
    w = min(viirs_arr.shape[1], landsat_ds.shape[1])
    
    return viirs_arr[:h, :w], landsat_ds[:h, :w]


def create_joint_classification(viirs_mask, landsat_ndbi, ndbi_threshold=0.1):
    """
    Create joint classification map:
    0 = Both non-urban
    1 = VIIRS only (false positive)
    2 = Landsat only (false negative)
    3 = Both urban (agreement)
    """
    landsat_mask = (landsat_ndbi >= ndbi_threshold).astype(np.uint8)
    
    joint = np.zeros_like(viirs_mask, dtype=np.uint8)
    joint[(viirs_mask == 0) & (landsat_mask == 0)] = 0  # Both non-urban
    joint[(viirs_mask == 1) & (landsat_mask == 0)] = 1  # VIIRS only (FP)
    joint[(viirs_mask == 0) & (landsat_mask == 1)] = 2  # Landsat only (FN)
    joint[(viirs_mask == 1) & (landsat_mask == 1)] = 3  # Both urban (TP)
    
    return joint


def main():
    root = Path(__file__).parent.parent
    landsat_dir = root / 'data' / 'landsat_raw'
    masks_dir = root / 'outputs' / 'viirs_masks'
    out_dir = root / 'outputs'
    
    # Find Landsat file
    landsat_files = sorted(landsat_dir.glob('*.tif'))
    if not landsat_files:
        logger.error('No Landsat TIFFs found in data/landsat_raw/')
        return
    
    landsat_file = landsat_files[0]
    
    # Parse year
    import re
    m = re.search(r'(\d{4})', landsat_file.name)
    validation_year = int(m.group(0)) if m else 2023
    
    logger.info(f'Validation year: {validation_year}')
    
    # Find VIIRS mask
    viirs_mask_file = masks_dir / f'VIIRS_{validation_year}_mask.tif'
    if not viirs_mask_file.exists():
        logger.error(f'VIIRS mask not found for {validation_year}')
        return
    
    # Read data
    logger.info(f'Reading Landsat: {landsat_file.name}')
    with rasterio.open(landsat_file) as src:
        landsat_ndbi = src.read(1).astype(np.float32)
    
    logger.info(f'Reading VIIRS mask: {viirs_mask_file.name}')
    with rasterio.open(viirs_mask_file) as src:
        viirs_mask = src.read(1).astype(np.uint8)
    
    # Align extents
    viirs_mask, landsat_ndbi = match_spatial_extent(viirs_mask, landsat_ndbi)
    
    # Create joint classification
    joint_class = create_joint_classification(viirs_mask, landsat_ndbi, ndbi_threshold=0.1)
    
    # Figure 1: Side-by-side comparison
    logger.info('Creating Figure 1: Side-by-side comparison...')
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # Panel A: Landsat NDBI (with percentile-based scaling)
    ax1 = fig.add_subplot(gs[0:2, 0])
    ndbi_valid = landsat_ndbi[~np.isnan(landsat_ndbi)]
    vmin_ndbi = np.percentile(ndbi_valid, 2)
    vmax_ndbi = np.percentile(ndbi_valid, 98)
    im1 = ax1.imshow(landsat_ndbi, cmap='viridis', origin='upper', vmin=vmin_ndbi, vmax=vmax_ndbi)
    ax1.contour(landsat_ndbi, levels=[0.1], colors='red', linewidths=2, alpha=0.8)
    ax1.set_title(f'Landsat NDBI ({validation_year})\n2%-98% scale', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Pixels (X)')
    ax1.set_ylabel('Pixels (Y)')
    cbar1 = plt.colorbar(im1, ax=ax1, label='NDBI Value')
    cbar1.ax.text(0.5, 0.05, f'Threshold: 0.1', ha='center', fontsize=9, color='red', fontweight='bold',
                 transform=cbar1.ax.transAxes, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))
    
    # Panel B: VIIRS Mask
    ax2 = fig.add_subplot(gs[0:2, 1])
    im2 = ax2.imshow(viirs_mask, cmap='binary', origin='upper', vmin=0, vmax=1)
    ax2.set_title(f'VIIRS Urban Mask (DN > {NTL_THRESHOLD})', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Pixels (X)')
    ax2.set_ylabel('Pixels (Y)')
    plt.colorbar(im2, ax=ax2, label='Urban (1) / Non-urban (0)')
    
    # Panel C: Joint Classification
    ax3 = fig.add_subplot(gs[0:2, 2])
    cmap_joint = ListedColormap(['white', 'red', 'blue', 'green'])
    im3 = ax3.imshow(joint_class, cmap=cmap_joint, origin='upper', vmin=0, vmax=3)
    ax3.set_title('Joint Classification', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Pixels (X)')
    ax3.set_ylabel('Pixels (Y)')
    
    # Custom legend for joint classification
    legend_elements = [
        mpatches.Patch(facecolor='white', edgecolor='black', label='Both non-urban'),
        mpatches.Patch(facecolor='red', label='VIIRS only (False Positive)'),
        mpatches.Patch(facecolor='blue', label='Landsat only (False Negative)'),
        mpatches.Patch(facecolor='green', label='Both urban (Agreement)')
    ]
    ax3.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    # Panel D: Landsat NDBI histogram
    ax4 = fig.add_subplot(gs[2, 0])
    ndbi_valid = landsat_ndbi[~np.isnan(landsat_ndbi)]
    ax4.hist(ndbi_valid, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    ax4.axvline(0.1, color='red', linestyle='--', linewidth=2, label='Threshold (0.1)')
    ax4.set_xlabel('NDBI Value')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Landsat NDBI Distribution', fontsize=11, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Panel E: VIIRS mask histogram
    ax5 = fig.add_subplot(gs[2, 1])
    urban_pixels = np.sum(viirs_mask == 1)
    non_urban_pixels = np.sum(viirs_mask == 0)
    ax5.bar(['Non-urban', 'Urban'], [non_urban_pixels, urban_pixels], color=['gray', 'darkred'], alpha=0.7, edgecolor='black')
    ax5.set_ylabel('Pixel Count')
    ax5.set_title('VIIRS Mask Distribution', fontsize=11, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Panel F: Agreement summary
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    TP = np.sum(joint_class == 3)
    FP = np.sum(joint_class == 1)
    FN = np.sum(joint_class == 2)
    TN = np.sum(joint_class == 0)
    total = TP + FP + FN + TN
    
    OA = (TP + TN) / total if total > 0 else 0
    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    
    summary_text = f"""VALIDATION SUMMARY

Confusion Matrix:
  TP (Agreement):    {TP:5d}
  FP (VIIRS only):   {FP:5d}
  FN (Landsat only): {FN:5d}
  TN (Both non-u):   {TN:5d}

Metrics:
  Overall Accuracy:  {OA:.3f}
  Sensitivity:       {sensitivity:.3f}
  Precision:         {precision:.3f}
  
Datasets:
  VIIRS year: {validation_year}
  Landsat year: {validation_year}
  VIIRS threshold: DN > {NTL_THRESHOLD}
  Landsat threshold: NDBI > 0.1
"""
    
    ax6.text(0.1, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle(f'VIIRS NTL vs Landsat NDBI Validation ({validation_year})', 
                fontsize=14, fontweight='bold', y=0.995)
    
    fig.savefig(out_dir / 'validation_comparison_figure.png', dpi=300, bbox_inches='tight')
    logger.info('Saved: validation_comparison_figure.png')
    plt.close()
    
    # Figure 2: Detailed NDBI distribution with overlay
    logger.info('Creating Figure 2: NDBI with VIIRS mask overlay...')
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: NDBI with percentile-based scaling
    ax = axes[0]
    ndbi_valid = landsat_ndbi[~np.isnan(landsat_ndbi)]
    vmin_ndbi = np.percentile(ndbi_valid, 2)
    vmax_ndbi = np.percentile(ndbi_valid, 98)
    im = ax.imshow(landsat_ndbi, cmap='viridis', origin='upper', vmin=vmin_ndbi, vmax=vmax_ndbi)
    ax.set_title('Landsat NDBI (2%-98% scale)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Pixels (X)')
    ax.set_ylabel('Pixels (Y)')
    cbar = plt.colorbar(im, ax=ax, label='NDBI Value')
    cbar.ax.text(0.5, 0.05, f'Threshold: 0.1', ha='center', fontsize=9, color='red', fontweight='bold',
                transform=cbar.ax.transAxes, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))
    
    # Right: NDBI with VIIRS mask contour (same scaling)
    ax = axes[1]
    im = ax.imshow(landsat_ndbi, cmap='viridis', origin='upper', vmin=vmin_ndbi, vmax=vmax_ndbi)
    # Overlay VIIRS urban mask as red contour
    ax.contour(viirs_mask, levels=[0.5], colors='red', linewidths=2.5, alpha=0.9)
    ax.set_title('Landsat NDBI with VIIRS Urban Boundary (red)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Pixels (X)')
    ax.set_ylabel('Pixels (Y)')
    plt.colorbar(im, ax=ax, label='NDBI Value')
    
    plt.tight_layout()
    fig.savefig(out_dir / 'validation_ndbi_with_viirs_outline.png', dpi=300, bbox_inches='tight')
    logger.info('Saved: validation_ndbi_with_viirs_outline.png')
    plt.close()
    
    logger.info('✓ Validation visualization complete.')


if __name__ == '__main__':
    main()
