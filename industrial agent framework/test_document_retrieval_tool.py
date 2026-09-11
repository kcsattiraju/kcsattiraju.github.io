from app.tools.document_retrieval_tool import search_documents


print("\n================================")
print("CHECKPOINT 28")
print("DOCUMENT RETRIEVAL TOOL TEST")
print("================================")


question = (
    "What should I check when "
    "P-101 has low discharge pressure?"
)


print(
    "\nQuestion:",
    question,
)


print(
    "\nCalling document retrieval tool..."
)


# LangChain tools are invoked using .invoke()

result = search_documents.invoke(
    {
        "query": question
    }
)


print("\n================================")
print("TOOL RESULT")
print("================================")

print(result)


print(
    "\nCheckpoint 28 tool test completed."
)