from pathlib import Path
from datasets import load_dataset


def download_and_save_dataset():
    # Define the output directory and file path
    data_dir = Path("/home/divas/ml/CI-diagnosis-agent/data")
    output_path = data_dir / "ci_repair_bench.parquet"

    # Ensure target directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching dataset 'ci-benchmark-user/ci-repair-bench' from Hugging Face...")
    dataset = load_dataset("ci-benchmark-user/ci-repair-bench", split="train")

    print(f"Successfully downloaded!")
    print(f" - Rows: {len(dataset)}")
    print(f" - Columns ({len(dataset.column_names)}): {dataset.column_names}")

    print(f"Saving dataset to: {output_path}")
    dataset.to_parquet(output_path)

    # Verification Step: Ensure magic bytes b'PAR1' exist at start and end
    with open(output_path, "rb") as f:
        first_bytes = f.read(4)
        f.seek(-4, 2)
        last_bytes = f.read(4)

    if first_bytes == b"PAR1" and last_bytes == b"PAR1":
        print("\n✅ Verification passed: Valid Parquet file saved successfully!")
    else:
        print("\n❌ Warning: File created, but Parquet header/footer validation failed.")


if __name__ == "__main__":
    download_and_save_dataset()