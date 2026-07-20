#!/usr/bin/env python3
"""Generate the exact BCW/Yagzhev dimension-79 certificate.

The output is deterministic for the pinned Python/SymPy environment and is
written atomically. All mathematical checks use exact symbolic arithmetic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import sympy as s

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "artifacts/bcw-yagzhev-certificate.schema.json"
GENERATOR_REL = "scripts/bcw_yagzhev_certificate.py"
VERIFIER_REL = "scripts/verify_bcw_yagzhev_artifact.py"
PAPER_REL = "ahora-sabemos-v1.0.tex"


class VerificationError(RuntimeError):
    """Raised when an exact identity required by the certificate fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def monomial(variables: Sequence[s.Symbol], exponents: Sequence[int]) -> s.Expr:
    return s.prod(variable**exponent for variable, exponent in zip(variables, exponents))


def homogeneous_part(expression: s.Expr, variables: Sequence[s.Symbol], degree: int) -> s.Expr:
    return s.Add(
        *[
            coefficient * monomial(variables, exponents)
            for exponents, coefficient in s.Poly(expression, *variables).terms()
            if sum(exponents) == degree
        ]
    )


def evaluate(expression: s.Expr, variables: Sequence[s.Symbol], point: Sequence[s.Rational]) -> s.Expr:
    return s.expand(expression).subs(dict(zip(variables, point)))


def is_zero(expression: s.Expr) -> bool:
    return s.expand(expression) == 0


def rational_string(value: s.Expr) -> str:
    value = s.Rational(value)
    return str(value)


def polynomial_record(expression: s.Expr, variables: Sequence[s.Symbol]) -> dict[str, object]:
    polynomial = s.Poly(s.expand(expression), *variables, domain=s.QQ)
    terms = []
    for exponents, coefficient in polynomial.terms():
        if coefficient == 0:
            continue
        terms.append(
            {
                "coefficient": rational_string(coefficient),
                "exponents": [int(exponent) for exponent in exponents],
            }
        )
    return {"expression": s.sstr(s.expand(expression)), "terms": terms}


def point_record(point: Sequence[s.Expr]) -> list[str]:
    return [rational_string(coordinate) for coordinate in point]


def verify_stabilization_step(
    old_variables: list[s.Symbol],
    old_map: list[s.Expr],
    component: int,
    left_factor: s.Expr,
    right_factor: s.Expr,
    u: s.Symbol,
    v: s.Symbol,
    new_map: list[s.Expr],
) -> None:
    """Check the exact row identity proving preservation of the Jacobian."""
    n = len(old_variables)
    new_variables = old_variables + [u, v]
    old_jacobian = s.Matrix(old_map).jacobian(old_variables)
    new_jacobian = s.Matrix(new_map).jacobian(new_variables)
    corrected = (
        new_jacobian.row(component)
        + (v + right_factor) * new_jacobian.row(n)
        + (u + left_factor) * new_jacobian.row(n + 1)
    )
    target = list(old_jacobian.row(component)) + [s.Integer(0), s.Integer(0)]
    require(
        all(is_zero(corrected[index] - target[index]) for index in range(n + 2)),
        f"Jacobian row identity failed at stabilization step {u}",
    )
    require(
        all(is_zero(new_map[index] - old_map[index]) for index in range(n) if index != component),
        "A stabilization step changed an unrelated component",
    )
    require(is_zero(new_map[n] - (u + left_factor)), "Incorrect first auxiliary component")
    require(is_zero(new_map[n + 1] - (v + right_factor)), "Incorrect second auxiliary component")
    require(s.diff(left_factor, u) == s.diff(left_factor, v) == 0, "P depends on a new variable")
    require(s.diff(right_factor, u) == s.diff(right_factor, v) == 0, "Q depends on a new variable")


