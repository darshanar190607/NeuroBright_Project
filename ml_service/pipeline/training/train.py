"""Train EEGNet model on preprocessed EEG data."""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import numpy as np
from pathlib import Path
import time
from sklearn.metrics import classification_report, confusion_matrix

from .eegnet import EEGNet
from .dataset import EEGDataset
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config
from utils.exceptions import ModelNotFoundError

logger = get_logger(__name__)


class EarlyStopping:
    """Early stopping to prevent overfitting."""
    
    def __init__(self, patience=20, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
    
    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for X_batch, y_batch in dataloader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == y_batch).sum().item()
        total += y_batch.size(0)
    
    return total_loss / len(dataloader), correct / total


def validate(model, dataloader, criterion, device):
    """Validate model."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == y_batch).sum().item()
            total += y_batch.size(0)
    
    return total_loss / len(dataloader), correct / total


def run_training():
    """Run complete training pipeline."""
    log_pipeline_step("Model Training")
    
    config = load_config()
    
    # Load processed data
    processed_dir = Path(config['paths']['processed_data'])
    X = np.load(processed_dir / 'X_windows.npy')
    y = np.load(processed_dir / 'y_labels.npy')
    
    logger.info(f"Loaded data: X={X.shape}, y={y.shape}")
    
    # Create dataset
    dataset = EEGDataset(X, y)
    
    # Split train/val
    val_size = int(len(dataset) * config['training']['val_split'])
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(config['training']['random_seed'])
    )
    
    logger.info(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False
    )
    
    # Initialize model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    model = EEGNet(
        n_classes=config['model']['n_classes'],
        n_channels=config['model']['n_channels'],
        n_samples=config['model']['n_samples'],
        F1=config['model']['F1'],
        D=config['model']['D'],
        F2=config['model']['F2'],
        dropout=config['model']['dropout']
    ).to(device)
    
    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=config['training']['learning_rate'],
        weight_decay=config['training']['weight_decay']
    )
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config['training']['epochs']
    )
    
    # Early stopping
    early_stopping = EarlyStopping(patience=config['training']['patience'])
    
    # Training loop
    best_val_acc = 0
    logger.info(f"\n{'='*70}")
    logger.info(f"{'Epoch':<8} {'Train Loss':<12} {'Train Acc':<12} {'Val Acc':<12} {'Time':<8}")
    logger.info(f"{'='*70}")
    
    for epoch in range(config['training']['epochs']):
        start_time = time.time()
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        scheduler.step()
        
        epoch_time = time.time() - start_time
        
        logger.info(
            f"{epoch+1:<8} {train_loss:<12.4f} {train_acc:<12.4f} {val_acc:<12.4f} {epoch_time:<8.2f}s"
        )
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            model_path = Path(config['paths']['saved_models']) / 'eegnet_best.pth'
            model_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), model_path)
        
        # Early stopping
        early_stopping(val_loss)
        if early_stopping.early_stop:
            logger.info(f"\nEarly stopping at epoch {epoch+1}")
            break
    
    logger.info(f"{'='*70}\n")
    logger.info(f"[OK] Best validation accuracy: {best_val_acc:.4f}")
    logger.info(f"[OK] Model saved to: {model_path}")
    
    # Final evaluation
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch)
            _, predicted = torch.max(outputs, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(y_batch.numpy())
    
    # Classification report
    class_names = config['model']['class_names']
    logger.info("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=class_names))
    
    logger.info("\nConfusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))


if __name__ == '__main__':
    run_training()
