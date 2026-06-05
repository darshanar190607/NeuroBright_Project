# NeuroBright Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.9+
- Arduino UNO R4 with BioAmp EXG Pill
- USB cable
- Windows/Linux/macOS

### Step 1: Setup Environment

```bash
# Navigate to ML service
cd ml_service

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Hardware

Edit `config/config.yaml`:

```yaml
hardware:
  port: "COM5"  # Change to your Arduino port
  baud_rate: 230400
```

Find your port:
```bash
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

### Step 3: Test Connection

```bash
python app.py --mode test
```

Expected output:
```
[OK] Connected to UNO-R4
[OK] Sample 1: [123.45, 234.56, 345.67]
...
[OK] Connection test complete
```

### Step 4: Collect Training Data

```bash
python app.py --mode collect
```

You'll record 3 brain states (7 minutes each):

1. **Focused**: Solve math problems with concentration
2. **Drowsy**: Relax, close eyes, let mind wander
3. **Stressed**: Solve problems under time pressure

Total time: ~25 minutes (including breaks)

### Step 5: Preprocess Data

```bash
python app.py --mode process
```

This will:
- Apply notch filter (remove 50Hz noise)
- Apply bandpass filter (keep 1-45Hz)
- Create 2-second sliding windows
- Reject artifact windows
- Save to `data/processed/`

### Step 6: Train Model

```bash
python app.py --mode train
```

Training takes ~10-20 minutes on GPU, longer on CPU.

Expected output:
```
Epoch    Train Loss   Train Acc    Val Acc      Time
1        1.0234       0.4567       0.5123       12.34s
...
194      0.2345       0.9123       0.8756       11.23s

[OK] Best validation accuracy: 0.8756
[OK] Model saved to: models/saved/eegnet_best.pth
```

### Step 7: Real-Time Inference

```bash
python app.py --mode infer
```

You'll see live predictions:
```
State: FOCUSED    | Confidence: 0.873
State: FOCUSED    | Confidence: 0.891
State: DROWSY     | Confidence: 0.756
```

Press Ctrl+C to stop.

### Step 8: Start API Server (Optional)

```bash
python app.py --mode server
```

Server runs at `http://localhost:8000`

Test endpoints:
```bash
# Health check
curl http://localhost:8000/api/health

# System status
curl http://localhost:8000/api/status

# Start session
curl http://localhost:8000/api/session/start
```

WebSocket connection:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/brain-state');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('State:', data.state);
  console.log('Confidence:', data.confidence);
  console.log('Action:', data.action);
};
```

## 🎯 Common Workflows

### Daily Usage (After Initial Setup)

```bash
cd ml_service
venv\Scripts\activate  # Windows
python app.py --mode infer
```

### Retrain with New Data

```bash
# Collect more data
python app.py --mode collect

# Reprocess all data
python app.py --mode process

# Retrain model
python app.py --mode train
```

### Hyperparameter Tuning

```bash
# Run Optuna optimization (50 trials)
python app.py --mode tune

# This will:
# - Search for best F1, D, dropout, lr, batch_size
# - Save best model to models/saved/eegnet_tuned.pth
```

### Development Mode

```bash
# Test individual modules
cd ml_service

# Test Arduino reader
python -m pipeline.ingestion.arduino_reader

# Test filters
python -m pipeline.preprocessing.filters

# Test EEGNet
python -m pipeline.training.eegnet

# Test feature extraction
python -m pipeline.features.band_powers
```

## 📊 Understanding Output

### Brain States

| State | Meaning | Adaptive Action |
|-------|---------|-----------------|
| **FOCUSED** | High engagement | Increase difficulty |
| **DROWSY** | Low alertness | Trigger break |
| **STRESSED** | High cognitive load | Simplify content |

### Confidence Score

- **> 0.8**: High confidence, reliable prediction
- **0.6 - 0.8**: Medium confidence, generally reliable
- **< 0.6**: Low confidence, may be transitioning

### Band Powers

- **Delta (1-4 Hz)**: Deep sleep, unconscious
- **Theta (4-8 Hz)**: Drowsiness, meditation
- **Alpha (8-12 Hz)**: Relaxed, eyes closed
- **Beta (13-30 Hz)**: Active thinking, focus
- **Gamma (30-45 Hz)**: High-level cognition

## 🐛 Troubleshooting

### "Port not found" error

```bash
# List available ports
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"

# Update config/config.yaml with correct port
```

### "Model not found" error

```bash
# Train model first
python app.py --mode train
```

### Poor signal quality

1. Check electrode contact (should be firm)
2. Apply electrode gel if available
3. Reduce movement during recording
4. Ensure proper grounding
5. Adjust thresholds in `config/config.yaml`:

```yaml
signal:
  artifact_threshold_uv: 200.0  # Increase if too sensitive
  flatline_threshold: 0.3       # Decrease if too sensitive
```

### Low accuracy

1. Collect more training data
2. Ensure clear mental states during recording
3. Run hyperparameter tuning: `python app.py --mode tune`
4. Check data quality in `data/raw/`

### Import errors

Make sure you're in `ml_service/` directory:
```bash
cd ml_service
python app.py --mode <mode>
```

## 📁 File Locations

- **Config**: `ml_service/config/config.yaml`
- **Raw data**: `ml_service/data/raw/*.csv`
- **Processed data**: `ml_service/data/processed/*.npy`
- **Models**: `ml_service/models/saved/*.pth`
- **Logs**: `ml_service/logs/neurobright.log`

## 🎓 Learning Resources

### Understanding the Pipeline

1. **Ingestion**: Read raw EEG from Arduino
2. **Preprocessing**: Filter noise, create windows
3. **Features**: Extract brain wave characteristics
4. **Training**: Train EEGNet classifier
5. **Evaluation**: Measure performance
6. **Inference**: Real-time prediction
7. **Adaptive**: Adjust learning content

### Key Concepts

- **Windowing**: 2-second windows with 0.5s overlap
- **Normalization**: Zero mean, unit variance per channel
- **Artifact Rejection**: Remove noisy windows
- **Majority Vote**: Smooth predictions over 5 windows
- **Hysteresis**: Wait 10s before adapting

## 🔧 Advanced Configuration

### Adjust Window Size

```yaml
windowing:
  window_seconds: 2.0    # Change to 1.0 for faster response
  step_seconds: 0.5      # Change to 0.25 for more predictions
```

### Adjust Model Architecture

```yaml
model:
  F1: 16      # Temporal filters
  D: 4        # Depth multiplier
  F2: 64      # Pointwise filters
  dropout: 0.2765
```

### Adjust Training

```yaml
training:
  epochs: 194
  batch_size: 64
  learning_rate: 0.009923
  patience: 20  # Early stopping patience
```

## 📞 Getting Help

1. Check logs: `ml_service/logs/neurobright.log`
2. Review config: `ml_service/config/config.yaml`
3. Read documentation: `README.md`, `MIGRATION_GUIDE.md`
4. Test hardware: `python app.py --mode test`

## 🎉 Success Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Hardware connected and tested
- [ ] Training data collected (3 states)
- [ ] Data preprocessed
- [ ] Model trained (>80% accuracy)
- [ ] Real-time inference working
- [ ] API server running (optional)

---

**You're ready to use NeuroBright! [NeuroBright]**
