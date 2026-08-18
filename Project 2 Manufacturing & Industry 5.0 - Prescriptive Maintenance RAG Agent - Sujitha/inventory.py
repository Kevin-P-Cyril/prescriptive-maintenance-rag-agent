"""
inventory.py

Mock warehouse inventory tool for the
Prescriptive Maintenance RAG Agent.
"""

INVENTORY = {
    "bearing": 12,
    "cooling_fan": 5,
    "lubricant": 20,
    "motor": 3,
    "pump": 4,
    "filter": 10,
}


def check_inventory(part_id: str) -> dict:
    """
    Check the available quantity of a spare part.
    """

    part_id = part_id.lower().strip()

    quantity = INVENTORY.get(part_id, 0)

    return {
        "part_id": part_id,
        "available": quantity > 0,
        "quantity": quantity,
    }


if __name__ == "__main__":

    print("===== INVENTORY TOOL TEST =====")

    test_parts = [
        "bearing",
        "cooling_fan",
        "motor",
        "unknown_part",
    ]

    for part in test_parts:

        result = check_inventory(part)

        print(f"\nPart: {part}")
        print(f"Available: {result['available']}")
        print(f"Quantity: {result['quantity']}")