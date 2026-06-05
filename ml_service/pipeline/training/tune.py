"""Hyperparameter tuning with Optuna."""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import numpy as np
from pathlib import Path
import optuna
from optuna.pruners import MedianPruner

from .eegnet import EEGNet
from .dataset import EEGDataset
from .train import train_epoch, validate
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config

logger = get_logger(__name__)


def objective(trial, X, y, config):
    """Optuna objective function."""
    
    F1 = trial.suggest_int('F1', 8, 32, step=8)
    D = trial.suggest_int('D', 2, 8)
    dropout = trial.suggest_float('dropout', 0.1, 0.5)
    lr = trial.suggest_float('lr', 1e-4, 1e-2, log=True)
    batch_size = trial.suggest_categorical('batch_size', [32, 64, 128])
    
    dataset = EEGDataset(X, y)
    val_size = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # FIXED — reads n_channels from config, not hardcoded 3
    model = EEGNet(
        n_classes=config['model']['n_classes'],
        n_channels=config['model']['n_channels'],
        n_samples=config['model']['n_samples'],
        F1=F1, D=D, F2=F1*D, dropout=dropout
    ).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(30):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        trial.report(val_acc, epoch)
        
        if trial.should_prune():
            raise optuna.TrialPruned()
    
    return val_acc


def run_tuning():
    """Run Optuna hyperparameter search."""
    log_pipeline_step("Hyperparameter Tuning")
    
    config = load_config()
    
    processed_dir = Path(config['paths']['processed_data'])
    X = np.load(processed_dir / 'X_windows.npy')
    y = np.load(processed_dir / 'y_labels.npy')
    
    logger.info(f"Loaded data: {X.shape}")
    
    study = optuna.create_study(
        direction='maximize',
        pruner=MedianPruner()
    )
    
    study.optimize(
        lambda trial: objective(trial, X, y, config),
        n_trials=config['optuna']['n_trials']
    )
    
    logger.info(f"\n[OK] Best accuracy: {study.best_value:.4f}")
    logger.info(f"[OK] Best params: {study.best_params}")
    
    # Retrain with best params and save as tuned model
    logger.info("\nRetraining with best parameters...")
    best = study.best_params
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dataset = EEGDataset(X, y)
    val_size = int(len(dataset) * config['training']['val_split'])
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(config['training']['random_seed'])
    )
    
    train_loader = DataLoader(train_dataset, batch_size=best['batch_size'], shuffle=True)
    val_loader   = DataLoader(val_dataset,   batch_size=best['batch_size'], shuffle=False)
    
    model = EEGNet(
        n_classes=config['model']['n_classes'],
        n_channels=config['model']['n_channels'],
        n_samples=config['model']['n_samples'],
        F1=best['F1'], D=best['D'],
        F2=best['F1'] * best['D'],
        dropout=best['dropout']
    ).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer  = optim.Adam(model.parameters(), lr=best['lr'])
    scheduler  = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config['training']['epochs']
    )
    
    best_val_acc = 0
    model_path = Path(config['paths']['saved_models']) / 'eegnet_tuned.pth'
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(config['training']['epochs']):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc     = validate(model, val_loader, criterion, device)
        scheduler.step()
        
        logger.info(f"Epoch {epoch+1}: train_acc={train_acc:.4f} val_acc={val_acc:.4f}")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)
    
    logger.info(f"\n[OK] Tuned model saved to: {model_path}")
    logger.info(f"[OK] Best tuned accuracy: {best_val_acc:.4f}")


if __name__ == '__main__':
    run_tuning()