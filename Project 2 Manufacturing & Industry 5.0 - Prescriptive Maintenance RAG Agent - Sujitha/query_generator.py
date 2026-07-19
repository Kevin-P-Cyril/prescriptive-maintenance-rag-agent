"""
query_generator.py

Converts validated IoT sensor alerts into optimized
natural language queries for the RAG retrieval system.
"""

from typing import Dict


def generate_search_query(sensor_data: Dict) -> str:
    """
    Generate a natural language search query from
    incoming sensor telemetry.

    Parameters
    ----------
    sensor_data : dict
        Example:
        {
            "machine_id": "TURBINE-01",
            "error_code": "E-404",
            "temperature": 105,
            "vibration": 4.8
        }

    Returns
    -------
    str
        Optimized search query for the vector database.
    """

    machine_id = sensor_data.get("machine_id", "Unknown Machine")
    error_code = sensor_data.get("error_code", "Unknown Error")
    temperature = sensor_data.get("temperature", "Unknown")
    vibration = sensor_data.get("vibration", "Unknown")

    query = (
        f"{machine_id} "
        f"error code {error_code} "
        f"temperature {temperature}°C "
        f"vibration amplitude {vibration} mm/s "
        f"repair procedure troubleshooting guide"
    )

    return query


if __name__ == "__main__":
    sample_alert = {
        "machine_id": "TURBINE-01",
        "error_code": "E-404",
        "temperature": 105,
        "vibration": 4.8,
    }

    print(generate_search_query(sample_alert))