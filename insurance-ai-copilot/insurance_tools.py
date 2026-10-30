
from langchain_core.tools import tool


@tool
def calculate_insurance_premium(
    vehicle_value: float,
    premium_rate: float
) -> str:
    """Calculate an estimated annual insurance premium.

    Args:
        vehicle_value: Vehicle value in dollars.
        premium_rate: Annual premium percentage.
    """

    if vehicle_value <= 0 or not 0 <= premium_rate <= 100:
        return "Invalid vehicle value or premium rate."

    premium = vehicle_value * premium_rate / 100

    return f"Estimated annual premium: ${premium:,.2f}"


@tool
def lookup_insurance_policy(policy_type: str) -> str:
    """Look up general information about an insurance policy type."""

    policies = {
        "collision": "Covers collision-related vehicle damage.",
        "comprehensive": "Covers certain non-collision damage.",
        "liability": "Covers certain damage or injury to others."
    }

    return policies.get(
        policy_type.lower().strip(),
        "Policy type not found."
    )
