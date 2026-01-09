"""
Run full Hanoi NTL analysis over all VIIRS GeoTIFFs in `data/viirs_raw/`.

This single script performs the following steps:
  - Reads all GeoTIFFs in `data/viirs_raw/` and groups them by year
  - Builds annual median composites (per-pixel median, ignoring zero/no-data)
  - Creates binary urban masks using the threshold in `config.py`
  - Computes lit-area, compactness, centroid for each year
  - Runs ring-wise and directional analyses per year
  - Computes centroid shifts year-to-year
  - Saves masks, CSV summaries, plots and a validation report to `outputs/`

Assumptions:
  - Input TIFFs share the same crs/transform and pixel grid (typical for GEE exports).
  - Filenames include a 4-digit year (e.g., VIIRS_DNB_2012_05.tif). The script will log files that cannot be parsed.

Run example:
  C:/Users/anhmi/OneDrive/Documents/University/CRP2/.venv/Scripts/python.exe scripts/run_full_analysis.py
"""
from pathlib import Path
import re
import logging
import numpy as np
import pandas as pd
import rasterio

import sys
# ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ANALYSIS_YEARS, NTL_THRESHOLD, NTL_SENSITIVITY_THRESHOLDS
from ntl_processing import (
    read_viirs_tif, create_urban_mask, calculate_lit_area,
    calculate_compactness, find_centroid, export_geotiff, sensitivity_analysis
)
from spatial_analysis import (
    analyze_ring_expansion, analyze_directional_expansion,
    compute_centroid_shift, visualize_ring_analysis, visualize_directional_analysis
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('run_full_analysis')


def list_input_tifs(raw_dir: Path):
    files = sorted(raw_dir.glob('*.tif'))
    return files


def parse_year_from_name(name: str):
    m = re.search(r'(19|20)\d{2}', name)
    if m:
        return int(m.group(0))
    return None


def build_annual_composites(files):
    """Return {year: (array, meta)} map with per-year median composites."""
    by_year = {}
    meta_example = None

    for f in files:
        year = parse_year_from_name(f.name)
        if year is None:
            logger.warning(f'Could not parse year from filename: {f.name}; skipping')
            continue
        with rasterio.open(f) as src:
            arr = src.read(1).astype(float)
            m = src.meta.copy()
        if meta_example is None:
            meta_example = m

        # treat zeros as nodata for compositing (common in VIIRS exports)
        arr[arr == 0] = np.nan

        by_year.setdefault(year, []).append(arr)

    composites = {}
    for year, stacks in by_year.items():
        stack = np.stack(stacks, axis=0)
        # compute median ignoring nan
        comp = np.nanmedian(stack, axis=0)
        # replace nan back to 0 for storage/processing
        comp = np.where(np.isnan(comp), 0, comp)
        composites[year] = (comp, meta_example)
        logger.info(f'Built composite for year {year} (shape={comp.shape})')

    return composites


def run(composites: dict, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    masks_dir = out_dir / 'viirs_masks'
    masks_dir.mkdir(exist_ok=True)

    # Collect time series metrics
    metrics = []
    ring_results = []
    sector_results = []
    centroids = {}

    years = sorted(composites.keys())
    for year in years:
        arr, meta = composites[year]
        logger.info(f'Processing year {year}...')

        # Create mask
        mask = create_urban_mask(arr, threshold=NTL_THRESHOLD)

        # Metrics
        area_km2 = calculate_lit_area(mask)
        compactness = calculate_compactness(mask)
        centroid = find_centroid(mask)
        centroids[year] = centroid

        metrics.append({
            'year': year,
            'lit_area_km2': area_km2,
            'compactness': compactness,
            'centroid_row': centroid[0] if centroid else None,
            'centroid_col': centroid[1] if centroid else None
        })

        # Save mask geotiff
        mask_meta = meta.copy()
        mask_meta.update({'dtype': 'uint8', 'count': 1, 'compress': 'lzw'})
        mask_path = masks_dir / f'VIIRS_{year}_mask.tif'
        try:
            with rasterio.open(mask_path, 'w', **mask_meta) as dst:
                dst.write(mask.astype('uint8'), 1)
            logger.info(f'Wrote mask: {mask_path.name}')
        except Exception as e:
            logger.error(f'Failed to write mask for {year}: {e}')

        # Ring and sector analyses
        ring_df = analyze_ring_expansion(mask, centroid, year=year)
        if ring_df is not None:
            ring_results.append(ring_df)

        sector_df = analyze_directional_expansion(mask, centroid, num_sectors=8, year=year)
        if sector_df is not None:
            sector_results.append(sector_df)

        # Sensitivity (optional)
        sens_df = sensitivity_analysis(arr, thresholds=NTL_SENSITIVITY_THRESHOLDS)
        sens_df['year'] = year
        sens_path = out_dir / f'sensitivity_{year}.csv'
        sens_df.to_csv(sens_path, index=False)

    # Time series metrics
    metrics_df = pd.DataFrame(metrics).sort_values('year')
    metrics_df['annual_growth_pct'] = metrics_df['lit_area_km2'].pct_change() * 100
    metrics_csv = out_dir / 'time_series_metrics.csv'
    metrics_df.to_csv(metrics_csv, index=False)
    logger.info(f'Wrote metrics CSV: {metrics_csv.name}')

    # Spatial results
    if ring_results:
        ring_combined = pd.concat(ring_results, ignore_index=True)
        ring_csv = out_dir / 'spatial_analysis_rings.csv'
        ring_combined.to_csv(ring_csv, index=False)
        logger.info(f'Wrote ring CSV: {ring_csv.name}')
        # plot
        fig = visualize_ring_analysis(ring_results)
        fig.savefig(out_dir / 'spatial_analysis_rings.png', dpi=300, bbox_inches='tight')
        logger.info('Saved ring plot')

    if sector_results:
        sector_combined = pd.concat(sector_results, ignore_index=True)
        sector_csv = out_dir / 'spatial_analysis_directional.csv'
        sector_combined.to_csv(sector_csv, index=False)
        logger.info(f'Wrote sector CSV: {sector_csv.name}')
        # plot
        latest_year = sector_combined['year'].max()
        fig = visualize_directional_analysis(sector_results, year=latest_year)
        fig.savefig(out_dir / 'spatial_analysis_directional.png', dpi=300, bbox_inches='tight')
        logger.info('Saved sector plot')

    # Centroid shifts
    cent_df = compute_centroid_shift(centroids)
    cent_csv = out_dir / 'centroid_shift.csv'
    cent_df.to_csv(cent_csv, index=False)
    logger.info(f'Wrote centroid shift CSV: {cent_csv.name}')

    # Simple validation report (template)
    report_lines = []
    report_lines.append('Hanoi NTL Full Analysis Report')
    report_lines.append('Processed years: ' + ', '.join(map(str, years)))
    report_lines.append(f'Threshold used: DN > {NTL_THRESHOLD}')
    report_lines.append('Sensitivity CSVs: one per year (sensitivity_{year}.csv)')
    report_lines.append('\nTime series summary:')
    report_lines.append(metrics_df.to_string(index=False))

    report_path = out_dir / 'validation_and_summary_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    logger.info(f'Wrote report: {report_path.name}')


def main():
    root = Path(__file__).parent.parent
    raw_dir = root / 'data' / 'viirs_raw'
    out_dir = root / 'outputs'

    files = list_input_tifs(raw_dir)
    if not files:
        logger.error('No VIIRS TIFFs found in data/viirs_raw/. Place exported GeoTIFFs there and retry.')
        return

    comps = build_annual_composites(files)
    if not comps:
        logger.error('No composites built; check input files and metadata.')
        return

    run(comps, out_dir)


if __name__ == '__main__':
    main()
