
def round_TOL(value: float, tol: float) -> float:
    """Round a value to the nearest multiple of tol and rounds to 4 decimal places."""
    if tol <= 0:
        raise ValueError("Tolerance must be positive and non-zero.")
    return round(round(value / tol) * tol, 4)

