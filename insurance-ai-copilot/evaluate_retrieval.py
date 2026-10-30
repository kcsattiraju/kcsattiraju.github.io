
import json
import time
from statistics import mean

from rag_tools import retrieve_documents, FINAL_TOP_K


def evaluate_method(method, dataset, k=FINAL_TOP_K):
    recalls = []
    precisions = []
    latencies = []

    for test in dataset:
        question = test["question"]
        relevant_ids = set(test["relevant_chunk_ids"])

        start = time.perf_counter()

        passages = retrieve_documents(
            query=question,
            source=test.get("source", ""),
            method=method,
            k=k
        )

        latency = time.perf_counter() - start

        retrieved_ids = [p["id"] for p in passages]

        hits = len(set(retrieved_ids) & relevant_ids)

        recall = hits / len(relevant_ids)
        precision = hits / k

        recalls.append(recall)
        precisions.append(precision)
        latencies.append(latency)

        print(f"\nQuestion: {question}")
        print(f"Retrieved IDs: {retrieved_ids}")
        print(f"Recall@{k}: {recall:.3f}")
        print(f"Precision@{k}: {precision:.3f}")
        print(f"Latency: {latency:.3f}s")

    return {
        "method": method,
        "recall": mean(recalls),
        "precision": mean(precisions),
        "latency": mean(latencies)
    }


def main():
    with open("evaluation_dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    if not dataset:
        raise ValueError("Evaluation dataset is empty")

    for test in dataset:
        relevant_ids = test.get("relevant_chunk_ids", [])

        if not relevant_ids or any(
            not isinstance(chunk_id, str)
            or chunk_id.startswith(("REPLACE_", "actual_chunk_id"))
            for chunk_id in relevant_ids
        ):
            raise ValueError(
                f"Use actual Chroma chunk IDs for: {test['question']}"
            )

    print(f"Loaded {len(dataset)} evaluation questions.")

    results = []

    for method in ["semantic", "bm25", "hybrid"]:
        print(f"\n========== {method.upper()} ==========")

        result = evaluate_method(method, dataset)
        results.append(result)

    print("\n========== FINAL COMPARISON ==========")

    for result in results:
        print(
            f"{result['method']:10} | "
            f"Recall@{FINAL_TOP_K}: {result['recall']:.3f} | "
            f"Precision@{FINAL_TOP_K}: {result['precision']:.3f} | "
            f"Latency: {result['latency']:.3f}s"
        )


if __name__ == "__main__":
    main()
