from ultralytics import YOLO
import yaml
import os

def train_model():
    model = YOLO("yolov8n.pt")
    data_yaml = {
        'path': '/app/training/data',
        'train': 'images/train',
        'val': 'images/val',
        'names': {
            0: 'crack', 1: 'hotspot', 2: 'soiling', 3: 'delamination', 4: 'broken_panel',
            5: 'vegetation_overgrowth', 6: 'structural_damage', 7: 'corrosion',
            8: 'missing_component', 9: 'water_damage', 10: 'worker', 11: 'vehicle', 12: 'safety_violation'
        }
    }
    with open('/app/training/dataset.yaml', 'w') as f:
        yaml.dump(data_yaml, f)
    results = model.train(data='/app/training/dataset.yaml', epochs=100, imgsz=640, batch=16, device=0 if os.path.exists('/dev/nvidia0') else 'cpu', patience=20, save=True, project='/app/models', name='drone_custom', exist_ok=True)
    model.export(format='onnx', dynamic=True)
    print(f"Training complete. Best model: {results.best}")
    return results

if __name__ == "__main__":
    train_model()
