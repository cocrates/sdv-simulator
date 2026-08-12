"""sdv-sim: SDV (Software Defined Vehicle) simulator.

E/E architecture modeling, in-vehicle communication (CAN/Ethernet) simulation,
and app runtime execution — driven by YAML definition files, verified via
declarative assertions, and automated through the ``sdv-sim`` CLI.
"""

from sdv_sim.core.component import Component, Message, TaskContext
from sdv_sim.core.engine import Simulator, SimulationResult, load, loads
from sdv_sim.core.events import Event
from sdv_sim.core.report import AssertionResult, LinkReport, Report, TaskReport

__all__ = [
    "Component",
    "Message",
    "TaskContext",
    "Simulator",
    "SimulationResult",
    "load",
    "loads",
    "Event",
    "Report",
    "LinkReport",
    "TaskReport",
    "AssertionResult",
]

__version__ = "0.1.0"
