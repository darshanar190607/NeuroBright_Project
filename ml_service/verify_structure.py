"""Verify NeuroBright restructured project integrity."""

import sys
from pathlib import Path

# Add ml_service to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config

logger = get_logger(__name__)


def check_file_exists(filepath, description):
    """Check if file exists."""
    if filepath.exists():
        logger.info(f"[OK] {description}: {filepath.name}")
        return True
    else:
        logger.error(f"[FAIL] {description}: {filepath.name} NOT FOUND")
        return False


def verify_structure():
    """Verify project structure."""
    log_pipeline_step("Project Structure Verification")
    
    base_dir = Path(__file__).parent
    checks_passed = 0
    checks_total = 0
    
    # Check critical files
    critical_files = [
        (base_dir / 'config' / 'config.yaml', 'Configuration'),
        (base_dir / 'app.py', 'CLI Entry Point'),
        (base_dir / 'requirements.txt', 'Dependencies'),
        (base_dir / 'setup.py', 'Setup Script'),
    ]
    
    logger.info("\n=== Critical Files ===")
    for filepath, desc in critical_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Check pipeline modules
    pipeline_modules = [
        'ingestion/arduino_reader.py',
        'ingestion/record_session.py',
        'ingestion/test_connection.py',
        'preprocessing/filters.py',
        'preprocessing/windowing.py',
        'preprocessing/artifact_rejection.py',
        'preprocessing/process_pipeline.py',
        'features/band_powers.py',
        'features/hjorth_params.py',
        'features/spectral_entropy.py',
        'features/feature_extractor.py',
        'training/dataset.py',
        'training/eegnet.py',
        'training/train.py',
        'training/tune.py',
        'inference/realtime_engine.py',
        'adaptive/learning_engine.py',
    ]
    
    logger.info("\n=== Pipeline Modules ===")
    for module in pipeline_modules:
        filepath = base_dir / 'pipeline' / module
        checks_total += 1
        if check_file_exists(filepath, f"Pipeline: {module}"):
            checks_passed += 1
    
    # Check API modules
    api_modules = [
        'main.py',
        'schemas.py',
        'websocket_manager.py',
    ]
    
    logger.info("\n=== API Modules ===")
    for module in api_modules:
        filepath = base_dir / 'api' / module
        checks_total += 1
        if check_file_exists(filepath, f"API: {module}"):
            checks_passed += 1
    
    # Check utilities
    util_modules = [
        'logger.py',
        'exceptions.py',
        'config_loader.py',
    ]
    
    logger.info("\n=== Utilities ===")
    for module in util_modules:
        filepath = base_dir / 'utils' / module
        checks_total += 1
        if check_file_exists(filepath, f"Utils: {module}"):
            checks_passed += 1
    
    # Check directories
    directories = [
        'data/raw',
        'data/processed',
        'data/external',
        'models/saved',
        'logs',
    ]
    
    logger.info("\n=== Directories ===")
    for directory in directories:
        dirpath = base_dir / directory
        checks_total += 1
        if dirpath.exists():
            logger.info(f"[OK] Directory: {directory}")
            checks_passed += 1
        else:
            logger.error(f"[FAIL] Directory: {directory} NOT FOUND")
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"Verification Results: {checks_passed}/{checks_total} checks passed")
    
    if checks_passed == checks_total:
        logger.info("[OK] ALL CHECKS PASSED - Project structure is correct!")
        return True
    else:
        logger.error(f"[FAIL] {checks_total - checks_passed} checks failed")
        return False


def verify_config():
    """Verify configuration."""
    log_pipeline_step("Configuration Verification")
    
    try:
        config = load_config()
        
        required_keys = [
            'hardware',
            'signal',
            'windowing',
            'bands',
            'model',
            'training',
            'optuna',
            'api',
            'recording',
            'paths'
        ]
        
        logger.info("\n=== Configuration Keys ===")
        all_present = True
        for key in required_keys:
            if key in config:
                logger.info(f"[OK] {key}")
            else:
                logger.error(f"[FAIL] {key} NOT FOUND")
                all_present = False
        
        if all_present:
            logger.info("\n[OK] Configuration is valid")
            return True
        else:
            logger.error("\n[FAIL] Configuration is incomplete")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] Configuration error: {e}")
        return False


def verify_imports():
    """Verify critical imports."""
    log_pipeline_step("Import Verification")
    
    imports_to_test = [
        ('utils.logger', 'get_logger'),
        ('utils.config_loader', 'load_config'),
        ('utils.exceptions', 'HardwareConnectionError'),
        ('pipeline.ingestion.arduino_reader', 'ArduinoReader'),
        ('pipeline.preprocessing.filters', 'notch_filter'),
        ('pipeline.training.eegnet', 'EEGNet'),
        ('pipeline.training.dataset', 'EEGDataset'),
        ('api.schemas', 'BrainStateResponse'),
    ]
    
    logger.info("\n=== Import Tests ===")
    all_passed = True
    
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            logger.info(f"[OK] {module_name}.{class_name}")
        except Exception as e:
            logger.error(f"[FAIL] {module_name}.{class_name}: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("\n[OK] All imports successful")
        return True
    else:
        logger.error("\n[FAIL] Some imports failed")
        return False


def main():
    """Run all verifications."""
    print("\n" + "="*70)
    print("  NeuroBright Structure Verification")
    print("="*70 + "\n")
    
    results = []
    
    # Run verifications
    results.append(("Structure", verify_structure()))
    results.append(("Configuration", verify_config()))
    results.append(("Imports", verify_imports()))
    
    # Final summary
    log_pipeline_step("Final Summary")
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        logger.info(f"{name}: {status}")
    
    if all_passed:
        logger.info("\nALL VERIFICATIONS PASSED!")
        logger.info("Project is ready to use.")
        logger.info("\nNext steps:")
        logger.info("  1. python app.py --mode test")
        logger.info("  2. python app.py --mode collect")
        logger.info("  3. python app.py --mode train")
        return 0
    else:
        logger.error("\nSOME VERIFICATIONS FAILED")
        logger.error("Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
