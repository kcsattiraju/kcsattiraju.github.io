from transformers import AutoTokenizer, AutoModel

model_name = "distilbert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

text = "The pump motor is overheating"

inputs = tokenizer(text, return_tensors="pt")

print("Input IDs:")
print(inputs["input_ids"])

outputs = model(**inputs)

print("\nOutput shape:")
print(outputs.last_hidden_state.shape)