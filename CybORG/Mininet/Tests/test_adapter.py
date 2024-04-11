import pytest
import inspect

from CybORG.Mininet.MininetAdapter import MininetAdapter

class TestMininetAdapter:
    def __init__(self):
        self.mininet_adapter = MininetAdapter()
        
    def test_topology(self):
        assert 1 == 1