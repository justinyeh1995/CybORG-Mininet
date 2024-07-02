import pytest
import inspect

from CybORG.Mininet.mininet_adapter import YamlTopologyManager

class TestMininetYamlTopologyManager:
    def __init__(self):
        self.yaml_topo_generator = YamlTopologyManager()