def verify_final_block_identity(
    variables: list[s.Symbol],
    quadratic: list[s.Expr],
    cubic: list[s.Expr],
    y_variables: list[s.Symbol],
    homogenizer: s.Symbol,
    final_map: list[s.Expr],
) -> None:
    """Check the exact block-Jacobian identity used in homogenization."""
    n = len(variables)
    b_matrix = s.Matrix(quadratic).jacobian(variables)
    c_matrix = s.Matrix(cubic).jacobian(variables)
    block = s.Matrix(final_map[:-1]).jacobian(variables + y_variables)
    for row in range(n):
        for column in range(n):
            delta = s.Integer(row == column)
            require(
                is_zero(block[row, column] - delta - homogenizer * b_matrix[row, column]),
                f"Upper-left block identity failed at ({row}, {column})",
            )
            require(
                is_zero(block[row, n + column] - homogenizer**2 * delta),
                f"Upper-right block identity failed at ({row}, {column})",
            )
            require(
                is_zero(block[n + row, column] + c_matrix[row, column]),
                f"Lower-left block identity failed at ({row}, {column})",
            )
            require(
                is_zero(block[n + row, n + column] - delta),
                f"Lower-right block identity failed at ({row}, {column})",
            )
    scaling = dict(zip(variables, [homogenizer * variable for variable in variables]))
    require(
        all(is_zero(expression.xreplace(scaling) - homogenizer**2 * expression) for expression in quadratic),
        "Quadratic part is not homogeneous of degree two",
    )
    require(
        all(is_zero(expression.xreplace(scaling) - homogenizer**3 * expression) for expression in cubic),
        "Cubic part is not homogeneous of degree three",
    )
    require(
        all(s.diff(final_map[-1], variable) == 0 for variable in variables + y_variables),
        "Final homogenizing component depends on X or Y",
    )
    require(s.diff(final_map[-1], homogenizer) == 1, "Final homogenizing component is not T")


def build_exact_data() -> dict[str, object]:
    x, y, z = s.symbols("x y z")
    source_variables = [x, y, z]
    a = 1 + x * y
    source_map = [
        a**3 * z + y**2 * a * (4 + 3 * x * y),
        y + 3 * x * a**2 * z + 3 * x * y**2 * (4 + 3 * x * y),
        2 * x - 3 * x**2 * y - x**3 * z,
    ]
    source_det = s.factor(s.Matrix(source_map).jacobian(source_variables).det())
    require(source_det == -2, f"Expected source determinant -2, got {source_det}")

    source_points = [
        [s.Rational(0), s.Rational(0), -s.Rational(1, 4)],
        [s.Rational(1), -s.Rational(3, 2), s.Rational(13, 2)],
        [-s.Rational(1), s.Rational(3, 2), s.Rational(13, 2)],
    ]
    source_target = [-s.Rational(1, 4), s.Rational(0), s.Rational(0)]
    require(len({tuple(point) for point in source_points}) == 3, "Source collision points are not distinct")
    require(
        all([evaluate(component, source_variables, point) for component in source_map] == source_target for point in source_points),
        "Source collision certificate failed",
    )

    variables = list(source_variables)
    current_map = [s.expand(source_map[2] / 2), s.expand(source_map[1]), s.expand(source_map[0])]
    normalized_det = s.factor(s.Matrix(current_map).jacobian(variables).det())
    require(normalized_det == 1, f"Expected normalized determinant 1, got {normalized_det}")
    points = [list(point) for point in source_points]
    target = [s.Rational(0), s.Rational(0), -s.Rational(1, 4)]
    require(
        all([evaluate(component, variables, point) for component in current_map] == target for point in points),
        "Normalized collision certificate failed",
    )

    history: list[dict[str, object]] = []
    profile = [
        {
            "step": 0,
            "dimension": len(variables),
            "max_degree": max(s.Poly(component, *variables).total_degree() for component in current_map),
            "terms": sum(len(s.Poly(component, *variables).terms()) for component in current_map),
        }
    ]

    while max(s.Poly(component, *variables).total_degree() for component in current_map) > 3:
        degree = max(s.Poly(component, *variables).total_degree() for component in current_map)
        chosen: tuple[int, tuple[int, ...], s.Expr] | None = None
        for component_index, component in enumerate(current_map):
            for exponents, coefficient in s.Poly(component, *variables).terms():
                if sum(exponents) == degree:
                    chosen = component_index, exponents, coefficient
                    break
            if chosen is not None:
                break
        require(chosen is not None, "No leading monomial was found")
        component_index, exponents, coefficient = chosen
        remaining = degree // 2
        left_exponents = []
        for exponent in exponents:
            take = min(exponent, remaining)
            left_exponents.append(take)
            remaining -= take
        right_exponents = [exponent - take for exponent, take in zip(exponents, left_exponents)]
        left_factor = coefficient * monomial(variables, left_exponents)
        right_factor = monomial(variables, right_exponents)
        step_number = len(history) + 1
        u, v = s.symbols(f"u{step_number} v{step_number}")
        old_variables = list(variables)
        old_map = list(current_map)
        new_map = list(old_map)
        new_map[component_index] = s.expand(old_map[component_index] - (u + left_factor) * (v + right_factor))
        new_map.extend([u + left_factor, v + right_factor])
        verify_stabilization_step(
            old_variables,
            old_map,
            component_index,
            left_factor,
            right_factor,
            u,
            v,
            new_map,
        )
        current_map = new_map
        points = [
            point + [-evaluate(left_factor, variables, point), -evaluate(right_factor, variables, point)]
            for point in points
        ]
        variables.extend([u, v])
        target.extend([s.Rational(0), s.Rational(0)])
        history.append(
            {
                "step": step_number,
                "component": component_index + 1,
                "degree_before": degree,
                "variables_before": [str(variable) for variable in old_variables],
                "new_variables": [str(u), str(v)],
                "P": left_factor,
                "Q": right_factor,
            }
        )
        profile.append(
            {
                "step": step_number,
                "dimension": len(variables),
                "max_degree": max(s.Poly(component, *variables).total_degree() for component in current_map),
                "terms": sum(len(s.Poly(component, *variables).terms()) for component in current_map),
            }
        )

    require(len(history) == 18, f"Expected 18 stabilization steps, got {len(history)}")
    require(len(variables) == 39, f"Expected intermediate dimension 39, got {len(variables)}")
    quadratic = [homogeneous_part(component, variables, 2) for component in current_map]
    cubic = [homogeneous_part(component, variables, 3) for component in current_map]
    require(
        all(is_zero(current_map[index] - variables[index] - quadratic[index] - cubic[index]) for index in range(len(variables))),
        "Intermediate map is not identity + quadratic + cubic",
    )
    require(
        all([evaluate(component, variables, point) for component in current_map] == target for point in points),
        "Intermediate collision certificate failed",
    )
    degree_counts = Counter(
        sum(exponents)
        for component in current_map
        for exponents, _coefficient in s.Poly(component, *variables).terms()
    )
    require(dict(sorted(degree_counts.items())) == {1: 39, 2: 47, 3: 38}, f"Unexpected degree counts: {degree_counts}")

    n = len(variables)
    y_variables = list(s.symbols(f"Y1:{n + 1}"))
    homogenizer = s.Symbol("T")
    final_variables = variables + y_variables + [homogenizer]
    final_map = (
        [variables[index] + y_variables[index] * homogenizer**2 + quadratic[index] * homogenizer for index in range(n)]
        + [y_variables[index] - cubic[index] for index in range(n)]
        + [homogenizer]
    )
    verify_final_block_identity(variables, quadratic, cubic, y_variables, homogenizer, final_map)
    final_points = []
    final_target = target + [s.Rational(0)] * n + [s.Rational(1)]
    for point in points:
        substitution = dict(zip(variables, point))
        final_point = point + [component.subs(substitution) for component in cubic] + [s.Rational(1)]
        final_points.append(final_point)
        require(
            [evaluate(component, final_variables, final_point) for component in final_map] == final_target,
            "Final collision certificate failed",
        )
    require(len(final_variables) == 79, f"Expected final dimension 79, got {len(final_variables)}")
    return {
        "source_variables": source_variables,
        "source_map": source_map,
        "source_points": source_points,
        "source_target": source_target,
        "normalized_map": [s.expand(source_map[2] / 2), s.expand(source_map[1]), s.expand(source_map[0])],
        "normalized_points": source_points,
        "normalized_target": [s.Rational(0), s.Rational(0), -s.Rational(1, 4)],
        "variables": variables,
        "intermediate_map": current_map,
        "quadratic": quadratic,
        "cubic": cubic,
        "history": history,
        "profile": profile,
        "degree_counts": degree_counts,
        "final_variables": final_variables,
        "final_map": final_map,
        "final_points": final_points,
        "final_target": final_target,
    }


