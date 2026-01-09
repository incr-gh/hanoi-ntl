"""
Run spatial analyses (ring-wise, directional, centroid shift) on masks
created in `outputs/viirs_masks/` and save CSVs/plots to `outputs/`.
"""
from pathlib import Path
import logging
import rasterio
import numpy as np
import pandas as pd

from spatial_analysis import (
    analyze_ring_expansion, analyze_directional_expansion,
    compute_centroid_shift, visualize_ring_analysis, visualize_directional_analysis
)
from ntl_processing import find_centroid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_spatial_on_masks():
    root = Path(__file__).parent.parent
    masks_dir = root / 'outputs' / 'viirs_masks'
    out_dir = root / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)

    mask_files = sorted(masks_dir.glob('*_mask.tif'))
    if not mask_files:
        logger.error('No masks found in outputs/viirs_masks/. Run scripts/03_process_samples.py first.')
        return

    ring_results = []
    sector_results = []
    centroids = {}

    for mf in mask_files:
        logger.info(f'Analyzing mask: {mf.name}')
        # parse year from filename like VIIRS_DNB_2012_05_mask.tif
        parts = mf.stem.split('_')
        year = None
        for p in parts:
            if p.isdigit() and len(p) == 4:
                year = int(p)
                break

        with rasterio.open(mf) as src:
            arr = src.read(1).astype(np.uint8)

        centroid = find_centroid(arr)
        centroids[year] = centroid

        ring_df = analyze_ring_expansion(arr, centroid, year=year)
        if ring_df is not None:
            ring_results.append(ring_df)

        sector_df = analyze_directional_expansion(arr, centroid, num_sectors=8, year=year)
        if sector_df is not None:
            sector_results.append(sector_df)

    # Combine and save
    if ring_results:
        ring_combined = pd.concat(ring_results, ignore_index=True)
        ring_csv = out_dir / 'spatial_analysis_rings_samples.csv'
        ring_combined.to_csv(ring_csv, index=False)
        logger.info(f'Saved ring CSV: {ring_csv.name}')
        # plot
        fig = visualize_ring_analysis(ring_results)
        fig.savefig(out_dir / 'spatial_analysis_rings_samples.png', dpi=300, bbox_inches='tight')
        logger.info('Saved ring plot')

    if sector_results:
        sector_combined = pd.concat(sector_results, ignore_index=True)
        sector_csv = out_dir / 'spatial_analysis_directional_samples.csv'
        sector_combined.to_csv(sector_csv, index=False)
        logger.info(f'Saved sector CSV: {sector_csv.name}')
        # plot most recent year
        latest_year = sector_combined['year'].max()
        fig = visualize_directional_analysis(sector_results, year=latest_year)
        fig.savefig(out_dir / 'spatial_analysis_directional_samples.png', dpi=300, bbox_inches='tight')
        logger.info('Saved sector plot')

    # Centroid shift
    cent_df = compute_centroid_shift(centroids)
    cent_csv = out_dir / 'centroid_shift_samples.csv'
    cent_df.to_csv(cent_csv, index=False)
    logger.info(f'Saved centroid shift CSV: {cent_csv.name}')


if __name__ == '__main__':
    run_spatial_on_masks()
