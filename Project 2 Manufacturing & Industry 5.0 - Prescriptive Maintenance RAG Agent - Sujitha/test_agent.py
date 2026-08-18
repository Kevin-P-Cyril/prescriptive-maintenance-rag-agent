from agent import run_agent


def test_maintenance_alert(alert, test_name):
    print(f"\n{'=' * 60}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 60}")

    print("\nSensor Alert:")
    print(alert)

    result = run_agent(alert)

    print("\nGenerated Query:")
    print(result.get("search_query"))

    print("\nRetrieved Maintenance Instructions:")

    for i, chunk in enumerate(
        result.get("retrieved_chunks", []),
        start=1
    ):
        print(f"\n--- Result {i} ---")
        print(f"Instruction: {chunk.get('instruction')}")
        print(f"Document: {chunk.get('document_title')}")
        print(f"Section: {chunk.get('section')}")
        print(f"Page: {chunk.get('page')}")

    print("\nTool Required:")
    print(result.get("tool_required", False))

    if result.get("tool_result"):

        print("\nInventory Results:")

        for item in result["tool_result"].get("inventory", []):
            print(
                f"{item['part_id']} -> "
                f"Available: {item['available']}, "
                f"Quantity: {item['quantity']}"
            )

        print("\nFinal Recommendation:")
        print(
            result["tool_result"].get(
                "recommendation",
                ""
            )
        )

    print("\nTEST COMPLETED")


if __name__ == "__main__":

    alerts = [
        (
            {
                "machine_id": "TURBINE-01",
                "error_code": "E-404",
                "temperature": 105,
                "vibration": 4.8
            },
            "High Temperature + High Vibration"
        ),

        (
            {
                "machine_id": "PUMP-02",
                "error_code": "E-201",
                "temperature": 82,
                "vibration": 2.1
            },
            "Pump Maintenance Alert"
        ),

        (
            {
                "machine_id": "MOTOR-03",
                "error_code": "E-105",
                "temperature": 110,
                "vibration": 5.2
            },
            "Motor Overheating Alert"
        )
    ]

    print("\n===== AGENT INTEGRATION TESTING =====")

    for alert, test_name in alerts:
        test_maintenance_alert(alert, test_name)

    print("\n===== ALL INTEGRATION TESTS COMPLETED =====")