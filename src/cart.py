THRESHOLD = 50_000
THRESHOLD_RATE = 0.9


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


def apply_threshold_discount(amount):
    if amount >= THRESHOLD:
        return round(amount * THRESHOLD_RATE)  # INV-2
    return amount  # INV-2


def final_total(items, is_vip=False):
    base = subtotal(items)
    amount = apply_threshold_discount(base)  # INV-2
    if is_vip and base >= THRESHOLD:
        return round(amount * 0.95)  # INV-3
    return amount  # INV-3, INV-5
