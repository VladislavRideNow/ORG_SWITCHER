from pathlib import Path

from app.workers.customer_events_transformer import transform_events


if __name__ == "__main__":
    input_path = Path("output/customer_events_20260128_202420.json")
    output_path = Path("output/customer_events_20260128_202420_transformed.json")
    orgs_path = Path("ORGS.json")
    transform_events(input_path=input_path, output_path=output_path, orgs_path=orgs_path)

