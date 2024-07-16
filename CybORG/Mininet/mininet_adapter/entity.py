from dataclasses import dataclass, field
from typing import Any

from CybORG.Mininet import MininetAdapter

@dataclass
class Entity:
    """_summary_
    
    """
    isRegister: bool = False
    mininet_adpator: MininetAdapter = None
    def register(self, mininet_adpator):
        self.mininet_adpator = mininet_adpator # For Upper level access, upcalling purpose
        self.isRegister = True