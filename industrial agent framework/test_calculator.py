from app.tools.calculator_tool import calculator


result = calculator.invoke(
    {
        "expression": "125 * 48"
    }
)

print(result)