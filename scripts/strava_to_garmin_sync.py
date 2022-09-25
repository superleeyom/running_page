import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from io import BytesIO
from xml.etree import ElementTree

import gpxpy
import gpxpy.gpx
from config import STRAVA_GARMIN_TYPE_DICT
from garmin_sync import Garmin
from strava_sync import run_strava_sync

from utils import make_strava_client
from stravaweblib import WebClient, DataFormat
import pytz


def generate_strava_run_points(start_time, strava_streams):
    """
    strava return same len data list
    """
    if not (strava_streams.get("time") and strava_streams.get("latlng")):
        return None
    points_dict_list = []
    time_list = strava_streams["time"].data
    time_list = [start_time + timedelta(seconds=int(i)) for i in time_list]
    latlng_list = strava_streams["latlng"].data

    for i, j in zip(time_list, latlng_list):
        points_dict_list.append(
            {
                "latitude": j[0],
                "longitude": j[1],
                "time": i,
            }
        )
    # add heart rate
    if strava_streams.get("heartrate"):
        heartrate_list = strava_streams.get("heartrate").data
        for index, h in enumerate(heartrate_list):
            points_dict_list[index]["heart_rate"] = h
    # add altitude
    if strava_streams.get("altitude"):
        heartrate_list = strava_streams.get("altitude").data
        for index, h in enumerate(heartrate_list):
            points_dict_list[index]["elevation"] = h
    return points_dict_list


def make_gpx_from_points(title, points_dict_list):
    gpx = gpxpy.gpx.GPX()
    gpx.nsmap["gpxtpx"] = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = title
    gpx_track.type = "Run"
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    for p in points_dict_list:
        if p.get("heart_rate") is None:
            point = gpxpy.gpx.GPXTrackPoint(**p)
        else:
            heart_rate_num = p.pop("heart_rate")
            point = gpxpy.gpx.GPXTrackPoint(**p)
            gpx_extension_hr = ElementTree.fromstring(
                f"""<gpxtpx:TrackPointExtension xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
                <gpxtpx:hr>{heart_rate_num}</gpxtpx:hr>
                </gpxtpx:TrackPointExtension>
            """
            )
            point.extensions.append(gpx_extension_hr)
        gpx_segment.points.append(point)
    return gpx.to_xml()


async def upload_to_activities(garmin_client, strava_client, strava_web_client, format):
    files_list = []
    last_activity = await garmin_client.get_activities(0, 1)
    if not last_activity:
        print("no activity")
        return files_list
    else:
        # is this startTimeGMT must have ?
        after_datetime_str = last_activity[0]["startTimeGMT"]
        after_datetime = datetime.strptime(after_datetime_str, "%Y-%m-%d %H:%M:%S")
        after_datetime = (
            after_datetime.replace(tzinfo=timezone.utc)
                .astimezone(tz=pytz.timezone("Asia/Shanghai"))
                .strftime("%Y-%m-%d %H:%M:%S")
        )
        print(after_datetime)
        filters = {"after": after_datetime}
    strava_activities = list(strava_client.get_activities(**filters))
    # strava rate limit
    for i in strava_activities[:50]:
        print(i.id)
        data = strava_web_client.get_activity_data(i.id, fmt=format)
        files_list.append(data)
    await garmin_client.upload_activities_original(files_list)
    return files_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("strava_client_id", help="strava client id")
    parser.add_argument("strava_client_secret", help="strava client secret")
    parser.add_argument("strava_refresh_token", help="strava refresh token")
    parser.add_argument("garmin_email", nargs="?", help="email of garmin")
    parser.add_argument("garmin_password", nargs="?", help="password of garmin")
    parser.add_argument("strava_email", nargs="?", help="email of strava")
    parser.add_argument("strava_password", nargs="?", help="password of strava")
    parser.add_argument(
        "--is-cn",
        dest="is_cn",
        action="store_true",
        help="if garmin accout is cn",
    )

    options = parser.parse_args()
    strava_client = make_strava_client(
        options.strava_client_id,
        options.strava_client_secret,
        options.strava_refresh_token,
    )
    strava_web_client = WebClient(
        access_token=strava_client.access_token,
        email=options.strava_email,
        password=options.strava_password,
    )

    garmin_auth_domain = "CN" if options.is_cn else ""

    try:
        garmin_client = Garmin(
            options.garmin_email, options.garmin_password, garmin_auth_domain
        )
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(
            upload_to_activities(
                garmin_client, strava_client, strava_web_client, DataFormat.ORIGINAL
            )
        )
        loop.run_until_complete(future)

    except Exception as err:
        print(err)
# Run the strava sync
run_strava_sync(
    options.strava_client_id,
    options.strava_client_secret,
    options.strava_refresh_token,
)
