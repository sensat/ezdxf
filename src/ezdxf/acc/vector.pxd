# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License
# type: ignore -- pylance sucks at type-checking cython files
# C-support functions:

cdef bint isclose(double a, double b, double rel_tol, double abs_tol)
cdef double normalize_rad_angle(double a)
cdef double normalize_deg_angle(double a)

from ._cpp_vec3 cimport CppVec3

cdef class Vec2:
    cdef readonly double x, y
    cdef CppVec3 to_cpp_vec3(self)

# Vec2 C-functions:
cdef Vec2 v2_add(Vec2 a, Vec2 b)
cdef Vec2 v2_sub(Vec2 a, Vec2 b)
cdef Vec2 v2_mul(Vec2 a, double factor)
cdef Vec2 v2_normalize(Vec2 a, double length)
cdef double v2_dot(Vec2 a, Vec2 b)
cdef double v2_det(Vec2 a, Vec2 b)
cdef double v2_dist(Vec2 a, Vec2 b)
cdef Vec2 v2_from_angle(double angle, double length)
cdef double v2_angle_between(Vec2 a, Vec2 b) except -1000
cdef Vec2 v2_lerp(Vec2 a, Vec2 b, double factor)
cdef Vec2 v2_ortho(Vec2 a, bint ccw)
cdef Vec2 v2_project(Vec2 a, Vec2 b)
cdef bint v2_isclose(Vec2 a, Vec2 b, double rel_tol, double abs_tol)
cdef Vec2 v2_from_cpp_vec3(CppVec3)
# magnitude = hypot(vec2.x, vec2.y)
# angle = atan2(vec2.y, vec2.x)

# Vec2 inplace operators only for internal usage in Cython modules!
# Vec2 objects must not be shared!
cdef void v2_iadd(Vec2 a, Vec2 b)
cdef void v2_isub(Vec2 a, Vec2 b)
cdef void v2_imul(Vec2 a, double factor)

cdef class Vec3:
    cdef readonly double x, y, z
    cdef CppVec3 to_cpp_vec3(self)

# Vec3 C-functions:
cdef Vec3 v3_add(Vec3 a, Vec3 b)
cdef Vec3 v3_sub(Vec3 a, Vec3 b)
cdef Vec3 v3_mul(Vec3 a, double factor)
cdef Vec3 v3_reverse(Vec3 a)
cdef double v3_dot(Vec3 a, Vec3 b)
cdef Vec3 v3_cross(Vec3 a, Vec3 b)
cdef double v3_magnitude_sqr(Vec3 a)
cdef double v3_magnitude(Vec3 a)
cdef double v3_dist(Vec3 a, Vec3 b)
cdef Vec3 v3_from_angle(double angle, double length)
cdef double v3_angle_between(Vec3 a, Vec3 b) except -1000
cdef double v3_angle_about(Vec3 a, Vec3 base, Vec3 target)
cdef Vec3 v3_normalize(Vec3 a, double length)
cdef Vec3 v3_lerp(Vec3 a, Vec3 b, double factor)
cdef Vec3 v3_ortho(Vec3 a, bint ccw)
cdef Vec3 v3_project(Vec3 a, Vec3 b)
cdef bint v3_isclose(Vec3 a, Vec3 b, double rel_tol, double abs_tol)
cdef Vec3 v3_from_cpp_vec3(CppVec3)

# ----------------------------------------
# CVec3 is a simple struct-based 3D vector
# ----------------------------------------

cdef struct CVec3:
    double x
    double y
    double z

cdef CVec3 cv3_from_vec3(Vec3 a)
cdef Vec3 v3_from_cvec3(CVec3 a)
cdef bint cv3_isclose(CVec3 a, CVec3 b, double rel_tol, double abs_tol)
cdef CVec3 cv3_add(CVec3 a, CVec3 b)
cdef CVec3 cv3_sub(CVec3 a, CVec3 b)
cdef CVec3 cv3_mul(CVec3 a, double factor)
cdef double cv3_magnitude_sqr(CVec3 a)
cdef double cv3_magnitude(CVec3 a)
cdef void cv3_iadd(CVec3 a, Vec3 b)
cdef void cv3_isub(CVec3 a, Vec3 b)
cdef void cv3_imul(CVec3 a, double factor)

