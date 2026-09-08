from app.models.llm_factory import create_llm


llm = create_llm()

response = llm.invoke(
    "Say hello in one short sentence."
)

print(response.content)