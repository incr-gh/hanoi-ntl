"""
Download NOAA VIIRS DNB monthly composites from Google Earth Engine
Reference: https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG
"""

import ee
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Ensure project root is on path so `config` imports reliably
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HANOI_BOUNDS, ANALYSIS_YEARS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def authenticate_gee():
    """Authenticate with Google Earth Engine."""
    try:
        # Interactive authentication (opens browser). If already authenticated,
        # ee.Authenticate() will be a no-op.
        ee.Authenticate()
        # Initialize Earth Engine (no explicit project required here).
        ee.Initialize(project="nlp-in-medical-p-1699514675739")
        logger.info("GEE authentication successful")
    except Exception as e:
        logger.error(f"GEE authentication failed: {e}")
        logger.info("Please run: earthengine authenticate")
        raise

def create_hanoi_geometry():
    """Create Hanoi municipality boundary geometry."""
    coords = [
        [HANOI_BOUNDS['west'], HANOI_BOUNDS['south']],
        [HANOI_BOUNDS['east'], HANOI_BOUNDS['south']],
        [HANOI_BOUNDS['east'], HANOI_BOUNDS['north']],
        [HANOI_BOUNDS['west'], HANOI_BOUNDS['north']],
        [HANOI_BOUNDS['west'], HANOI_BOUNDS['south']],
    ]
    return ee.Geometry.Polygon([coords])

def download_viirs_monthly(year, month, output_dir):
    """Download VIIRS DNB monthly composite for specified month."""
    try:
        # Try to resolve a valid VIIRS DNB collection. Some dataset IDs
        # have changed or require special access; try common variants and
        # provide informative errors if none are available.
        DATASET_IDS = [
            # Add the Code Editor-working ID first (matches the JS snippet)
            'NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG',
            'NOAA/VIIRS/DNB_MONTHLY_V1/VCMCFG',
            'NOAA/VIIRS/DNB_MONTHLY_V1_VCMCFG',
            'NOAA/VIIRS/DNB_MONTHLY_V1',
            'NOAA/VIIRS/DNB_MONTHLY_V1/VCMSLV',
        ]

        def get_viirs_collection():
            last_exc = None
            for ds in DATASET_IDS:
                try:
                    coll = ee.ImageCollection(ds)
                    # Trigger a lightweight server check
                    _ = coll.size().getInfo()
                    logger.info(f"Using VIIRS collection: {ds}")
                    return coll
                except Exception as e:
                    last_exc = e
                    logger.debug(f"Dataset {ds} not available: {e}")
            # If we reach here, none of the dataset IDs worked
            logger.error("Unable to access any known VIIRS DNB collections.")
            logger.error("Possible causes: dataset not available in your EE account, or incorrect dataset ID.")
            logger.error("Visit: https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG to check access.")
            if last_exc is not None:
                logger.error(f"Last error: {last_exc}")
            return None

        viirs = get_viirs_collection()
        if viirs is None:
            return None
        
        # Filter by date
        start_date = f'{year}-{month:02d}-01'
        end_date = datetime(year, month, 1) + timedelta(days=32)
        end_date = end_date.replace(day=1).strftime('%Y-%m-%d')
        
        # Filter collection
        filtered = viirs.filterDate(start_date, end_date) \
                .filterBounds(create_hanoi_geometry())

        # Check whether any images exist for this month/region
        count = int(filtered.size().getInfo() or 0)
        if count == 0:
            logger.warning(f"No VIIRS data found for {year}-{month:02d}")
            return None

        # Prefer the `avg_rad` band (matches your JS snippet). Try selecting
        # it from the filtered collection and use the first image for export.
        try:
            image = ee.Image(filtered.select('avg_rad').first())
            viirs_image = image.select(['avg_rad'])
        except Exception:
            # Fallback: take the first image and select any available common bands
            image = ee.Image(filtered.first())
            try:
                bands = image.bandNames().getInfo()
            except Exception:
                bands = []
            pick = [b for b in ['avg_rad', 'avg_dnb', 'cf_cvg'] if b in bands]
            if not pick:
                logger.error('No recognized VIIRS bands found on image; aborting.')
                return None
            viirs_image = image.select(pick)
        
        # Export to Google Drive
        task = ee.batch.Export.image.toDrive(
            image=viirs_image,
            description=f'VIIRS_DNB_{year}_{month:02d}',
            folder='hanoi_ntl_analysis',
            fileNamePrefix=f'VIIRS_DNB_{year}_{month:02d}',
            region=create_hanoi_geometry(),
            scale=463,  # VIIRS native resolution
            crs='EPSG:32648',  # UTM Zone 48N
            maxPixels=1e10,
            fileFormat='GeoTIFF'
        )
        
        task.start()
        logger.info(f"Started export: VIIRS_DNB_{year}_{month:02d}")
        return task
        
    except Exception as e:
        logger.error(f"Error downloading VIIRS for {year}-{month:02d}: {e}")
        return None

def main():
    """Main execution function."""
    logger.info("Starting VIIRS DNB data download...")
    
    # Authenticate with GEE
    authenticate_gee()

    # Ensure the data output directory is at the project root
    output_dir = Path(__file__).parent.parent / 'data' / 'viirs_raw'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download all monthly composites for 2012-2023
    tasks = []
    for year in ANALYSIS_YEARS:
        for month in range(1, 13):
            logger.info(f"Queuing VIIRS for {year}-{month:02d}...")
            task = download_viirs_monthly(year, month, output_dir)
            if task:
                tasks.append({
                    'year': year,
                    'month': month,
                    'task_id': task.id
                })
    
    logger.info(f"Submitted {len(tasks)} export tasks to Google Drive")
    logger.info("Monitor progress at: https://code.earthengine.google.com/tasks")
    logger.info("Once downloaded, move files to: data/viirs_raw/")
    
    # Save task log
    task_log = pd.DataFrame(tasks)
    task_log.to_csv(output_dir.parent / 'gee_export_log.csv', index=False)
    logger.info(f"Task log saved: {output_dir.parent / 'gee_export_log.csv'}")

if __name__ == '__main__':
    main()
