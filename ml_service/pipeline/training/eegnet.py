"""EEGNet architecture for brain state classification."""

import torch
import torch.nn as nn


class EEGNet(nn.Module):
    """
    EEGNet: Compact Convolutional Neural Network for EEG-based BCIs.
    
    Optimized hyperparameters from Optuna tuning:
    - F1=16, D=4, F2=64, dropout=0.2765
    """
    
    def __init__(self, n_classes=3, n_channels=1, n_samples=1000,
                 F1=16, D=4, F2=64, dropout=0.2765):
        """
        Initialize EEGNet.
        
        Args:
            n_classes (int): Number of output classes
            n_channels (int): Number of EEG channels
            n_samples (int): Number of time samples
            F1 (int): Number of temporal filters
            D (int): Depth multiplier for spatial filters
            F2 (int): Number of pointwise filters
            dropout (float): Dropout rate
        """
        super(EEGNet, self).__init__()
        
        self.n_classes = n_classes
        self.n_channels = n_channels
        self.n_samples = n_samples
        
        # Block 1: Temporal convolution + Spatial filtering
        self.block1 = nn.Sequential(
            nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False),
            nn.BatchNorm2d(F1),
            
            nn.Conv2d(F1, F1 * D, (n_channels, 1), groups=F1, bias=False),
            nn.BatchNorm2d(F1 * D),
            nn.ELU(),
            nn.AvgPool2d((1, 4)),
            nn.Dropout(dropout)
        )
        
        # Block 2: Separable convolution
        self.block2 = nn.Sequential(
            nn.Conv2d(F1 * D, F2, (1, 16), padding=(0, 8), groups=F1 * D, bias=False),
            nn.Conv2d(F2, F2, (1, 1), bias=False),
            nn.BatchNorm2d(F2),
            nn.ELU(),
            nn.AvgPool2d((1, 8)),
            nn.Dropout(dropout)
        )
        
        # Calculate flattened size
        self.feature_size = self._get_feature_size()
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(self.feature_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, n_classes)
        )
    
    def _get_feature_size(self):
        """Calculate size after convolutions."""
        with torch.no_grad():
            x = torch.zeros(1, 1, self.n_channels, self.n_samples)
            x = self.block1(x)
            x = self.block2(x)
            return x.numel()
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x (torch.Tensor): Input (batch, channels, samples)
        
        Returns:
            torch.Tensor: Logits (batch, n_classes)
        """
        # Add dimension for Conv2d: (batch, 1, channels, samples)
        x = x.unsqueeze(1)
        
        # Convolutional blocks
        x = self.block1(x)
        x = self.block2(x)
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Classify
        x = self.classifier(x)
        
        return x


if __name__ == '__main__':
    # Test EEGNet
    model = EEGNet(n_classes=3, n_channels=3, n_samples=1000)
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Test forward pass
    x = torch.randn(8, 3, 1000)  # Batch of 8
    y = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {y.shape}")
    print(f"Feature size: {model.feature_size}")
