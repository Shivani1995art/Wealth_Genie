import json
from pathlib import Path


def load_sample(sample_dir: Path):
    metadata = json.loads((sample_dir / "metadata.json").read_text())
    expected = json.loads((sample_dir / "expected.json").read_text())

    return {
        "path": sample_dir,
        "metadata": metadata,
        "expected": expected,
    }


def main():
    evaluation_dir = Path(__file__).parent

    print("=" * 60)
    print("Universal Financial Extractor Evaluation")
    print("=" * 60)

    total = 0

    for document_type in sorted(evaluation_dir.iterdir()):

        if not document_type.is_dir():
            continue

        print(f"\n{document_type.name}")

        for sample in sorted(document_type.iterdir()):

            if not sample.is_dir():
                continue

            data = load_sample(sample)

            print(
                f"  ✓ {data['metadata']['id']}"
            )

            total += 1

    print("\n" + "=" * 60)
    print(f"Total Evaluation Samples : {total}")


if __name__ == "__main__":
    main()