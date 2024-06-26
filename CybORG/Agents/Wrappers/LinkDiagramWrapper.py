from copy import deepcopy
from pprint import pprint
from prettytable import PrettyTable

from CybORG.Shared.Enums import TrinaryEnum
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper

class LinkDiagramWrapper(BaseWrapper):
    def __init__(self, env: BaseWrapper = None):
        super().__init__(env)
        