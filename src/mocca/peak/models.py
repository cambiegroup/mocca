import numpy as np

from dataclasses import dataclass
from typing import Optional, Any
# TODO: Replace Any by DadData


@dataclass(frozen = True)
class BasePeak():
    left : int
    right : int
    maximum : int

@dataclass(frozen = True)
class PickedPeak(BasePeak):
    dataset : Any  # DADData parent of peak
    idx : int
    
    def __eq__(self, other):
        if not isinstance(other, BasePeak):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return (self.left == other.left and
                self.right == other.right and
                self.maximum == other.maximum and
                self.dataset == other.dataset)

@dataclass(frozen = True, eq = False)
class CheckedPeak(PickedPeak):
    saturation : bool
    pure : bool

@dataclass(frozen = True, eq = False)
class AssignedPeak(CheckedPeak):
    # istd : bool
    compound_id : Optional[str]

@dataclass(frozen = True, eq = False)
class ProcessedPeak(AssignedPeak):
    integral : float
    concentration : Optional[float]