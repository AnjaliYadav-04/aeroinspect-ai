import cv2
import numpy as np
from typing import Dict, List, Tuple
import uuid

class ImageProcessor:
    @staticmethod
    def preprocess(image_path: str, target_size: Tuple[int, int] = (640, 640)) -> str:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        h, w = denoised.shape[:2]
        scale = min(target_size[0] / w, target_size[1] / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(denoised, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        padded = np.full((target_size[1], target_size[0], 3), 114, dtype=np.uint8)
        x_offset = (target_size[0] - new_w) // 2
        y_offset = (target_size[1] - new_h) // 2
        padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        output_path = f"/tmp/processed_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(output_path, padded)
        return output_path

    @staticmethod
    def extract_patches(image_path: str, patch_size: int = 640, overlap: int = 100) -> List[Dict]:
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        patches = []
        step = patch_size - overlap
        for y in range(0, h - overlap, step):
            for x in range(0, w - overlap, step):
                x2 = min(x + patch_size, w)
                y2 = min(y + patch_size, h)
                x1 = max(0, x2 - patch_size)
                y1 = max(0, y2 - patch_size)
                patch = img[y1:y2, x1:x2]
                patch_path = f"/tmp/patch_{x1}_{y1}.jpg"
                cv2.imwrite(patch_path, patch)
                patches.append({"path": patch_path, "offset_x": x1, "offset_y": y1, "width": x2 - x1, "height": y2 - y1})
        return patches

    @staticmethod
    def create_heatmap(image_path: str, detections: List[Dict], output_path: str) -> str:
        img = cv2.imread(image_path)
        if img is None: return output_path
        heatmap = np.zeros_like(img[:, :, 0], dtype=np.float32)
        for det in detections:
            bbox = det["bbox"]
            x1, y1, x2, y2 = int(bbox["x1"]), int(bbox["y1"]), int(bbox["x2"]), int(bbox["y2"])
            weight = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}.get(det["severity"], 0.1)
            heatmap[y1:y2, x1:x2] += weight
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap = np.uint8(heatmap)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
        cv2.imwrite(output_path, overlay)
        return output_path
