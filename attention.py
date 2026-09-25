import numpy as np

scores = np.array([
    [1.0, 2.0, 0.5],
    [2.0, 1.0, 0.5],
    [0.5, 0.5, 2.0]
])

def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum()

attention_weights = np.array([
    softmax(row) for row in scores
])

print("Attention Scores:")
print(scores)

print("\nAttention Weights:")
print(attention_weights)