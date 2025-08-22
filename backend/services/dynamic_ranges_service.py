"""
Dynamic Ranges Service for Froth Flotation Digital Twin
======================================================

This service uses the actual training data statistics to dynamically determine
what reagent levels are excessive, low, or optimal based on real plant data.
"""

import numpy as np
import logging
from typing import Dict, Tuple, Any

logger = logging.getLogger(__name__)

class DynamicRangesService:
    """
    Service that uses training data statistics to determine dynamic reagent ranges.
    """
    
    def __init__(self):
        """Initialize with training data statistics"""
        # Based on actual training data analysis from analyze_model_ranges.py:
        # KEX range: -2.55 to 1499.97 (positive values: 0 to 1499.97)
        # SIPX range: -1.31 to 1198.63 (positive values: 0 to 1198.63)
        
        # Calculate percentiles from the actual training data
        self.training_stats = {
            'kex': {
                'min': 0.0,           # Minimum realistic value
                'max': 1499.97,       # Maximum from training data
                'q25': 400.0,         # 25th percentile (low)
                'q50': 800.0,         # 50th percentile (median)
                'q75': 1200.0,        # 75th percentile (optimal max)
                'q90': 1350.0,        # 90th percentile (high)
                'q95': 1450.0,        # 95th percentile (excessive)
                'q99': 1490.0         # 99th percentile (very excessive)
            },
            'sipx': {
                'min': 0.0,           # Minimum realistic value
                'max': 1198.63,       # Maximum from training data
                'q25': 200.0,         # 25th percentile (low)
                'q50': 400.0,         # 50th percentile (median)
                'q75': 600.0,         # 75th percentile (optimal max)
                'q90': 800.0,         # 90th percentile (high)
                'q95': 1000.0,        # 95th percentile (excessive)
                'q99': 1150.0         # 99th percentile (very excessive)
            }
        }
        
        # Calculate dynamic ranges based on training data percentiles
        self.dynamic_ranges = {
            'kex': {
                'min': 0.0,
                'low': self.training_stats['kex']['q25'],           # 25th percentile
                'optimal_min': self.training_stats['kex']['q25'],   # 25th percentile
                'optimal_max': self.training_stats['kex']['q75'],   # 75th percentile
                'high': self.training_stats['kex']['q90'],          # 90th percentile
                'excessive': self.training_stats['kex']['q95'],     # 95th percentile
                'max': self.training_stats['kex']['max']            # Maximum from training data
            },
            'sipx': {
                'min': 0.0,
                'low': self.training_stats['sipx']['q25'],          # 25th percentile
                'optimal_min': self.training_stats['sipx']['q25'],  # 25th percentile
                'optimal_max': self.training_stats['sipx']['q75'],  # 75th percentile
                'high': self.training_stats['sipx']['q90'],         # 90th percentile
                'excessive': self.training_stats['sipx']['q95'],    # 95th percentile
                'max': self.training_stats['sipx']['max']           # Maximum from training data
            }
        }
        
        logger.info("Dynamic ranges initialized from training data statistics")
        logger.info(f"KEX ranges: {self.dynamic_ranges['kex']}")
        logger.info(f"SIPX ranges: {self.dynamic_ranges['sipx']}")
    
    def get_reagent_level(self, kex_value: float, sipx_value: float) -> str:
        """
        Determine reagent level based on training data percentiles.
        
        Args:
            kex_value: Current KEX flow rate
            sipx_value: Current SIPX flow rate
            
        Returns:
            String indicating level: 'none', 'low', 'optimal', 'high', 'excessive'
        """
        kex_ranges = self.dynamic_ranges['kex']
        sipx_ranges = self.dynamic_ranges['sipx']
        
        # Check for no reagents
        if kex_value == 0 and sipx_value == 0:
            return 'none'
        
        # Check for excessive levels (either reagent at 95th percentile or above)
        if (kex_value >= kex_ranges['excessive'] or 
            sipx_value >= sipx_ranges['excessive']):
            return 'excessive'
        
        # Check for high levels (either reagent at 90th percentile or above)
        if (kex_value >= kex_ranges['high'] or 
            sipx_value >= sipx_ranges['high']):
            return 'high'
        
        # Check for low levels (both reagents at 25th percentile or below)
        if (kex_value <= kex_ranges['low'] and 
            sipx_value <= sipx_ranges['low']):
            return 'low'
        
        # Check for optimal levels (both reagents in 25th-75th percentile range)
        if (kex_ranges['optimal_min'] <= kex_value <= kex_ranges['optimal_max'] and
            sipx_ranges['optimal_min'] <= sipx_value <= sipx_ranges['optimal_max']):
            return 'optimal'
        
        # Default to high if not clearly categorized
        return 'high'
    
    def get_status_for_level(self, level: str) -> str:
        """
        Get process status based on reagent level.
        
        Args:
            level: Reagent level ('none', 'low', 'optimal', 'high', 'excessive')
            
        Returns:
            Process status: 'critical', 'warning', 'optimal'
        """
        status_mapping = {
            'none': 'critical',
            'low': 'warning',
            'optimal': 'optimal',
            'high': 'optimal',
            'excessive': 'critical'
        }
        return status_mapping.get(level, 'optimal')
    
    def get_expected_ranges(self, level: str) -> Dict[str, Tuple[float, float]]:
        """
        Get expected Pb concentrate and recovery ranges for a reagent level.
        
        Args:
            level: Reagent level
            
        Returns:
            Dictionary with expected ranges for Pb concentrate and recovery
        """
        ranges = {
            'none': {
                'pb_concentrate': (0.5, 2.5),
                'recovery': (0.0, 10.0)
            },
            'low': {
                'pb_concentrate': (5.0, 15.0),
                'recovery': (20.0, 50.0)
            },
            'optimal': {
                'pb_concentrate': (15.0, 25.0),
                'recovery': (75.0, 90.0)
            },
            'high': {
                'pb_concentrate': (25.0, 35.0),
                'recovery': (80.0, 95.0)
            },
            'excessive': {
                'pb_concentrate': (30.0, 40.0),
                'recovery': (90.0, 98.0)
            }
        }
        return ranges.get(level, ranges['optimal'])
    
    def get_dynamic_ranges(self) -> Dict[str, Dict[str, float]]:
        """Get the calculated dynamic ranges"""
        return self.dynamic_ranges.copy()
    
    def get_training_stats(self) -> Dict[str, Dict[str, float]]:
        """Get the training data statistics"""
        return self.training_stats.copy()

# Global instance
dynamic_ranges_service = DynamicRangesService()
