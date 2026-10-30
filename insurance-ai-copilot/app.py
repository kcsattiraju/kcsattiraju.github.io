
import boto3

# Create a client to communicate with Bedrock Runtime.
client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "amazon.nova-lite-v1:0"


def ask_insurance_question(question):
    # Send a conversation request to the model.
    response = client.converse(
        modelId=MODEL_ID,
        system=[
            {
                "text": (
                    "You are an insurance education assistant. "
                    "Explain insurance terms in simple language. "
                    "Never invent policy-specific coverage details."
                )
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [{"text": question}]
            }
        ],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.2
        }
    )

    # Extract the generated text from the response.
    answer = response["output"]["message"]["content"][0]["text"]

    return answer


question = "What is collision insurance coverage?"

answer = ask_insurance_question(question)

print("\nInsurance AI Copilot:")
print(answer)
