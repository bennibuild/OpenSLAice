from enum import Enum, auto
from typing import Set, List, Type
from src.slicer.core.constants import *
from src.slicer.core.helper_functions import round_TOL
import math


class Feature(Enum):
    MF = auto()     # Microfluidic
    TL = auto()     # Top Layer
    F = auto()      # Fine Section


class Section:
    def __init__(self, start: float, end: float):
        if start > end:
            t = start
            start = end
            end = t
        self.start = start
        self.end = end
    
    def includes_point(self, point: float) -> bool:
        return self.start <= point <= self.end

    def overlaps_with(self, other: "Section") -> bool:
        """same borders does not result in true"""
        return self.start < other.end and self.end > other.start
    
    @property
    def height(self):
        return self.end - self.start

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.start:.3f} -> {self.end:.3f})"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))


class AngleSection(Section):
    def __init__(self, start: float, end: float, angle: float, part_of_mf: bool = False):
        super().__init__(start, end)
        self.angle = angle
        self.part_of_mf = part_of_mf

    def set_angle(self, new_angle: float):
        self.angle = new_angle

    def __eq__(self, other):
        return (super().__eq__(other) and self.angle == other.angle and self.part_of_mf == other.part_of_mf)

    def __hash__(self):
        return hash((self.start, self.end, self.angle, self.part_of_mf))

    def __repr__(self):
        return f"{self.__class__.__name__} (z: {self.start:.3f} -> {self.end:.3f}; angle={self.angle:.3f}; part_of_mf={self.part_of_mf})\n"


class AngleSectionFragment(AngleSection):
    def __init__(self, start: float, end: float, angle: float, face_index: int):
        super().__init__(start, end, angle, False)
        self.face_index = face_index

    def __eq__(self, other):
        return (super().__eq__(other) and self.face_index == other.face_index)

    def __hash__(self):
        return hash((self.start, self.end, self.angle, self.face_index))

    def __repr__(self):
        return f"{self.__class__.__name__} (z: {self.start:.3f} -> {self.end:.3f}; angle={self.angle:.3f}, face_i={self.face_index})\n"


class FeatureSection(AngleSection):
    def __init__(self, start: float, end: float, angle: float, features: List[Feature]):
        super().__init__(start, end, angle)
        self.features: Set[Feature] = set(features)

    def add_feature(self, feature: Feature):
        self.features.add(feature)

    @classmethod
    def from_boundaries(cls, boundaries: List[float]) -> List["FeatureSection"]:
        sorted_bounds = sorted(boundaries)
        return [cls(start=sorted_bounds[i], end=sorted_bounds[i+1], angle=0.0, features=[]) for i in range(len(sorted_bounds) - 1)]


    def get_intersection_levels(self, min_lh: float, max_lh: float, z_res: float) -> set[float]:
        intersection_levels = set()
        print("==>", self)
        # input: 
        # - max_layer_height determined by the section angle
        # - F -> full range layerheight ~ MIN_LAYER_HEIGHT
        # - MF -> layerheight <= OPTIMAL_MF_LAYER_HEIGHT
        # - TL -> fist layer <= MIN_FIRST_LAYER_H -> in the end devide first layer as often as necessary
        # constrain: 
        #  a) layerheight = int * z_res
        #  b) section.height = int * layerheight
        #  c) layerheight >= min_lh

        # angle between 0-90° (0° -> vertical wall => bigger angle -> smaller layer height)
        max_lh = max_lh - ((max_lh - min_lh)/90 * self.angle)
        #if Feature.F in section.features:
        #    max_lh = min(min_lh, max_lh)
        if Feature.MF in self.features:
            max_lh = min(OPTIMAL_MF_LAYER_HEIGHT, max_lh)
        section_height = round_TOL(self.height, z_res)
        max_lh = min(max_lh, section_height)  # avoid overshooting section_height

        # find the optimal layer height that fits all constraints:
        # 1) round to z_res
        max_lh = round_TOL(max_lh, z_res)
        print (f"max_lh: {max_lh}")
        print (f"section_height: {section_height}")
        # 2) compute number of layers (ensure at least one) and ceiling (results in a smaller layer height) 
        num_layers = max(1, math.ceil(section_height / max_lh))
        print (f"num_layers: {num_layers}")
        # 3) Try to find an actual_lh that is a multiple of z_res and >= min_lh
        best_lh = min_lh
        min_error = float('inf')
        found = False
        best_n = 1
        max_num_layers = int(section_height / min_lh) # like floor -> garantee that min_lh is not undercut
        for n in range(num_layers, max_num_layers + 1):
            candidate_lh = section_height / n
            quantized_lh = round_TOL(candidate_lh, z_res)
            error = abs(candidate_lh - quantized_lh)
            if quantized_lh < min_lh:
                break  # Don't go below min layer height
            if error < z_res:
                actual_lh = quantized_lh
                num_layers = n
                found = True
                break
            # Track closest if no perfect match
            if error < min_error:
                min_error = error
                best_lh = quantized_lh
                best_n = n
        if not found:
            actual_lh = best_lh
            num_layers = best_n
            print(f"Warning: Could not quantize actual_lh perfectly, using closest value {actual_lh}")
        print (f"actual_lh: {actual_lh}")

        # adapting first layer height to the min acceptable value to improve surface finish
        first_lh = actual_lh
        if Feature.TL in self.features and actual_lh < MIN_FIRST_LAYER_H:
            for i in range(1, num_layers):
                if first_lh >= MIN_FIRST_LAYER_H:
                    break
                first_lh = first_lh + actual_lh
        first_lh_level = round_TOL(self.start + first_lh, z_res)

        # Generate intermediate levels
        levels = [first_lh_level]
        for i in range(1, num_layers):
            new_level = round_TOL(self.start + i * actual_lh, z_res)
            if new_level > first_lh_level:
                levels.append(new_level)
            else:
                continue
        intersection_levels.update(levels)
        
        # Ensure start and end are always in the result
        intersection_levels.add(self.start)
        intersection_levels.add(self.end)

        return intersection_levels


    def __repr__(self):
        return f"{self.__class__.__name__} (z: {self.start:.3f} -> {self.end:.3f}; angle={self.angle:.3f}, features={[f.name for f in self.features]})"



