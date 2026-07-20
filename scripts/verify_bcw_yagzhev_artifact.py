#!/usr/bin/env python3
"""Independently verify the BCW/Yagzhev JSON certificate.

This program uses only the Python standard library. It does not import SymPy
or the generator. Polynomial arithmetic is implemented with sparse exponent
vectors and fractions.Fraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_fraction(text: str) -> Fraction:
    require(isinstance(text, str) and text, f"Invalid rational value: {text!r}")
    try:
        result = Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise VerificationError(f"Invalid rational value {text!r}: {error}") from error
    require(str(result) == text, f"Rational is not in canonical reduced form: {text!r}")
    return result


@dataclass(frozen=True)
class Poly:
    nvars: int
    terms: tuple[tuple[tuple[int, ...], Fraction], ...]

    @staticmethod
    def from_dict(nvars: int, data: Mapping[tuple[int, ...], Fraction]) -> "Poly":
        cleaned: dict[tuple[int, ...], Fraction] = {}
        for exponents, coefficient in data.items():
            require(len(exponents) == nvars, "Exponent vector has the wrong length")
            require(all(isinstance(value, int) and value >= 0 for value in exponents), "Invalid exponent")
            if coefficient:
                cleaned[tuple(exponents)] = cleaned.get(tuple(exponents), Fraction(0)) + coefficient
        cleaned = {exponents: coefficient for exponents, coefficient in cleaned.items() if coefficient}
        return Poly(nvars, tuple(sorted(cleaned.items(), key=lambda item: item[0], reverse=True)))

    @staticmethod
    def zero(nvars: int) -> "Poly":
        return Poly(nvars, ())

    @staticmethod
    def constant(nvars: int, value: Fraction | int) -> "Poly":
        coefficient = Fraction(value)
        if not coefficient:
            return Poly.zero(nvars)
        return Poly.from_dict(nvars, {(0,) * nvars: coefficient})

    @staticmethod
    def variable(nvars: int, index: int) -> "Poly":
        require(0 <= index < nvars, "Variable index out of range")
        exponents = [0] * nvars
        exponents[index] = 1
        return Poly.from_dict(nvars, {tuple(exponents): Fraction(1)})

    def as_dict(self) -> dict[tuple[int, ...], Fraction]:
        return dict(self.terms)

    def extend(self, nvars: int) -> "Poly":
        require(nvars >= self.nvars, "Cannot shrink a polynomial by extension")
        if nvars == self.nvars:
            return self
        return Poly.from_dict(nvars, {exponents + (0,) * (nvars - self.nvars): coefficient for exponents, coefficient in self.terms})

    def __add__(self, other: "Poly") -> "Poly":
        require(self.nvars == other.nvars, "Polynomial dimensions differ")
        data = self.as_dict()
        for exponents, coefficient in other.terms:
            data[exponents] = data.get(exponents, Fraction(0)) + coefficient
        return Poly.from_dict(self.nvars, data)

    def __neg__(self) -> "Poly":
        return Poly.from_dict(self.nvars, {exponents: -coefficient for exponents, coefficient in self.terms})

    def __sub__(self, other: "Poly") -> "Poly":
        return self + (-other)

    def __mul__(self, other: "Poly") -> "Poly":
        require(self.nvars == other.nvars, "Polynomial dimensions differ")
        data: dict[tuple[int, ...], Fraction] = {}
        for left_exponents, left_coefficient in self.terms:
            for right_exponents, right_coefficient in other.terms:
                exponents = tuple(a + b for a, b in zip(left_exponents, right_exponents))
                data[exponents] = data.get(exponents, Fraction(0)) + left_coefficient * right_coefficient
        return Poly.from_dict(self.nvars, data)

    def scale(self, scalar: Fraction | int) -> "Poly":
        scalar = Fraction(scalar)
        return Poly.from_dict(self.nvars, {exponents: scalar * coefficient for exponents, coefficient in self.terms})

    def derivative(self, index: int) -> "Poly":
        require(0 <= index < self.nvars, "Derivative index out of range")
        data: dict[tuple[int, ...], Fraction] = {}
        for exponents, coefficient in self.terms:
            power = exponents[index]
            if not power:
                continue
            reduced = list(exponents)
            reduced[index] -= 1
            data[tuple(reduced)] = coefficient * power
        return Poly.from_dict(self.nvars, data)

    def evaluate(self, point: Sequence[Fraction]) -> Fraction:
        require(len(point) == self.nvars, "Point has the wrong dimension")
        total = Fraction(0)
        for exponents, coefficient in self.terms:
            value = coefficient
            for coordinate, exponent in zip(point, exponents):
                value *= coordinate**exponent
            total += value
        return total

    def degree(self) -> int:
        return max((sum(exponents) for exponents, _ in self.terms), default=-1)

    def homogeneous_part(self, degree: int) -> "Poly":
        return Poly.from_dict(self.nvars, {exponents: coefficient for exponents, coefficient in self.terms if sum(exponents) == degree})

    def is_homogeneous(self, degree: int) -> bool:
        return all(sum(exponents) == degree for exponents, _ in self.terms)


def parse_polynomial(record: object, nvars: int, label: str) -> Poly:
    require(isinstance(record, dict), f"{label} is not an object")
    require(set(record) == {"expression", "terms"}, f"{label} has unexpected fields")
    require(isinstance(record["expression"], str), f"{label}.expression is not text")
    raw_terms = record["terms"]
    require(isinstance(raw_terms, list), f"{label}.terms is not a list")
    data: dict[tuple[int, ...], Fraction] = {}
    seen: set[tuple[int, ...]] = set()
    listed_exponents: list[tuple[int, ...]] = []
    for index, term in enumerate(raw_terms):
        require(isinstance(term, dict) and set(term) == {"coefficient", "exponents"}, f"Malformed {label} term {index}")
        coefficient = parse_fraction(term["coefficient"])
        require(coefficient != 0, f"{label} stores a zero coefficient")
        raw_exponents = term["exponents"]
        require(isinstance(raw_exponents, list) and len(raw_exponents) == nvars, f"Wrong exponent length in {label}")
        require(all(isinstance(value, int) and value >= 0 for value in raw_exponents), f"Invalid exponents in {label}")
        exponents = tuple(raw_exponents)
        require(exponents not in seen, f"Duplicate monomial in {label}")
        seen.add(exponents)
        listed_exponents.append(exponents)
        data[exponents] = coefficient
    require(listed_exponents == sorted(listed_exponents, reverse=True), f"Terms are not canonically ordered in {label}")
    return Poly.from_dict(nvars, data)


def parse_point(value: object, dimension: int, label: str) -> list[Fraction]:
    require(isinstance(value, list) and len(value) == dimension, f"{label} has the wrong dimension")
    return [parse_fraction(coordinate) for coordinate in value]


def determinant_3(matrix: Sequence[Sequence[Poly]]) -> Poly:
    require(len(matrix) == 3 and all(len(row) == 3 for row in matrix), "Expected a 3x3 matrix")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def jacobian(polynomials: Sequence[Poly]) -> list[list[Poly]]:
    return [[polynomial.derivative(index) for index in range(polynomial.nvars)] for polynomial in polynomials]


def verify_file_record(record: object, label: str) -> None:
    require(isinstance(record, dict) and set(record) == {"path", "sha256"}, f"Malformed provenance record {label}")
    path = ROOT / record["path"]
    require(path.is_file(), f"Missing provenance file: {record['path']}")
    require(sha256_file(path) == record["sha256"], f"SHA-256 mismatch for {record['path']}")


def verify_artifact(artifact_path: Path) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    require(isinstance(artifact, dict), "Artifact root is not an object")
    require(artifact.get("schema") == "bcw-yagzhev-certificate-v2", "Artifact is not certificate v2")
    require(artifact.get("schema_file") == "artifacts/bcw-yagzhev-certificate.schema.json", "Unexpected schema path")
    dimensions = artifact.get("dimensions")
    require(dimensions == {"source": 3, "intermediate": 39, "final": 79}, "Unexpected dimensions")

    provenance = artifact.get("provenance")
    require(isinstance(provenance, dict), "Missing provenance")
    generator = provenance.get("generator")
    require(isinstance(generator, dict), "Missing generator provenance")
    require(set(generator) == {"path", "sha256", "command", "python_version", "sympy_version"}, "Malformed generator provenance")
    verify_file_record({"path": generator["path"], "sha256": generator["sha256"]}, "generator")
    require(isinstance(generator["command"], str) and generator["command"], "Missing generator command")
    require(isinstance(generator["python_version"], str) and generator["python_version"], "Missing Python version")
    require(isinstance(generator["sympy_version"], str) and generator["sympy_version"], "Missing SymPy version")
    for key in ("verifier", "schema", "paper_source"):
        verify_file_record(provenance.get(key), key)

    source = artifact.get("source_map")
    require(isinstance(source, dict), "Missing source map")
    source_variables = source.get("variables")
    require(source_variables == ["x", "y", "z"], "Unexpected source variables")
    source_components = [parse_polynomial(record, 3, f"source component {index}") for index, record in enumerate(source["components"], 1)]
    source_jacobian = jacobian(source_components)
    source_determinant = determinant_3(source_jacobian)
    require(source_determinant == Poly.constant(3, -2), "Source determinant is not -2")
    require(source.get("jacobian_determinant") == "-2", "Source determinant claim is not -2")
    source_points = [parse_point(point, 3, f"source collision point {index}") for index, point in enumerate(source["collision_points"], 1)]
    require(len({tuple(point) for point in source_points}) == 3, "Source collision points are not pairwise distinct")
    source_target = parse_point(source["common_value"], 3, "source common value")
    for point in source_points:
        require([component.evaluate(point) for component in source_components] == source_target, "Source collision verification failed")

    normalization = artifact.get("normalization")
    require(isinstance(normalization, dict), "Missing normalization")
    require(normalization.get("component_indices") == [3, 2, 1], "Unexpected normalization indices")
    require(normalization.get("component_scalars") == ["1/2", "1", "1"], "Unexpected normalization scalars")
    normalized_components = [parse_polynomial(record, 3, f"normalized component {index}") for index, record in enumerate(normalization["components"], 1)]
    expected_normalized = [source_components[2].scale(Fraction(1, 2)), source_components[1], source_components[0]]
    require(normalized_components == expected_normalized, "Normalization components do not equal (F3/2,F2,F1)")
    require(determinant_3(jacobian(normalized_components)) == Poly.constant(3, 1), "Normalized determinant is not 1")
    normalized_points = [parse_point(point, 3, f"normalized collision point {index}") for index, point in enumerate(normalization["collision_points"], 1)]
    normalized_target = parse_point(normalization["common_value"], 3, "normalized common value")
    for point in normalized_points:
        require([component.evaluate(point) for component in normalized_components] == normalized_target, "Normalized collision failed")

    reduction = artifact.get("degree_reduction")
    require(isinstance(reduction, dict) and reduction.get("index_base") == 1, "Malformed degree reduction")
    steps = reduction.get("steps")
    profile = reduction.get("profile")
    require(isinstance(steps, list) and len(steps) == 18, "Expected 18 reduction steps")
    require(isinstance(profile, list) and len(profile) == 19, "Expected 19 profile records")
    current_variables = ["x", "y", "z"]
    current_map = normalized_components
    computed_profile: list[dict[str, int]] = []

    def profile_record(step_number: int, polynomials: Sequence[Poly]) -> dict[str, int]:
        return {
            "step": step_number,
            "dimension": polynomials[0].nvars,
            "max_degree": max(poly.degree() for poly in polynomials),
            "terms": sum(len(poly.terms) for poly in polynomials),
        }

    computed_profile.append(profile_record(0, current_map))
    for expected_step, step in enumerate(steps, 1):
        require(isinstance(step, dict), f"Step {expected_step} is not an object")
        require(step.get("step") == expected_step, f"Incorrect step number at step {expected_step}")
        require(step.get("variables_before") == current_variables, f"variables_before mismatch at step {expected_step}")
        require(step.get("degree_before") == max(poly.degree() for poly in current_map), f"degree_before mismatch at step {expected_step}")
        component = step.get("component")
        require(isinstance(component, int) and 1 <= component <= len(current_map), f"Invalid component at step {expected_step}")
        new_names = step.get("new_variables")
        require(new_names == [f"u{expected_step}", f"v{expected_step}"], f"Unexpected new variables at step {expected_step}")
        n = len(current_variables)
        p_old = parse_polynomial(step["P"], n, f"P at step {expected_step}")
        q_old = parse_polynomial(step["Q"], n, f"Q at step {expected_step}")
        p = p_old.extend(n + 2)
        q = q_old.extend(n + 2)
        u = Poly.variable(n + 2, n)
        v = Poly.variable(n + 2, n + 1)
        old_extended = [poly.extend(n + 2) for poly in current_map]
        new_map = list(old_extended)
        new_map[component - 1] = old_extended[component - 1] - (u + p) * (v + q)
        new_map.extend([u + p, v + q])

        old_j = jacobian(current_map)
        new_j = jacobian(new_map)
        for column in range(n + 2):
            corrected = new_j[component - 1][column] + (v + q) * new_j[n][column] + (u + p) * new_j[n + 1][column]
            target = old_j[component - 1][column].extend(n + 2) if column < n else Poly.zero(n + 2)
            require(corrected == target, f"Jacobian row identity failed at step {expected_step}, column {column + 1}")
        current_variables.extend(new_names)
        current_map = new_map
        computed_profile.append(profile_record(expected_step, current_map))
    require(computed_profile == profile, "Degree-lowering profile does not match reconstructed maps")

    intermediate = artifact.get("intermediate_map")
    require(isinstance(intermediate, dict), "Missing intermediate map")
    require(intermediate.get("variables") == current_variables, "Intermediate variables do not match reduction")
    distributed_intermediate = [parse_polynomial(record, 39, f"intermediate component {index}") for index, record in enumerate(intermediate["components"], 1)]
    require(distributed_intermediate == current_map, "Distributed intermediate map differs from reconstructed map")
    quadratic = [poly.homogeneous_part(2) for poly in current_map]
    cubic = [poly.homogeneous_part(3) for poly in current_map]
    distributed_quadratic = [parse_polynomial(record, 39, f"quadratic component {index}") for index, record in enumerate(intermediate["quadratic_components"], 1)]
    distributed_cubic = [parse_polynomial(record, 39, f"cubic component {index}") for index, record in enumerate(intermediate["cubic_components"], 1)]
    require(distributed_quadratic == quadratic, "Quadratic components do not match")
    require(distributed_cubic == cubic, "Cubic components do not match")
    for index, component in enumerate(current_map):
        identity = Poly.variable(39, index)
        require(component == identity + quadratic[index] + cubic[index], f"Intermediate decomposition failed at component {index + 1}")
    degree_counts: dict[str, int] = {"1": 0, "2": 0, "3": 0}
    for component in current_map:
        for exponents, _ in component.terms:
            degree_counts[str(sum(exponents))] += 1
    require(degree_counts == {"1": 39, "2": 47, "3": 38}, f"Unexpected degree counts: {degree_counts}")
    require(intermediate.get("degree_counts") == degree_counts, "Stored degree counts are incorrect")

    final = artifact.get("final_map")
    require(isinstance(final, dict), "Missing final map")
    expected_final_variables = current_variables + [f"Y{index}" for index in range(1, 40)] + ["T"]
    require(final.get("variables") == expected_final_variables, "Unexpected final variables")
    nfinal = 79
    x_vars = [Poly.variable(nfinal, index) for index in range(39)]
    y_vars = [Poly.variable(nfinal, 39 + index) for index in range(39)]
    t = Poly.variable(nfinal, 78)
    quadratic_ext = [poly.extend(nfinal) for poly in quadratic]
    cubic_ext = [poly.extend(nfinal) for poly in cubic]
    expected_final = [x_vars[index] + y_vars[index] * t * t + quadratic_ext[index] * t for index in range(39)]
    expected_final += [y_vars[index] - cubic_ext[index] for index in range(39)]
    expected_final += [t]
    distributed_final = [parse_polynomial(record, nfinal, f"final component {index}") for index, record in enumerate(final["components"], 1)]
    require(distributed_final == expected_final, "Final map does not have the required block form")
    for index, component in enumerate(distributed_final):
        nonlinear = component - Poly.variable(nfinal, index)
        require(nonlinear.is_homogeneous(3), f"Nonlinear part of final component {index + 1} is not homogeneous cubic")

    # Independently check the four Jacobian block identities.
    b = [[quadratic[row].derivative(column).extend(nfinal) for column in range(39)] for row in range(39)]
    c = [[cubic[row].derivative(column).extend(nfinal) for column in range(39)] for row in range(39)]
    final_j = jacobian(distributed_final[:-1])
    zero = Poly.zero(nfinal)
    one = Poly.constant(nfinal, 1)
    for row in range(39):
        for column in range(39):
            delta = one if row == column else zero
            require(final_j[row][column] == delta + t * b[row][column], "Upper-left final Jacobian block failed")
            require(final_j[row][39 + column] == (t * t if row == column else zero), "Upper-right final Jacobian block failed")
            require(final_j[39 + row][column] == -c[row][column], "Lower-left final Jacobian block failed")
            require(final_j[39 + row][39 + column] == delta, "Lower-right final Jacobian block failed")

    final_points = [parse_point(point, 79, f"final collision point {index}") for index, point in enumerate(final["collision_points"], 1)]
    require(len({tuple(point) for point in final_points}) == 3, "Final collision points are not distinct")
    final_target = parse_point(final["common_value"], 79, "final common value")
    for point in final_points:
        require([component.evaluate(point) for component in distributed_final] == final_target, "Final collision certificate failed")

    claims = artifact.get("claims")
    expected_claims = {
        "source_jacobian_determinant": "-2",
        "normalized_source_jacobian_determinant": "1",
        "elementary_jacobian_row_identities": 18,
        "homogeneous_decomposition": True,
        "final_block_jacobian_identity": True,
        "final_jacobian_determinant": "1",
        "final_nonlinear_part_homogeneous_degree": 3,
        "collision_points_pairwise_distinct": True,
        "rational_collision_certificates": 3,
    }
    require(claims == expected_claims, "Claims record is inconsistent")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", default="artifacts/bcw-yagzhev-dim79.json")
    arguments = parser.parse_args()
    path = Path(arguments.artifact)
    if not path.is_absolute():
        path = ROOT / path
    try:
        require(path.is_file(), f"Artifact not found: {path}")
        verify_artifact(path)
    except (VerificationError, OSError, json.JSONDecodeError) as error:
        print(f"Certificate verification: FAIL\n{error}", file=sys.stderr)
        return 1
    print("Certificate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
