"""
Process sample VIIRS GeoTIFFs in `data/viirs_raw/`.
Creates binary urban masks, computes lit-area, compactness and centroid,
exports masks to `outputs/viirs_masks/` and writes a summary CSV.

Run: Use the workspace venv Python executable (see README). Example:
  C:/Users/anhmi/OneDrive/Documents/University/CRP2/.venv/Scripts/python.exe scripts/03_process_samples.py
"""
from pathlib import Path
import logging
import rasterio
import numpy as np
import pandas as pd

from ntl_processing import (
    read_viirs_tif, create_urban_mask, calculate_lit_area,
    calculate_compactness, find_centroid, export_geotiff
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_all_samples():
    root = Path(__file__).parent.parent
    raw_dir = root / 'data' / 'viirs_raw'
    out_masks = root / 'outputs' / 'viirs_masks'
    out_masks.mkdir(parents=True, exist_ok=True)
    out_dir = root / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)

    tif_paths = sorted(raw_dir.glob('*.tif'))
    if not tif_paths:
        logger.error('No TIFFs found in data/viirs_raw/. Place sample files there and retry.')
        return

    rows = []
    for tif in tif_paths:
        logger.info(f'Processing: {tif.name}')
        try:
            data, meta, bounds = read_viirs_tif(str(tif))
        except Exception as e:
            logger.error(f'Failed to read {tif.name}: {e}')
            continue

        # Create mask (use default threshold from config inside function call)
        mask = create_urban_mask(data)

        # Metrics
        area_km2 = calculate_lit_area(mask)
        compactness = calculate_compactness(mask)
        centroid = find_centroid(mask)

        # Export mask as uint8 GeoTIFF
        mask_out_meta = meta.copy()
        mask_out_meta.update({
            'dtype': 'uint8',
            'count': 1,
            'compress': 'lzw'
        })
        out_path = out_masks / f'{tif.stem}_mask.tif'
        try:
            with rasterio.open(out_path, 'w', **mask_out_meta) as dst:
                dst.write(mask.astype('uint8'), 1)
            logger.info(f'Exported mask: {out_path.name}')
        except Exception as e:
            logger.error(f'Error exporting mask for {tif.name}: {e}')

        rows.append({
            'file': tif.name,
            'mask_file': out_path.name,
            'area_km2': area_km2,
            'compactness': compactness,
            'centroid_row': centroid[0] if centroid else None,
            'centroid_col': centroid[1] if centroid else None
        })

    df = pd.DataFrame(rows)
    summary_csv = out_dir / 'sample_processing_summary.csv'
    df.to_csv(summary_csv, index=False)
    logger.info(f'Saved summary: {summary_csv}')


if __name__ == '__main__':
    process_all_samples()
