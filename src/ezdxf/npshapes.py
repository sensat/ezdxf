#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable
import abc

import numpy as np
from ezdxf.math import Matrix44, Vec2, UVec
from ezdxf.path import AbstractPath, Path2d, Command

__all__ = ["NumpyPath2d", "NumpyPoints2d", "NumpyShapesException", "EmptyShapeError"]


class NumpyShapesException(Exception):
    pass


class EmptyShapeError(NumpyShapesException):
    pass


class NumpyShape2d(abc.ABC):
    """This is an optimization to store many 2D paths and polylines in a compact way
    without sacrificing basic functions like transformation and bounding box calculation.
    """

    _vertices: np.ndarray

    def extents(self) -> tuple[Vec2, Vec2]:
        """Returns the extents of the bounding box as tuple (extmin, extmax)."""
        v = self._vertices
        if len(v) > 0:
            return Vec2(v.min(0)), Vec2(v.max(0))
        else:
            raise EmptyShapeError("empty shape has no extends")

    def transform_inplace(self, m: Matrix44) -> None:
        """Transforms the vertices of the shape inplace."""
        v = self._vertices
        if len(v) == 0:
            return
        m.transform_array_inplace(v, 2)

    def vertices(self) -> list[Vec2]:
        """Returns the shape vertices as list of :class:`Vec2`."""
        return Vec2.list(self._vertices)


class NumpyPoints2d(NumpyShape2d):
    """Represents an array of 2D points stored as a ndarray."""

    def __init__(self, points: Iterable[UVec]) -> None:
        self._vertices = np.array(Vec2.list(points), dtype=np.float64)

    def __len__(self) -> int:
        return len(self._vertices)


class NumpyPath2d(NumpyShape2d):
    """Represents a 2D path, the path control vertices and commands are stored as ndarray."""

    def __init__(self, path: AbstractPath) -> None:
        if isinstance(path, Path2d):
            vertices = path.control_vertices()
        else:
            vertices = Vec2.list(path.control_vertices())
        if len(vertices) == 0:
            try:  # control_vertices() does not return start point of empty paths
                vertices = [path.start]
            except IndexError:
                vertices = [Vec2()]  # default start point of empty paths
        self._vertices = np.array(vertices, dtype=np.float64)
        self._commands = np.array(path.command_codes(), dtype=np.int8)

    def __len__(self) -> int:
        return len(self._commands)

    def to_path2d(self) -> Path2d:
        """Returns a new :class:`Path2d` instance."""
        vertices = [Vec2(v) for v in self._vertices]
        commands = [Command(c) for c in self._commands]
        return Path2d.from_vertices_and_commands(vertices, commands)
