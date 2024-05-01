#constants.py
import os
import yaml
# Loading Constants
SYMBOLS = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']

with open('app_config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Config Constants
PROFILE = config['copernicus']['profile_name']
TOKEN_URL = config['copernicus']['token_url']
BASE_URL = config['copernicus']['base_url']
ID = os.environ.get('API_CLIENT_ID')
SECRET = os.environ.get('API_SECRET')
PROJECT_NAME = os.environ.get('PROJECT_NAME')

# Data/Img Configurations
RESOLUTION = config['copernicus']['image']['resolution']
BUFFER = config['copernicus']['image']['buffer']
YEAR = config['copernicus']['image']['year']
CRS_SETTING = config['copernicus']['image']['crs']

# AOD Configurations
AOD_URL = config['aeronet']['aod']['url']
COLUMNS = config['aeronet']['aod']['columns']
COLUMNS = [col.strip() for col in (COLUMNS.split(','))]

# Input/Output Configuration
INPUT = f"./data/Input/aeronet_locations_v3_{YEAR}.txt"
INPUT_DEBUGGING = f"./data/Input/test.txt"
OUTPUT = f"./data/Output/{YEAR}/Master/master_aod_{YEAR}.csv"
OUTPUT_FOLDER = f"./data/Output/{YEAR}/PreProcessed"
SAT_PROCESS_NAME_S3OLCI_L1_FR = "_SENTINEL3_OL_1_EFR_"

# Extras
JAN, DEZ = 1, 12

# Scripts
SCRIPT_ALL_BANDS_EXTRA = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B09","B10","B11","B12","B13","B14","B15","B16","B17","B18","B19","B20","B21","SAA", "SZA", "VAA", "VZA", "HUMIDITY", "TOTAL_COLUMN_OZONE", "TOTAL_COLUMN_WATER_VAPOUR", "dataMask"],
                units: ["REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "REFLECTANCE",
                        "DEGREES",
                        "DEGREES",
                        "DEGREES",
                        "DEGREES",
                        "PERCENT",
                        "KG_M2",
                        "KG_M2",
                        "DN"
                        ]
            }],
            output: {
                bands: 29,
                sampleType: "INT16"
            }
        };
    }

    function evaluatePixel(sample) {
        return [10000 * sample.B01,
                10000 * sample.B02,
                10000 * sample.B03,
                10000 * sample.B04,
                10000 * sample.B05,
                10000 * sample.B06,
                10000 * sample.B07,
                10000 * sample.B08,
                10000 * sample.B09,
                10000 * sample.B10,
                10000 * sample.B11,
                10000 * sample.B12,
                10000 * sample.B13,
                10000 * sample.B14,
                10000 * sample.B15,
                10000 * sample.B16,
                10000 * sample.B17,
                10000 * sample.B18,
                10000 * sample.B19,
                10000 * sample.B20,
                10000 * sample.B21,
                sample.SAA,
                sample.SZA,
                sample.VAA,
                sample.VZA,
                sample.HUMIDITY,
                100000 * sample.TOTAL_COLUMN_OZONE,
                sample.TOTAL_COLUMN_WATER_VAPOUR,
                sample.dataMask];
    }
"""
