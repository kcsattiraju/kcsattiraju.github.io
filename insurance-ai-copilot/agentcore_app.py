
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from insurance_agent import agent

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    # Read the user's question
    question = payload.get("prompt", "")

    if not isinstance(question, str) or not question.strip():
        return {"error": "Please provide a valid question."}

    # Call our existing LangGraph agent
    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    # Get the final AI response
    final_message = result["messages"][-1]

    content = final_message.content

    if isinstance(content, str):
        answer = content
    else:
        answer = str(content)

    return {
        "response": answer
    }


if __name__ == "__main__":
    app.run()
