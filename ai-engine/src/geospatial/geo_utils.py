from typing import List, Dict, Optional
from shapely.geometry import Point, mapping
from shapely.ops import unary_union
from processors.gps_extractor import GPSCoordinates

class GeoSpatialUtils:
    @staticmethod
    def detection_to_geojson(detection: Dict, gps: GPSCoordinates) -> Dict:
        return {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [gps.longitude, gps.latitude]},
            "properties": {
                "class_name": detection["class_name"], "severity": detection["severity"],
                "confidence": detection["confidence"], "bbox": detection["bbox"], "altitude": gps.altitude
            }
        }

    @staticmethod
    def calculate_defect_clusters(detections: List[Dict], cluster_radius: float = 10.0) -> List[Dict]:
        try:
            from sklearn.cluster import DBSCAN
            import numpy as np
            if len(detections) < 2: return []
            coords = np.array([[d["gps"]["longitude"], d["gps"]["latitude"]] for d in detections if "gps" in d and d["gps"]])
            if len(coords) == 0: return []
            eps = cluster_radius / 111320.0
            clustering = DBSCAN(eps=eps, min_samples=2).fit(coords)
            labels = clustering.labels_
            clusters = []
            for label in set(labels):
                if label == -1: continue
                cluster_points = coords[labels == label]
                cluster_detections = [d for d, l in zip(detections, labels) if l == label]
                center_lon = np.mean(cluster_points[:, 0])
                center_lat = np.mean(cluster_points[:, 1])
                severities = [d["severity"] for d in cluster_detections]
                critical_count = severities.count("critical")
                high_count = severities.count("high")
                clusters.append({
                    "cluster_id": int(label),
                    "center": {"lon": float(center_lon), "lat": float(center_lat)},
                    "detection_count": len(cluster_detections),
                    "critical_count": critical_count, "high_count": high_count,
                    "severity": "critical" if critical_count > 0 else ("high" if high_count > 0 else "medium"),
                    "detections": cluster_detections
                })
            return clusters
        except Exception as e:
            print(f"Clustering error: {e}")
            return []

    @staticmethod
    def generate_inspection_boundary(detections: List[Dict]) -> Optional[Dict]:
        try:
            from shapely.geometry import Polygon
            points = [Point(d["gps"]["longitude"], d["gps"]["latitude"]) for d in detections if "gps" in d and d["gps"]]
            if len(points) < 3: return None
            multi_point = unary_union(points)
            hull = multi_point.convex_hull
            return {"type": "Feature", "geometry": mapping(hull), "properties": {"area_sqm": hull.area * 111320**2, "point_count": len(points)}}
        except Exception as e:
            print(f"Boundary generation error: {e}")
            return None
