"""
Simple inventory system demonstrating safe I/O and input validation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Module-level inventory storage
stock_data: Dict[str, int] = {}


def add_item(item: str = "default", qty: int = 0,
             logs: List[str] | None = None) -> None:
    """
    Add a quantity to an item.

    Args:
        item: Name of the item.
        qty: Integer quantity to add. Must be >= 0.
        logs: Optional list to append log info.

    Raises:
        ValueError: Invalid item or qty.
    """
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a nonempty string")

    if not isinstance(qty, int):
        raise ValueError("qty must be an integer")

    if qty < 0:
        raise ValueError("qty must be nonnegative")

    if logs is None:
        logs = []

    stock_data[item] = stock_data.get(item, 0) + qty

    stamp = datetime.now().isoformat(timespec="seconds")
    logs.append(f"{stamp}: Added {qty} of {item}")
    logging.info("Added %s of %s", qty, item)


def remove_item(item: str, qty: int) -> None:
    """
    Remove a quantity from an item.

    Args:
        item: Item name.
        qty: Positive integer to remove.

    Raises:
        ValueError: Invalid input.
    """
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a nonempty string")

    if not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be a positive integer")

    if item not in stock_data:
        logging.warning("Tried removing missing item %s", item)
        return

    stock_data[item] -= qty
    if stock_data[item] <= 0:
        del stock_data[item]
        logging.info("Removed item %s completely", item)
    else:
        logging.info("New qty for %s: %s", item, stock_data[item])


def get_qty(item: str) -> int:
    """
    Get available quantity for an item.

    Args:
        item: Name of item.

    Returns:
        Quantity available.
    """
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a nonempty string")

    return stock_data.get(item, 0)


def load_data(file_path: str = "inventory.json") -> None:
    """
    Load inventory information from a JSON file.

    Args:
        file_path: Path to JSON file.

    Raises:
        OSError: Read errors.
        ValueError: Invalid data.
    """
    path = Path(file_path)

    if not path.exists():
        stock_data.clear()
        return

    with path.open("r", encoding="utf-8") as handle:
        data: Any = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("Invalid file format: not an object")

    if not all(isinstance(k, str) and isinstance(v, int)
               for k, v in data.items()):
        raise ValueError("File format must be str -> int mapping")

    stock_data.clear()
    stock_data.update(data)


def save_data(file_path: str = "inventory.json") -> None:
    """
    Save inventory to JSON.

    Args:
        file_path: Output file path.

    Raises:
        OSError: Write errors.
    """
    path = Path(file_path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(stock_data, handle, indent=2, sort_keys=True)


def print_data() -> None:
    """
    Print inventory report.
    """
    print("Items Report")
    for name in sorted(stock_data):
        print(f"{name} -> {stock_data[name]}")


def check_low_items(threshold: int = 5) -> List[str]:
    """
    List items that are below threshold.

    Args:
        threshold: Quantity cutoff.

    Returns:
        Item names lower than threshold.
    """
    if not isinstance(threshold, int) or threshold < 0:
        raise ValueError("threshold must be nonnegative")

    return [name for name, qty in stock_data.items()
            if qty < threshold]


def main() -> None:
    """
    Example usage.
    """
    add_item("apple", 10)
    add_item("banana", 2)

    remove_item("apple", 3)
    remove_item("orange", 1)

    print(f"Apple stock: {get_qty('apple')}")
    print(f"Low items: {check_low_items()}")

    save_data()
    load_data()
    print_data()


if __name__ == "__main__":
    main()
