#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from typing import (
    List,
    Iterable,
    Optional,
    Callable,
    TypeVar,
    Generic,
)
import abc
import copy
import enum
import itertools
import random
import time
from .binpacking import AbstractPacker

__all__ = ["DNA", "Selection", "FloatDNA", "RouletteSelection", "GeneticDriver"]


class MutationType(enum.Enum):
    FLIP = enum.auto()
    SWAP = enum.auto()


class DNA(abc.ABC):
    fitness: Optional[float] = None
    _data: List

    @classmethod
    @abc.abstractmethod
    def random(cls, length):
        ...

    @abc.abstractmethod
    def reset(self, values: Iterable):
        ...

    def copy(self):
        return copy.deepcopy(self)

    def _taint(self):
        self.fitness = None

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self._data == other._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)
        self._taint()

    def __iter__(self):
        return iter(self._data)

    def mutate(self, rate: float, mutation_type=MutationType.FLIP):
        for index in range(len(self)):
            if random.random() < rate:
                self._taint()
                if mutation_type == MutationType.FLIP:
                    self.flip_mutate_at(index)
                elif mutation_type == MutationType.SWAP:
                    self.swap_mutate(index, index - 1)
                else:
                    raise TypeError(mutation_type)

    @abc.abstractmethod
    def flip_mutate_at(self, index: int) -> None:
        ...

    def swap_mutate(self, i1: int, i2: int) -> None:
        tmp = self._data[i2]
        self._data[i2] = self._data[i1]
        self._data[i1] = tmp


def recombine_dna_1pcx(dna1: DNA, dna2: DNA, index: int) -> None:
    """Single point crossover."""
    recombine_dna_2pcx(dna1, dna2, index, len(dna1))


def recombine_dna_2pcx(dna1: DNA, dna2: DNA, i1: int, i2: int) -> None:
    """Two point crossover."""
    part1 = dna1[i1:i2]
    part2 = dna2[i1:i2]
    dna1[i1:i2] = part2
    dna2[i1:i2] = part1


class FloatDNA(DNA):
    __slots__ = ("_data", "fitness")

    def __init__(self, values: Iterable[float]):
        self._data: List[float] = list(values)
        self._check_valid_data()
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int) -> "FloatDNA":
        return cls(random.random() for _ in range(length))

    def _check_valid_data(self):
        if not all(0.0 <= v <= 1.0 for v in self._data):
            raise ValueError("data value out of range")

    def __str__(self):
        if self.fitness is None:
            fitness = ", fitness=None"
        else:
            fitness = f", fitness={self.fitness:.4f}"
        return f"{str([round(v, 4) for v in self._data])}{fitness}"

    def reset(self, values: Iterable[float]):
        self._data = list(values)
        self._check_valid_data()
        self._taint()

    def flip_mutate_at(self, index: int) -> None:
        self._data[index] = 1.0 - self._data[index]  # flip pick location


class BitDNA(DNA):
    __slots__ = ("_data", "fitness")

    def __init__(self, values: Iterable):
        self._data: List[bool] = list(bool(v) for v in values)
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int) -> "BitDNA":
        return cls(bool(random.randint(0, 1)) for _ in range(length))

    def __str__(self):
        if self.fitness is None:
            fitness = ", fitness=None"
        else:
            fitness = f", fitness={self.fitness:.4f}"
        return f"{str([int(v) for v in self._data])}{fitness}"

    def reset(self, values: Iterable) -> None:
        self._data = list(bool(v) for v in values)
        self._taint()

    def flip_mutate_at(self, index: int) -> None:
        self._data[index] = not self._data[index]


D = TypeVar("D", bound=DNA)


class Selection(abc.ABC, Generic[D]):
    @abc.abstractmethod
    def pick(self, count: int) -> Iterable[D]:
        ...


#############################################################################
# Optimizing only the order for the pack algorithm was not efficient, the
# BIGGER_FIRST strategy beats every other attempt!
# - schematic_packer() can be removed
#
# Next approach, find the optimal subset of items for the BIGGER_FIRST strategy
# to fill all bins
# 1. If all items fit into the bins, its done.
# 2. If not all items fit into the bins: search for the optimal subset of
#    items with the highest fitness.


