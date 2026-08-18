"""
tool_handler.py

Handles spare-part detection, inventory lookup,
and generation of the final prescriptive
maintenance recommendation.
"""

from typing import List, Dict, Any

from inventory import check_inventory


# Keywords used to identify spare parts from
# retrieved maintenance instructions.
PART_KEYWORDS = {
    "bearing": "bearing",
    "cooling fan": "cooling_fan",
    "fan": "cooling_fan",
    "motor": "motor",
    "pump": "pump",
    "filter": "filter",
    "lubricant": "lubricant",
}


def detect_spare_parts(retrieved_chunks: List[str]) -> List[str]:
    """
    Detect possible spare parts mentioned in
    retrieved maintenance instructions.
    """

    detected_parts = []

    for chunk in retrieved_chunks:

        # Retriever returns dictionary objects
        if isinstance(chunk, dict):
            text = str(chunk.get("instruction", "")).lower()
        else:
            text = str(chunk).lower()

        for keyword, part_id in PART_KEYWORDS.items():

            if keyword in text and part_id not in detected_parts:
                detected_parts.append(part_id)

    return detected_parts


def check_required_parts(parts: List[str]) -> List[Dict[str, Any]]:
    """
    Check inventory availability for all
    detected spare parts.
    """

    inventory_results = []

    for part in parts:

        result = check_inventory(part)

        inventory_results.append(result)

    return inventory_results


def generate_maintenance_recommendation(
    retrieved_chunks: List[str],
    inventory_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Combine repair instructions and inventory
    information into a prescriptive maintenance
    recommendation.
    """

    if not retrieved_chunks:
        return {
            "status": "no_repair_information",
            "recommendation": (
                "No grounded maintenance instruction was "
                "retrieved from the maintenance manual."
            ),
            "repair_instructions": [],
            "inventory": []
        }

    recommendations = []

    for item in inventory_results:

        if item["available"]:

            recommendations.append(
                f"Spare part '{item['part_id']}' is available "
                f"with {item['quantity']} unit(s) in stock."
            )

        else:

            recommendations.append(
                f"Spare part '{item['part_id']}' is currently "
                f"unavailable."
            )

    if recommendations:

        final_recommendation = (
            "Follow the retrieved maintenance procedure. "
            + " ".join(recommendations)
        )

    else:

        final_recommendation = (
            "Follow the retrieved maintenance procedure. "
            "No replacement spare part was identified."
        )

    return {
        "status": "recommendation_generated",
        "recommendation": final_recommendation,
        "repair_instructions": retrieved_chunks,
        "inventory": inventory_results
    }


def handle_tools(retrieved_chunks: List[str]) -> Dict[str, Any]:
    """
    Complete tool-calling workflow:

    Retrieved instructions
            ↓
    Detect spare parts
            ↓
    Check inventory
            ↓
    Generate recommendation
    """

    detected_parts = detect_spare_parts(retrieved_chunks)

    inventory_results = check_required_parts(
        detected_parts
    )

    return generate_maintenance_recommendation(
        retrieved_chunks,
        inventory_results
    )


if __name__ == "__main__":

    sample_chunks = [
        "Replace worn bearings to reduce vibration.",
        "Check lubrication levels regularly to avoid equipment failure."
    ]

    result = handle_tools(sample_chunks)

    print("\n===== TOOL HANDLER TEST =====")

    print("\nDetected / Checked Inventory:")

    for item in result["inventory"]:
        print(
            f"{item['part_id']} -> "
            f"Available: {item['available']}, "
            f"Quantity: {item['quantity']}"
        )

    print("\nFinal Recommendation:")
    print(result["recommendation"])

    print("\n===== TOOL HANDLER COMPLETE =====")