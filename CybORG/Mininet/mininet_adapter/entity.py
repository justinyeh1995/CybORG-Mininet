from dataclasses import dataclass, field
from typing import Any

# from CybORG.Mininet import MininetAdapter #This can cause circular import, but it is fine as of now

@dataclass
class Entity:
    """_summary_
    A class that is used to represent an entity in the Mininet Adapter
    mainly used for the purpose of upcalling the Mininet Adapter from the sub-classes
    """
    isRegister: bool = False
    mininet_adpator = None
    
    def register(self, mininet_adpator):
        self.mininet_adpator = mininet_adpator # For Upper level access, upcalling purpose
        self.isRegister = True