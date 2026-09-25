import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")
text = "Decentralization"
tokens = encoding.encode(text)
print("Text:")
print(text)

print("\nToken IDs:")
print(tokens)

print("\nNumber of tokens:")
print(len(tokens))

print("\nIndividual tokens:")

for token in tokens:
    print(token, "->", repr(encoding.decode([token])))