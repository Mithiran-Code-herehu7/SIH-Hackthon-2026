from math import isfinite
from typing import Any


ALLOWED_OPERATIONS = {"multiply", "divide", "percentage", "ratio", "efficiency", "mass_balance", "flow_rate", "convert_pressure", "convert_temperature"}


def _validate_number(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a numeric value.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric value.") from exc
    if not isfinite(number):
        raise ValueError(f"{name} must be finite.")
    return number


def industrial_calculator(operation: str, value_a: float, value_b: float, input_unit: str | None = None, output_unit: str | None = None) -> dict[str, Any]:
    """Perform only whitelisted deterministic calculations; never evaluate expressions."""
    if not isinstance(operation, str):
        raise ValueError("operation must be a string.")
    operation = operation.strip().lower()
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(f"Unsupported calculation operation: {operation}")
    value_a = _validate_number(value_a, "value_a")
    value_b = _validate_number(value_b, "value_b")
    units: str | None = None
    if operation == "multiply":
        result = value_a * value_b
    elif operation == "divide":
        if value_b == 0:
            raise ValueError("Division by zero is not allowed.")
        result = value_a / value_b
    elif operation == "percentage":
        result = (value_a * value_b) / 100
    elif operation in {"ratio", "efficiency", "flow_rate"}:
        if value_b == 0:
            raise ValueError("Division by zero is not allowed.")
        result = value_a / value_b
        if operation == "efficiency":
            result *= 100
            units = "%"
    elif operation == "mass_balance":
        result = value_a - value_b
    elif operation == "convert_pressure":
        conversions = {("bar", "kpa"): 100.0, ("kpa", "bar"): 0.01, ("psi", "kpa"): 6.894757, ("kpa", "psi"): 1 / 6.894757}
        key = ((input_unit or "").lower(), (output_unit or "").lower())
        if key not in conversions:
            raise ValueError("Unsupported pressure conversion unit pair.")
        result, units = value_a * conversions[key], key[1]
    else:
        key = ((input_unit or "").lower(), (output_unit or "").lower())
        if key == ("c", "f"):
            result = value_a * 9 / 5 + 32
        elif key == ("f", "c"):
            result = (value_a - 32) * 5 / 9
        elif key == ("c", "k"):
            result = value_a + 273.15
        elif key == ("k", "c"):
            result = value_a - 273.15
        else:
            raise ValueError("Unsupported temperature conversion unit pair.")
        units = key[1]
    if not isfinite(result):
        raise ValueError("Calculation result must be finite.")
    return {"operation": operation, "value_a": value_a, "value_b": value_b, "result": result, "input_unit": input_unit, "output_unit": output_unit or units, "units": units, "disclaimer": "Deterministic arithmetic only; validate against approved engineering procedures."}
