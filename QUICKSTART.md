# NeuroBright - Quick Start Guide

## ✅ Project Setup Complete!

All files have been created successfully. Here's what you have:

### 📁 Project Structure
```
NeuroBright/
├── config/config.yaml          # All configuration settings
├── src/                        # Source code
│   ├── data/                  # Data collection & preprocessing
│   ├── models/                # EEGNet architecture
│   ├── training/              # Training & hyperparameter tuning
│   ├── inference/             # Real-time classification
│   ├── adaptive/              # Adaptive learning engine
│   └── utils/                 # Utilities & helpers
├── notebooks/                  # Jupyter notebooks (4 notebooks)
├── data/                      # Data storage
├── models/saved/              # Trained models
└── app.py                     # Main CLI application

Total Files Created: 35+
```

## 🚀 Getting Started

### Step 1: Install Dependencies
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install all dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Step 2: Configure Hardware
Edit `config/config.yaml` and set your Arduino COM port:
```yaml
hardware:
  port: "COM3"  # Change to your Arduino port
```

### Step 3: Test Hardware Connection
```bash
python app.py --mode test
```

### Step 4: Collect Training Data
```bash
python app.py --mode collect
```
This will record all 3 brain states (21 minutes total + breaks).

### Step 5: Train Model
```bash
python app.py --mode train
```

### Step 6: Run Real-Time Inference
```bash
python app.py --mode infer
```

## 📊 Using Jupyter Notebooks

Alternative workflow using notebooks:

1. **01_data_exploration.ipynb** - Explore configuration
2. **02_signal_recording_and_visualization.ipynb** - Record & visualize data
3. **03_model_training.ipynb** - Train the model
4. **04_results_analysis.ipynb** - Analyze results

```bash
jupyter notebook
```

## 🎯 Key Features Implemented

### ✅ Data Collection (src/data/collector.py)
- Serial communication with Arduino
- Real-time filtering (notch + bandpass)
- Artifact detection and rejection
- Progress tracking with tqdm
- Session metadata saving

### ✅ Signal Processing (src/utils/signal_utils.py)
- ADC to microvolt conversion
- Butterworth bandpass filter (1-45 Hz)
- Notch filter (50/60 Hz power line noise)
- Band power extraction (Delta, Theta, Alpha, Beta, Gamma)
- Hjorth parameters
- Spectral entropy
- Artifact checking

### ✅ Preprocessing (src/data/preprocessor.py)
- Sliding window creation (2s windows, 0.5s step)
- Per-channel normalization
- Artifact rejection
- Dataset statistics

### ✅ EEGNet Model (src/models/eegnet.py)
- Temporal convolution
- Depthwise spatial filtering
- Separable convolution
- Dropout regularization
- ~2000 parameters (lightweight!)

### ✅ Training (src/training/trainer.py)
- Adam optimizer
- Cosine annealing scheduler
- Class weight balancing
- Early stopping
- Training history tracking
- Best model checkpointing

### ✅ Hyperparameter Tuning (src/training/hyperparameter_tuner.py)
- Optuna integration
- Automatic pruning
- Configurable trials
- Best parameter logging

### ✅ Real-Time Inference (src/inference/realtime_engine.py)
- Sliding window buffer
- Real-time preprocessing
- Continuous prediction
- State statistics tracking

### ✅ Adaptive Learning (src/adaptive/learning_engine.py)
- State history tracking
- Break recommendations
- Difficulty adjustment
- Intervention suggestions

### ✅ Utilities
- Color-coded logging
- Custom exceptions with error codes
- Configuration management
- Comprehensive error handling

## 🔧 Configuration Options

All settings in `config/config.yaml`:

- **Hardware**: COM port, baud rate, channels, sampling rate
- **Signal Processing**: Filter parameters, artifact thresholds
- **Windowing**: Window size, step size
- **Model**: EEGNet architecture parameters
- **Training**: Epochs, batch size, learning rate, scheduler
- **Recording**: State durations, instructions, labels

## 📝 Brain States

1. **Focused (Label 0)**: Solve math problems continuously
2. **Drowsy (Label 1)**: Sit still, breathe slowly, relax
3. **Stressed (Label 2)**: Fast typing with time pressure

## 🎨 Visualizations Included

- Raw EEG time series
- Power spectral density (PSD)
- Band power comparison
- Spectrograms
- Training curves
- Confusion matrix
- Per-class accuracy

## 🐛 Troubleshooting

### Arduino Not Found
- Check COM port in config.yaml
- Verify Arduino is connected
- Install CH340 drivers if needed

### Signal Quality Issues
- Check electrode contact
- Apply conductive gel
- Reduce movement
- Check grounding

### Training Issues
- Ensure data is collected first
- Check processed data exists
- Verify GPU/CPU availability

## 📚 Next Steps

1. **Collect more data** - More training data = better accuracy
2. **Tune hyperparameters** - Run `python app.py --mode tune`
3. **Experiment with filters** - Adjust bandpass frequencies
4. **Try different tasks** - Customize recording instructions
5. **Add more states** - Extend to 4+ brain states

## 🎓 Code Quality

Every file includes:
- ✅ Complete docstrings
- ✅ Type hints in docstrings
- ✅ Error handling with custom exceptions
- ✅ Logging at every step
- ✅ Configuration-driven (no hardcoded values)
- ✅ Standalone execution support

## 📞 Support

Check logs in `logs/neurobright.log` for detailed debugging information.

---

**Ready to classify brain states in real-time! 🧠✨**
