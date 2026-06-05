# NeuroBright Migration Guide

## ✅ Completed Restructuring

The NeuroBright project has been successfully restructured into a production-grade monorepo.

## 📁 New Structure

```
NeuroBright/
├── ml_service/              # ✅ Complete ML pipeline + backend
│   ├── pipeline/            # ✅ 7-stage ML workflow
│   ├── api/                 # ✅ FastAPI + WebSocket
│   ├── config/              # ✅ Configuration
│   ├── utils/               # ✅ Utilities
│   ├── data/                # ✅ Datasets (migrated)
│   ├── models/              # ✅ Saved models (migrated)
│   └── app.py               # ✅ CLI entry point
├── frontend/                # ✅ React placeholder
└── NeuroBright_Firmware/    # ✅ Unchanged
```

## 🔄 What Changed

### Old Files → New Location

| Old File | New Location |
|----------|--------------|
| `record.py` | `ml_service/pipeline/ingestion/record_session.py` |
| `process_data.py` | `ml_service/pipeline/preprocessing/process_pipeline.py` |
| `train_model.py` | `ml_service/pipeline/training/train.py` |
| `tune_model.py` | `ml_service/pipeline/training/tune.py` |
| `realtime_predict.py` | `ml_service/pipeline/inference/realtime_engine.py` |
| `test_hardware.py` | `ml_service/pipeline/ingestion/test_connection.py` |
| `app.py` | `ml_service/app.py` (rewritten as CLI) |
| `config/config.yaml` | `ml_service/config/config.yaml` |
| `src/` | `ml_service/pipeline/` (restructured) |
| `data/` | `ml_service/data/` (migrated) |
| `models/` | `ml_service/models/` (migrated) |

### Old Files (Can be Deleted)

These files are now obsolete:

```
record.py
record_stressed.py
process_data.py
train_model.py
tune_model.py
realtime_predict.py
diagnose.py
test_hardware.py
test_model.py
verify_setup.py
app.py (old version)
src/ (old structure)
data/ (old location)
models/ (old location)
config/ (old location)
logs/ (old location)
```

## 🚀 New Usage

### All operations now go through the CLI:

```bash
cd ml_service

# Test hardware
python app.py --mode test

# Collect data
python app.py --mode collect

# Preprocess
python app.py --mode process

# Train
python app.py --mode train

# Tune hyperparameters
python app.py --mode tune

# Real-time inference
python app.py --mode infer

# Start API server
python app.py --mode server
```

## 📝 Import Path Changes

### Old Imports:
```python
from src.data.collector import BrainDataCollector
from src.utils.logger import get_logger
from src.models.eegnet import EEGNet
```

### New Imports:
```python
from pipeline.ingestion.arduino_reader import ArduinoReader
from utils.logger import get_logger
from pipeline.training.eegnet import EEGNet
```

## 🔧 Configuration

All settings are now in `ml_service/config/config.yaml`:

- Hardware settings (port, baud rate)
- Signal processing parameters
- Model hyperparameters
- Training settings
- API configuration

## 📊 Data Migration

✅ **Completed automatically:**

- `data/raw/*.csv` → `ml_service/data/raw/`
- `data/processed/*.npy` → `ml_service/data/processed/`
- `models/saved/*.pth` → `ml_service/models/saved/`

## 🌐 New FastAPI Backend

### Start server:
```bash
cd ml_service
python app.py --mode server
```

### Endpoints:
- WebSocket: `ws://localhost:8000/ws/brain-state`
- REST: `http://localhost:8000/api/*`

### Test WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/brain-state');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

## 🧪 Testing the New Structure

### 1. Test hardware connection:
```bash
cd ml_service
python app.py --mode test
```

### 2. Verify existing model works:
```bash
python app.py --mode infer
```

### 3. Test API server:
```bash
python app.py --mode server
# In another terminal:
curl http://localhost:8000/api/health
```

## 🐛 Troubleshooting

### Import errors:
- Make sure you're in `ml_service/` directory
- Check Python path: `sys.path.insert(0, str(Path(__file__).parent))`

### Config not found:
- Verify `ml_service/config/config.yaml` exists
- Check port settings match your Arduino

### Model not found:
- Verify `ml_service/models/saved/eegnet_best.pth` exists
- If missing, run: `python app.py --mode train`

## 📦 Next Steps

1. **Test all modes** to ensure everything works
2. **Update any custom scripts** to use new import paths
3. **Delete old files** after confirming new structure works
4. **Set up frontend** in `frontend/` directory
5. **Update documentation** with any project-specific changes

## 🎯 Benefits of New Structure

✅ **Clear separation**: ML pipeline vs API vs Frontend
✅ **Production-ready**: Proper logging, error handling, config management
✅ **Scalable**: Easy to add new pipeline stages
✅ **Maintainable**: Logical organization, clear dependencies
✅ **Testable**: Each module can be tested independently
✅ **Documented**: Comprehensive docstrings and README

## 📞 Support

If you encounter issues:
1. Check this migration guide
2. Review `ml_service/README.md`
3. Check logs in `ml_service/logs/neurobright.log`
4. Verify config in `ml_service/config/config.yaml`

---

**Migration completed successfully! 🎉**
