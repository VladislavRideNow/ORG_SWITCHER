import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


OLD_NEW_PATTERN = re.compile(r"Old value:\s*(.*?)\s*,\s*New value:\s*(.*)")


def _split_values(values_text: str) -> List[str]:
    return [value.strip() for value in values_text.split(",") if value.strip()]


def _extract_old_new(description: str) -> Tuple[List[str], List[str]]:
    match = OLD_NEW_PATTERN.search(description or "")
    if not match:
        return [], []
    old_values = _split_values(match.group(1))
    new_values = _split_values(match.group(2))
    return old_values, new_values


def _load_orgs_map(orgs_path: Path) -> Dict[str, str]:
    with orgs_path.open("r", encoding="utf-8") as file:
        items = json.load(file) or []
    return {item.get("displayname"): item.get("id") for item in items if item}


def transform_events(input_path: Path, output_path: Path, orgs_path: Path) -> Path:
    orgs_map = _load_orgs_map(orgs_path)
    not_merged = 0

    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    transformed: List[Dict] = []
    for item in data:
        customerdataid = item.get("customerdataid")
        events = item.get("events") or []
        old_values: List[str] = []
        new_values: List[str] = []
        for event in events:
            description = event.get("Description") or ""
            old_list, new_list = _extract_old_new(description)
            old_values.extend(old_list)
            new_values.extend(new_list)
        assign_ids: List[str] = []
        for value in old_values:
            org_id = orgs_map.get(value)
            if org_id:
                assign_ids.append(org_id)
            else:
                not_merged += 1
        transformed.append(
            {
                "customerdataid": customerdataid,
                "old_values": old_values,
                "new_values": new_values,
                "assign_ids": assign_ids,
            }
        )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(transformed, file, ensure_ascii=False, indent=2)
    print(f"[INFO] not merged count: {not_merged}")
    return output_path