class GeneticDriver:
    def __init__(
        self,
        packer: AbstractPacker,
        max_generations: int,
    ):
        if packer.is_packed:
            raise ValueError("packer is already packed")
        if max_generations < 1:
            raise ValueError("max_generations < 1")
        # data:
        self._packer = packer
        self._required_dna_length = len(packer.items)
        self._dna_strands: List[FloatDNA] = []

        # options:
        self._max_generations = int(max_generations)
        self._max_fitness: float = 1.0
        self._crossover_rate = 0.70
        self._mutation_rate = 0.001
        self.elitism: int = 2
        self.mutation_type1 = MutationType.FLIP
        self.mutation_type2 = MutationType.FLIP

        # state of last (current) generation:
        self.generation: int = 0
        self.runtime: float = 0.0
        self.best_dna = FloatDNA([])
        self.best_fitness: float = 0.0
        self.best_packer = packer
        self.stagnation: int = 0  # generations without improvement

    @property
    def max_fitness(self) -> float:
        return self._max_fitness

    @max_fitness.setter
    def max_fitness(self, value: float) -> None:
        if value > 1.0 or value < 0.0:
            raise ValueError("max_fitness not in range [0, 1]")
        self._max_fitness = value

    @property
    def crossover_rate(self) -> float:
        return self._crossover_rate

    @crossover_rate.setter
    def crossover_rate(self, value: float) -> None:
        if value > 1.0 or value < 0.0:
            raise ValueError("crossover_rate not in range [0, 1]")
        self._crossover_rate = value

    @property
    def mutation_rate(self) -> float:
        return self._mutation_rate

    @mutation_rate.setter
    def mutation_rate(self, value: float) -> None:
        if value > 1.0 or value < 0.0:
            raise ValueError("mutation_rate not in range [0, 1]")
        self._mutation_rate = value

    @property
    def is_executed(self) -> bool:
        return bool(self.generation)

    def add_dna(self, dna: FloatDNA):
        if not self.is_executed:
            if len(dna) != self._required_dna_length:
                raise ValueError(
                    f"invalid DNA length, requires {self._required_dna_length}"
                )
            self._dna_strands.append(dna)
        else:
            raise TypeError("already executed")

    def add_random_dna(self, count: int):
        for _ in range(count):
            self.add_dna(FloatDNA.random(self._required_dna_length))

    def execute(
        self,
        feedback: Callable[["GeneticDriver"], bool] = None,
        interval: float = 1.0,
        max_time: float = 1e99,
    ) -> None:
        if self.is_executed:
            raise TypeError("can only run once")
        if not self._dna_strands:
            print("no DNA defined!")
        t0 = time.perf_counter()
        start_time = t0
        for self.generation in range(1, self._max_generations + 1):
            self._measure_fitness()
            if self.best_fitness >= self._max_fitness:
                break
            t1 = time.perf_counter()
            self.runtime = t1 - start_time
            if self.runtime > max_time:
                break
            if feedback and t1 - t0 > interval:
                if feedback(self):  # stop if feedback() returns True
                    break
                t0 = t1
            self._next_generation()

    def _measure_fitness(self) -> None:
        self.stagnation += 1
        for dna in self._dna_strands:
            if dna.fitness is not None:
                continue
            p0 = self._packer.copy()
            p0.schematic_pack(iter(dna))
            fill_ratio = p0.get_fill_ratio()
            dna.fitness = fill_ratio
            if fill_ratio > self.best_fitness:
                self.best_fitness = fill_ratio
                self.best_packer = p0
                self.best_dna = dna.copy()
                self.stagnation = 0

    def _next_generation(self) -> None:
        selector: Selection[FloatDNA] = RouletteSelection(self._dna_strands)
        dna_strands: List[FloatDNA] = []
        count = len(self._dna_strands)

        if self.elitism > 0:
            dna_strands.extend([self.best_dna] * self.elitism)

        while len(dna_strands) < count:
            dna1, dna2 = selector.pick(2)
            dna1 = dna1.copy()
            dna2 = dna2.copy()
            if random.random() < self._crossover_rate:
                self._recombination(dna1, dna2)
            self._mutation(dna1, dna2)
            dna_strands.append(dna1)
            dna_strands.append(dna2)
        self._dna_strands = dna_strands

    def _recombination(self, dna1: DNA, dna2: DNA):
        i1 = random.randrange(0, self._required_dna_length)
        i2 = random.randrange(0, self._required_dna_length)
        if i1 > i2:
            i1, i2 = i2, i1
        recombine_dna_2pcx(dna1, dna2, i1, i2)

    def _mutation(self, dna1: DNA, dna2: DNA):
        mutation_rate = self._mutation_rate * self.stagnation
        dna1.mutate(mutation_rate, self.mutation_type1)
        dna2.mutate(mutation_rate, self.mutation_type2)


class RouletteSelection(Selection):
    def __init__(self, strands: Iterable[D]):
        self._strands: List[D] = list(strands)
        self._weights: List[float] = []
        self.update()

    def update(self):
        sum_fitness = sum(dna.fitness for dna in self._strands)
        if sum_fitness == 0.0:
            sum_fitness = 1.0
        self._weights = [dna.fitness / sum_fitness for dna in self._strands]

    def pick(self, count: int) -> Iterable[D]:
        return random.choices(self._strands, self._weights, k=count)
