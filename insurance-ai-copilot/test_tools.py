
from insurance_tools import (
    calculate_insurance_premium,
    lookup_insurance_policy
)

# Test premium calculator
result = calculate_insurance_premium.invoke({
    "vehicle_value": 30000,
    "premium_rate": 4
})

print("Premium:", result)

# Test policy lookup
policy = lookup_insurance_policy.invoke({
    "policy_type": "collision"
})

print("Policy:", policy)
