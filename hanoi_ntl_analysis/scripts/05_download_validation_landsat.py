"""
Download Landsat 8/9 imagery from Google Earth Engine for validation.

Computes NDBI (B6-B5)/(B6+B5) and exports composite GeoTIFFs for the most recent
year with VIIRS data. Uses annual median composites to minimize clouds.

Reference: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_8

Run: C:/Users/anhmi/OneDrive/Documents/University/CRP2/.venv/Scripts/python.exe scripts/05_download_validation_landsat.py
"""
import ee
import os
import sys
import pandas as pd
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HANOI_BOUNDS, ANALYSIS_YEARS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def authenticate_gee():
    """Authenticate with Google Earth Engine."""
    try:
        ee.Authenticate()
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


def download_landsat_validation(year, output_dir):
    """Download Landsat 8/9 annual median composite with NDBI."""
    try:
        # Use Landsat 8 and 9 (Collection 2, Tier 1)
        l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
            .filterDate(f'{year}-01-01', f'{year}-12-31') \
            .filterBounds(create_hanoi_geometry())
        
        l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') \
            .filterDate(f'{year}-01-01', f'{year}-12-31') \
            .filterBounds(create_hanoi_geometry())
        
        # Combine L8 and L9
        landsat = ee.ImageCollection(l8.merge(l9))
        
        count = int(landsat.size().getInfo() or 0)
        if count == 0:
            logger.warning(f"No Landsat images found for {year}")
            return None
        
        logger.info(f"Found {count} Landsat images for {year}")
        
        # Select bands and compute NDBI = (SWIR - NIR) / (SWIR + NIR)
        # For Landsat 8/9 Collection 2:
        #   SR_B5 = NIR (band 5)
        #   SR_B6 = SWIR1 (band 6)
        def add_ndbi(image):
            swir = image.select('SR_B6').float()
            nir = image.select('SR_B5').float()
            ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')
            # Cast NDBI to float32 to match SR band data types
            #ndbi = ndbi.toFloat32()
            return image.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6']).addBands(ndbi)
        
        landsat_ndbi = landsat.map(add_ndbi)
        
        # Compute annual median
        composite = landsat_ndbi.median()
        
        # Export NDBI and other bands
        task = ee.batch.Export.image.toDrive(
            image=composite.select(['NDBI', 'SR_B5', 'SR_B6']).float(),
            description=f'Landsat_NDBI_{year}_Hanoi',
            folder='hanoi_ntl_analysis_validation',
            fileNamePrefix=f'Landsat_NDBI_{year}',
            region=create_hanoi_geometry(),
            scale=30,  # Landsat native resolution
            crs='EPSG:32648',  # UTM Zone 48N
            maxPixels=1e10,
            fileFormat='GeoTIFF'
        )
        
        task.start()
        logger.info(f"Started Landsat export: Landsat_NDBI_{year}")
        return task
        
    except Exception as e:
        logger.error(f"Error downloading Landsat for {year}: {e}")
        return None


def main():
    logger.info("Starting Landsat data download for validation...")
    
    # Authenticate with GEE
    authenticate_gee()

    # Use most recent year with VIIRS data
    validation_year = max(ANALYSIS_YEARS)
    logger.info(f"Downloading Landsat for validation year: {validation_year}")
    
    output_dir = Path(__file__).parent.parent / 'data' / 'landsat_raw'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    task = download_landsat_validation(validation_year, output_dir)
    
    if task:
        logger.info(f"Submitted Landsat export task for {validation_year}")
        logger.info("Monitor progress at: https://code.earthengine.google.com/tasks")
        logger.info("Once downloaded, move files to: data/landsat_raw/")
        
        task_log = pd.DataFrame([{
            'year': validation_year,
            'task_id': task.id,
            'dataset': 'LANDSAT/LC08/C02/T1_L2 + LANDSAT/LC09/C02/T1_L2',
            'index': 'NDBI',
            'bands': 'SR_B5 (NIR), SR_B6 (SWIR1), NDBI'
        }])
        task_log.to_csv(output_dir.parent / 'gee_landsat_export_log.csv', index=False)
        logger.info(f"Task log saved: gee_landsat_export_log.csv")


if __name__ == '__main__':
    main()
