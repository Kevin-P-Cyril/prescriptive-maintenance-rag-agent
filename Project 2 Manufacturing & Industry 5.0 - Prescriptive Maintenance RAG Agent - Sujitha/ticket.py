import json
from datetime import datetime


def generate_ticket(sensor_data, repair_summary, spare_parts=None):

    spare_parts = spare_parts or []

    ticket_id = "TICKET-" + datetime.now().strftime("%Y%m%d%H%M%S")

    ticket = {
        "ticket_id": ticket_id,
        "created_at": datetime.now().isoformat(),
        "asset": sensor_data,
        "repair_summary": repair_summary,
        "required_spare_parts": spare_parts,
        "status": "Open"
    }

    filename = f"{ticket_id}.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(ticket, file, indent=4)

    return ticket


if __name__ == "__main__":

    sensor_data = {
        "machine_id": "TURBINE-01",
        "error_code": "E-404",
        "temperature": 105,
        "vibration": 4.8
    }

    repair_summary = "Replace worn bearings to reduce vibration."

    spare_parts = [
        {
            "part_id": "bearing",
            "available": True,
            "quantity": 12
        }
    ]

    generate_ticket(
        sensor_data,
        repair_summary,
        spare_parts
    )