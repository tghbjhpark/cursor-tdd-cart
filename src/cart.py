def _validate_line_items(items):
    for i, (price, qty) in enumerate(items):
        if price < 0 or qty < 0:
            raise ValueError(f"invalid item at index {i}")  # E-2


def subtotal(items):
    if items is None:
        raise TypeError("items must not be None")  # E-1
    _validate_line_items(items)
    total = 0
    for price, qty in items:
        total += price * qty  # INV-1
    return total
