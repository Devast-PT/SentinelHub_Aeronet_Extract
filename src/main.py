from pprint import pprint
import pandas as pd
from sentinelhub import (SentinelHubCatalog, DataCollection, CRS, BBox, SHConfig, bbox_to_dimensions)
import tempo
from utils import Print_Progress, get_config, gee_auth_init, irange, \
    exists_image, Request_AOD, exists_aod_data, get_all_bands_extra_request, get_formated_time, \
    get_formated_filename, download_all_requests, bounds, get_shconfig
import log
from constants import *

# Init Logger
LOGGER = log.get_logger("Main")

# Init Google Earth Engine for Buffer Calculations
gee_auth_init(PROJECT_NAME)

# Configuration for sentinel using copernicus
config = get_shconfig(PROFILE)

# Change Input path in constants
catalog = SentinelHubCatalog(config=config)

input_df = pd.read_csv(INPUT)

# Progress
curr, total = 0, input_df.shape[0]

for row in input_df.itertuples():
    curr = curr + 1

    results_AOD = []
    requests_Sentinel = []
    locationName, lon, lat = row.name, row.longitude, row.latitude

    # Create Boundaries Around AOI
    buffered_bounds = bounds(lon, lat, BUFFER)
    aoi_bbox = BBox(buffered_bounds, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=RESOLUTION)

    LOGGER.debug(f"Location: {locationName} | Lon: {lon} | Lat: {lat} | Buffered Bounds: {buffered_bounds}")
    LOGGER.debug(f"Image shape at {RESOLUTION} m to a area of ({BUFFER}m * {BUFFER}m) resolution: {aoi_size} pixels")
    # Check all months
    for i in irange(JAN, DEZ):
        Print_Progress(i, curr, total)
        # If location has data in that month
        if row[i + 4]:

            time_interval = tempo.Create_Month_Interval(YEAR, i)
            # Lazy loading..........
            search_iterator = catalog.search(
                DataCollection.SENTINEL3_OLCI,
                bbox=aoi_bbox,
                time=time_interval,
                fields={"include": ["id", "properties.datetime", "productType"], "exclude": []},
            )

            all_timestamps = search_iterator.get_timestamps()

            if exists_image(all_timestamps):
                LOGGER.debug(f"Found {search_iterator.index} products in {time_interval} at {locationName}")
                time_interval_hour = tempo.Create_One_Hour_Interval_On_Data(all_timestamps)

                for timestamp in time_interval_hour:
                    interval = tempo.Time_Interval(timestamp)
                    AOD_Data_TS = Request_AOD(AOD_URL, row.name, interval[0], interval[1])

                    # If there exists valid data
                    if exists_aod_data(AOD_Data_TS):
                        start_time, end_time = get_formated_time(interval)
                        filename = get_formated_filename(locationName, lon, lat, SAT_PROCESS_NAME_S3OLCI_L1_FR, start_time, end_time)

                        request_all_bands = get_all_bands_extra_request(config, start_time, end_time, aoi_bbox, aoi_size)
                        request_all_bands.download_list[0].filename = filename
                        requests_Sentinel.append(request_all_bands.download_list[0])

                        # Safe data for output and download lists
                        for list in AOD_Data_TS:
                            list.append(filename)
                        results_AOD.append(AOD_Data_TS)

    if exists_aod_data(AOD_Data_TS):
        flaten_results_AOD = [item for sublist in results_AOD for item in sublist]
        data = download_all_requests(config=config, requests_list=requests_Sentinel, show_progress=True, max_threads=5)

        if os.path.exists(OUTPUT):
            existing_data = pd.read_csv(OUTPUT, index_col=0)
            new_data = pd.DataFrame(data=flaten_results_AOD, columns = COLUMNS)
            new_data.columns = COLUMNS
            new_data = new_data.loc[:, ~new_data.columns.duplicated()]
            combined = existing_data._append(new_data, ignore_index=True)
            #combined.columns = COLUMNS
            combined.to_csv(OUTPUT)
        else:
            new_data = pd.DataFrame(data=flaten_results_AOD, columns = COLUMNS)
            new_data = new_data.loc[:, ~new_data.columns.duplicated()]
            new_data.to_csv(OUTPUT)

        LOGGER.debug(f"Location {curr} Saved {len(data)} Images and {len(results_AOD)} AOD Points")
