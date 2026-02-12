from dataclasses import dataclass, field
from typing import Dict

@dataclass
class AssetGroup:
    items: Dict[str, float] = field(default_factory=dict)

@dataclass
class FamilyProfile:
    cash: AssetGroup = field(default_factory=AssetGroup)
    stable: AssetGroup = field(default_factory=AssetGroup)
    invest: AssetGroup = field(default_factory=AssetGroup)
    property: AssetGroup = field(default_factory=AssetGroup)
    other: AssetGroup = field(default_factory=AssetGroup)
    debt: AssetGroup = field(default_factory=AssetGroup)