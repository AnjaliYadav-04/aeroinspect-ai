import exifread
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Dict, Optional
from dataclasses import dataclass
import rasterio
from pyproj import Transformer
import numpy as np

@dataclass
class GPSCoordinates:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    timestamp: Optional[str] = None
    direction: Optional[float] = None
    def to_dict(self) -> Dict:
        return {"latitude": self.latitude, "longitude": self.longitude, "altitude": self.altitude, "timestamp": self.timestamp, "direction": self.direction}
    def to_wkt(self) -> str:
        return f"POINT({self.longitude} {self.latitude})"

class GPSExtractor:
    @staticmethod
    def _convert_to_degrees(value) -> float:
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    @classmethod
    def extract_from_exif(cls, image_path: str) -> Optional[GPSCoordinates]:
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
            if not tags.get('GPS GPSLatitude') or not tags.get('GPS GPSLongitude'):
                return None
            lat = cls._convert_to_degrees(tags['GPS GPSLatitude'])
            if tags['GPS GPSLatitudeRef'].values[0] != 'N': lat = -lat
            lon = cls._convert_to_degrees(tags['GPS GPSLongitude'])
            if tags['GPS GPSLongitudeRef'].values[0] != 'E': lon = -lon
            altitude = None
            if 'GPS GPSAltitude' in tags:
                altitude = float(tags['GPS GPSAltitude'].values[0].num) / float(tags['GPS GPSAltitude'].values[0].den)
            timestamp = None
            if 'GPS GPSDate' in tags and 'GPS GPSTimeStamp' in tags:
                date = tags['GPS GPSDate'].values
                time_vals = tags['GPS GPSTimeStamp'].values
                timestamp = f"{date} {int(time_vals[0])}:{int(time_vals[1])}:{float(time_vals[2])}"
            direction = None
            if 'GPS GPSImgDirection' in tags:
                direction = float(tags['GPS GPSImgDirection'].values[0].num) / float(tags['GPS GPSImgDirection'].values[0].den)
            return GPSCoordinates(latitude=round(lat, 8), longitude=round(lon, 8), altitude=altitude, timestamp=timestamp, direction=direction)
        except Exception as e:
            print(f"EXIF extraction error: {e}")
            return None

    @classmethod
    def extract_from_pillow(cls, image_path: str) -> Optional[GPSCoordinates]:
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            if not exif: return None
            gps_info = {}
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = gps_value
            if not gps_info or 'GPSLatitude' not in gps_info: return None
            lat = gps_info['GPSLatitude']
            lat_ref = gps_info.get('GPSLatitudeRef', 'N')
            lon = gps_info['GPSLongitude']
            lon_ref = gps_info.get('GPSLongitudeRef', 'E')
            lat_dec = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
            if lat_ref != 'N': lat_dec = -lat_dec
            lon_dec = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
            if lon_ref != 'E': lon_dec = -lon_dec
            return GPSCoordinates(latitude=round(float(lat_dec), 8), longitude=round(float(lon_dec), 8))
        except Exception as e:
            print(f"Pillow extraction error: {e}")
            return None

    @classmethod
    def extract_from_geotiff(cls, image_path: str) -> Optional[GPSCoordinates]:
        try:
            with rasterio.open(image_path) as src:
                bounds = src.bounds
                center_lon = (bounds.left + bounds.right) / 2
                center_lat = (bounds.top + bounds.bottom) / 2
                if src.crs and src.crs.to_string() != "EPSG:4326":
                    transformer = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
                    center_lon, center_lat = transformer.transform(center_lon, center_lat)
                return GPSCoordinates(latitude=round(center_lat, 8), longitude=round(center_lon, 8))
        except Exception as e:
            print(f"GeoTIFF extraction error: {e}")
            return None

    @classmethod
    def extract(cls, image_path: str) -> Optional[GPSCoordinates]:
        for method in [cls.extract_from_exif, cls.extract_from_pillow, cls.extract_from_geotiff]:
            coords = method(image_path)
            if coords: return coords
        return None

    @staticmethod
    def pixel_to_gps(image_path: str, pixel_x: float, pixel_y: float, img_width: int, img_height: int) -> Optional[GPSCoordinates]:
        center_gps = GPSExtractor.extract(image_path)
        if not center_gps: return None
        altitude = center_gps.altitude or 100.0
        ground_width = 2 * altitude * 0.8391
        ground_height = ground_width * (img_height / img_width)
        dx_pixels = pixel_x - (img_width / 2)
        dy_pixels = pixel_y - (img_height / 2)
        dx_meters = (dx_pixels / img_width) * ground_width
        dy_meters = (dy_pixels / img_height) * ground_height
        lat_offset = dy_meters / 111320.0
        lon_offset = dx_meters / (111320.0 * abs(np.cos(np.radians(center_gps.latitude))))
        return GPSCoordinates(latitude=round(center_gps.latitude + lat_offset, 8), longitude=round(center_gps.longitude + lon_offset, 8), altitude=center_gps.altitude)
