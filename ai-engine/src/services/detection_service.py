import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from config import settings
from models.yolo_detector import detector
from processors.gps_extractor import GPSExtractor
from processors.image_processor import ImageProcessor
from geospatial.geo_utils import GeoSpatialUtils

class DetectionService:
    def __init__(self):
        self.detector = detector
        self.gps_extractor = GPSExtractor()
        self.geo_utils = GeoSpatialUtils()
        self.processed_dir = settings.PROCESSED_DIR
        Path(self.processed_dir).mkdir(parents=True, exist_ok=True)

    async def process_image(self, image_path: str, inspection_id: str, asset_id: Optional[str] = None) -> Dict:
        start_time = datetime.utcnow()
        gps = self.gps_extractor.extract(image_path)
        processed_path = ImageProcessor.preprocess(image_path)
        detections = self.detector.detect(processed_path)
        annotated_filename = f"annotated_{uuid.uuid4().hex}.jpg"
        annotated_path = os.path.join(self.processed_dir, annotated_filename)
        self.detector.annotate_image(processed_path, detections, annotated_path)
        enriched_detections = []
        for det in detections:
            det_gps = self.gps_extractor.pixel_to_gps(image_path, det["bbox"]["center_x"], det["bbox"]["center_y"], det["image_width"], det["image_height"])
            if det_gps:
                det["gps"] = det_gps.to_dict()
                det["geojson"] = self.geo_utils.detection_to_geojson(det, det_gps)
            elif gps:
                det["gps"] = gps.to_dict()
                det["geojson"] = self.geo_utils.detection_to_geojson(det, gps)
            else:
                det["gps"] = None
                det["geojson"] = None
            enriched_detections.append(det)
        heatmap_path = None
        if len(detections) > 0:
            heatmap_filename = f"heatmap_{uuid.uuid4().hex}.jpg"
            heatmap_path = os.path.join(self.processed_dir, heatmap_filename)
            ImageProcessor.create_heatmap(processed_path, detections, heatmap_path)
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for det in enriched_detections:
            sev = det.get("severity", "low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        result = {
            "inspection_id": inspection_id, "asset_id": asset_id, "image_path": image_path,
            "processed_image": processed_path, "annotated_image": annotated_path, "heatmap_image": heatmap_path,
            "gps": gps.to_dict() if gps else None, "detections": enriched_detections,
            "detection_count": len(enriched_detections), "severity_counts": severity_counts,
            "processing_time_seconds": round(processing_time, 2), "processed_at": datetime.utcnow().isoformat()
        }
        Path(processed_path).unlink(missing_ok=True)
        return result

    async def process_video(self, video_path: str, inspection_id: str, sample_interval: int = 30) -> Dict:
        detections = self.detector.detect_video(video_path, sample_interval)
        return {
            "inspection_id": inspection_id, "video_path": video_path, "detections": detections,
            "frame_count": len(set(d["frame_number"] for d in detections)),
            "total_detections": len(detections), "processed_at": datetime.utcnow().isoformat()
        }

    async def process_batch(self, image_paths: List[str], inspection_id: str) -> Dict:
        results = []
        all_detections = []
        for path in image_paths:
            try:
                result = await self.process_image(path, inspection_id)
                results.append(result)
                all_detections.extend(result["detections"])
            except Exception as e:
                results.append({"image_path": path, "error": str(e)})
        clusters = self.geo_utils.calculate_defect_clusters(all_detections)
        boundary = self.geo_utils.generate_inspection_boundary(all_detections)
        return {
            "inspection_id": inspection_id, "image_count": len(image_paths), "results": results,
            "total_detections": len(all_detections), "clusters": clusters, "boundary": boundary,
            "processed_at": datetime.utcnow().isoformat()
        }

    async def notify_backend(self, result: Dict) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{settings.BACKEND_URL}/api/v1/detections/batch", json=result, timeout=30.0)
                return response.status_code == 201
        except Exception as e:
            print(f"Failed to notify backend: {e}")
            return False

detection_service = DetectionService()
