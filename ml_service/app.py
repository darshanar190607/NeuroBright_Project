"""NeuroBright CLI - Main entry point for all operations."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# ✅ ADD THIS LINE
sys.stdout.reconfigure(encoding='utf-8')

# Add ml_service to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger(__name__)


def print_banner(mode):
    """Print startup banner."""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   [NeuroBright] NeuroBright - Neuroadaptive Learning Platform        ║
║                                                              ║
║   Mode: {mode.upper():<50}                                   ║
║   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50}   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='NeuroBright - EEG Brain State Classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py --mode test       # Test hardware connection
  python app.py --mode collect    # Collect training data
  python app.py --mode process    # Preprocess raw data
  python app.py --mode train      # Train EEGNet model
  python app.py --mode tune       # Hyperparameter tuning
  python app.py --mode infer      # Real-time inference
  python app.py --mode server     # Start FastAPI server
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['test', 'collect', 'process', 'train', 'tune', 'evaluate', 'infer', 'server'],
        help='Operation mode'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/config.yaml)'
    )
    
    args = parser.parse_args()
    
    print_banner(args.mode)
    
    try:
        # Load config
        config = load_config(args.config)
        logger.info(f" Configuration loaded")
        
        # Execute mode
        if args.mode == 'test':
            from pipeline.ingestion.test_connection import test_hardware
            test_hardware()
        
        elif args.mode == 'collect':
            from pipeline.ingestion.record_session import main as collect_main
            collect_main()
        
        elif args.mode == 'process':
            from pipeline.preprocessing.process_pipeline import main as process_main
            process_main()
        
        elif args.mode == 'train':
            from pipeline.training.train import run_training
            run_training()
        
        elif args.mode == 'tune':
            from pipeline.training.tune import run_tuning
            run_tuning()
        
        elif args.mode == 'evaluate':
            logger.info("Evaluation mode - see training output for metrics")
        
        elif args.mode == 'infer':
            from pipeline.inference.realtime_engine import main as infer_main
            infer_main()
        
        elif args.mode == 'server':
            from api.main import run_server
            run_server()
        
        logger.info("\n Operation completed successfully")
        
    except KeyboardInterrupt:
        logger.info("\n Operation cancelled by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"\n Operation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