def provenance_record() -> dict[str, object]:
    paths = {
        "generator": ROOT / GENERATOR_REL,
        "verifier": ROOT / VERIFIER_REL,
        "schema": ROOT / SCHEMA_REL,
        "paper_source": ROOT / PAPER_REL,
    }
    for label, path in paths.items():
        require(path.is_file(), f"Missing provenance file {label}: {path}")
    return {
        "generator": {
            "path": GENERATOR_REL,
            "sha256": sha256_file(paths["generator"]),
            "command": "python scripts/bcw_yagzhev_certificate.py --write-artifact artifacts/bcw-yagzhev-dim79.json",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "sympy_version": s.__version__,
        },
        "verifier": {"path": VERIFIER_REL, "sha256": sha256_file(paths["verifier"])},
        "schema": {"path": SCHEMA_REL, "sha256": sha256_file(paths["schema"])},
        "paper_source": {"path": PAPER_REL, "sha256": sha256_file(paths["paper_source"])},
    }


def build_payload(data: dict[str, object]) -> dict[str, object]:
    source_variables: list[s.Symbol] = data["source_variables"]  # type: ignore[assignment]
    variables: list[s.Symbol] = data["variables"]  # type: ignore[assignment]
    final_variables: list[s.Symbol] = data["final_variables"]  # type: ignore[assignment]
    return {
        "schema": "bcw-yagzhev-certificate-v2",
        "schema_file": SCHEMA_REL,
        "release": {
            "title": "Ahora sabemos que siempre era demasiado optimista",
            "title_en": "Now We Know That “Always” Was Too Optimistic",
            "author": "Javier Aragón",
            "email": "javier@affectiveAI.es",
            "version": "1.0",
            "date": "2026-07-20",
            "doi": "10.5281/zenodo.21460623",
            "doi_status": "reserved-pending-publication",
        },
        "format": {
            "coefficient_field": "Q",
            "arithmetic": "exact rational arithmetic",
            "readable_expressions": "SymPy sstr",
            "canonical_polynomials": "sparse-polynomial-v1",
            "term_encoding": "coefficient plus full exponent vector",
        },
        "provenance": provenance_record(),
        "dimensions": {"source": 3, "intermediate": len(variables), "final": len(final_variables)},
        "source_map": {
            "variables": [str(variable) for variable in source_variables],
            "components": [polynomial_record(component, source_variables) for component in data["source_map"]],
            "jacobian_determinant": "-2",
            "collision_points": [point_record(point) for point in data["source_points"]],
            "common_value": point_record(data["source_target"]),
        },
        "normalization": {
            "description": "K=(F3/2,F2,F1)",
            "component_indices": [3, 2, 1],
            "component_scalars": ["1/2", "1", "1"],
            "components": [polynomial_record(component, source_variables) for component in data["normalized_map"]],
            "jacobian_determinant": "1",
            "collision_points": [point_record(point) for point in data["normalized_points"]],
            "common_value": point_record(data["normalized_target"]),
        },
        "degree_reduction": {
            "index_base": 1,
            "profile": data["profile"],
            "steps": [
                {
                    "step": step["step"],
                    "component": step["component"],
                    "degree_before": step["degree_before"],
                    "variables_before": step["variables_before"],
                    "new_variables": step["new_variables"],
                    "P": polynomial_record(step["P"], [s.Symbol(name) for name in step["variables_before"]]),
                    "Q": polynomial_record(step["Q"], [s.Symbol(name) for name in step["variables_before"]]),
                }
                for step in data["history"]
            ],
        },
        "intermediate_map": {
            "variables": [str(variable) for variable in variables],
            "components": [polynomial_record(component, variables) for component in data["intermediate_map"]],
            "quadratic_components": [polynomial_record(component, variables) for component in data["quadratic"]],
            "cubic_components": [polynomial_record(component, variables) for component in data["cubic"]],
            "degree_counts": {str(degree): int(count) for degree, count in sorted(data["degree_counts"].items())},
            "decomposition": "identity + quadratic + cubic",
            "jacobian_determinant": "1",
        },
        "final_map": {
            "variables": [str(variable) for variable in final_variables],
            "components": [polynomial_record(component, final_variables) for component in data["final_map"]],
            "form": "identity + homogeneous cubic",
            "jacobian_determinant": "1",
            "collision_points": [point_record(point) for point in data["final_points"]],
            "common_value": point_record(data["final_target"]),
        },
        "claims": {
            "source_jacobian_determinant": "-2",
            "normalized_source_jacobian_determinant": "1",
            "elementary_jacobian_row_identities": 18,
            "homogeneous_decomposition": True,
            "final_block_jacobian_identity": True,
            "final_jacobian_determinant": "1",
            "final_nonlinear_part_homogeneous_degree": 3,
            "collision_points_pairwise_distinct": True,
            "rational_collision_certificates": 3,
        },
    }


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(rendered)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifact", metavar="PATH")
    parser.add_argument("--show-components", action="store_true")
    parser.add_argument("--show-points", action="store_true")
    arguments = parser.parse_args()
    try:
        data = build_exact_data()
        payload = build_payload(data)
        print("BCW degree-lowering steps: 18")
        print("intermediate dimension: 39")
        print("degree counts: {1: 39, 2: 47, 3: 38}")
        print("final cubic-homogeneous dimension: 79")
        print("source Jacobian determinant: -2")
        print("normalized and final Jacobian determinant: 1")
        print("three rational collision certificates: verified")
        if arguments.write_artifact:
            output = Path(arguments.write_artifact)
            if not output.is_absolute():
                output = ROOT / output
            atomic_write_json(output, payload)
            print(f"machine-readable artifact: {output}")
        if arguments.show_components:
            for index, component in enumerate(data["final_map"], 1):
                print(f"G{index} = {s.sstr(component)}")
        if arguments.show_points:
            for index, point in enumerate(data["final_points"], 1):
                print(f"P{index} = ({', '.join(map(str, point))})")
            print("common value = (" + ", ".join(map(str, data["final_target"])) + ")")
        return 0
    except (VerificationError, OSError, ValueError) as error:
        print(f"certificate generation failed: {error}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
