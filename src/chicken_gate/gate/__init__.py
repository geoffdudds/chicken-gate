"""
Gate Control Module

Contains the main gate control logic, hardware drivers, and scheduling system.
"""

# Only import non-GPIO dependent modules by default
from .gate import Gate
from .gate_cmd import Cmd

# Main function and schedule can be imported explicitly when needed
# from .main import main
# from .schedule import Schedule

__all__ = ['Gate', 'Cmd']
