import ee
import numpy as np
import sentinelhub
from sentinelhub import SHConfig, SentinelHubRequest, MimeType, DataCollection, BBox, bbox_to_dimensions, \
    SentinelHubDownloadClient
from constants import *
import requests

import log

LOGGER = log.get_logger(__name__)


def Filter_Results(inputList: list) -> list:
    """
    Filters results from catalog search API
    :param inputList:
    :return: Filtered list (NT for Non-Time Critical)
    """
    try:
        filtered_results = []

        for result in inputList:
            if '_NT_' in result['id']:
                filtered_results.append((result))

        return filtered_results
    except Exception as e:
        LOGGER.error(e)


def Print_Progress(month: int, curr: int, total: int) -> None:
    percentage = curr / total * 100
    print("\r{} Loading {:.2f}% | Month {}/12 | Location {}/{}".format(SYMBOLS[curr % len(SYMBOLS)], percentage, month,
                                                                       curr, total), end='', flush=True)


def get_all_bands_extra_request(config: SHConfig, start: str, end: str, aoi_bbox: BBox,
                                aoi_size: tuple[int, int]) -> SentinelHubRequest:
    return SentinelHubRequest(
        data_folder=OUTPUT_FOLDER,
        evalscript=SCRIPT_ALL_BANDS_EXTRA,
        input_data=[
            SentinelHubRequest.input_data(
                DataCollection.SENTINEL3_OLCI.define_from("s3olci", service_url=config.sh_base_url),
                time_interval=(start, end),
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF), ],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )


def gee_auth_init(project_name):
    ee.Authenticate()
    ee.Initialize(project=project_name)


def Request_AOD(url, locName, interval, lon, lat):
    start = interval[0]
    end = interval[1]
    params = {
        'site': locName,
        'year': start.year,
        'month': start.month,
        'day': start.day,
        'year2': end.year,
        'month2': end.month,
        'day2': end.day,
        'AVG': 10,
        'AOD15': 1,
        'hour': start.hour,
        'hour2': end.hour,
        'if_no_html': 1
    }

    return fetch_aeronet_data(url, params), locName, lon, lat, interval


def fetch_aeronet_data(aod_url, params):
    try:
        response = requests.get(
            url=aod_url,
            params=params
        )

        if not len(response.text) == 45:
            data = response.text.strip()
            data = data.split('\n')
            data = data[6:]

            result_list = []

            for i in range(len(data)):
                row_aeronet = data[i].split(',')
                result_list.append(row_aeronet)

            return result_list
        return []

    except Exception as e:
        LOGGER.error(f"Error fetching AERONET data: {e}")
        LOGGER.error(f"The parameters are: {params}")
        return []


def get_shconfig(profileName: str) -> SHConfig:
    config = SHConfig()
    config.sh_client_id = ID
    config.sh_client_secret = SECRET
    config.sh_token_url = TOKEN_URL
    config.sh_base_url = BASE_URL
    return config


def get_geometry_radius(geometry_point):
    coord = np.array(geometry_point.getInfo()['coordinates'][0])
    return tuple([coord[:, 0].min(), coord[:, 1].min(), coord[:, 0].max(), coord[:, 1].max()])


def bounds(lon: float, lat: float, buffer: int):
    geo = ee.Geometry.Point(lon, lat)
    radius = geo.buffer(buffer)
    return get_geometry_radius(radius)


def irange(jan, dez):
    return range(jan, dez + 1)


def exists_image(search_result):
    return len(search_result) > 0


def exists_aod_data(aod_list):
    return len(aod_list) > 0


def get_formated_time(interval):
    return interval[0].strftime("%Y%m%dT%H%M%S"), interval[-1].strftime("%Y%m%dT%H%M%S")


def get_formated_filename(locationName, lon, lat, sat_process_type_name, start_time, end_time):
    return f"{locationName}_{str(lon).replace(".", "-")}_{str(lat).replace(".", "-")}__{start_time}_{end_time}.tiff"


def download_all_requests(config, requests_list, show_progress, max_threads):
    return SentinelHubDownloadClient(config=config).download(requests_list, show_progress=True, max_threads=5)
