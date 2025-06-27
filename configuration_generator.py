import json
from pathlib import Path
from itertools import product
from typing import Dict, Iterator, List, Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data" / "Input"

with (DATA_DIR / "gender_ethnicity.json").open(encoding="utf-8") as f:
    people = json.load(f)
with (DATA_DIR / "universites.json").open(encoding="utf-8") as f:
    unis = json.load(f)

# Build single config dict
def _build_config(person: Dict[str, Any], uni: Dict[str, Any], model_id: int, repetition: int) -> Dict[str, Any]:
    return {
        "model_id": model_id,
        "gender": person["gender"],
        "ethnicity": person["ethnicity"],
        "name": person["name"],
        "specific_eth": person["specific_eth"],
        "education": uni["education"],
        "uni_version": uni["uni_version"],
        "repetition": repetition,
    }

# All 216 person/uni combinations × repetitions
def full_configs(model_id: int, repetitions: int = 1) -> Iterator[Dict[str, Any]]:
    for rep in range(repetitions):
        for person, uni in product(people, unis):
            yield _build_config(person, uni, model_id, rep)

# 36 persons on first university
def persons_first_uni(model_id: int, repetitions: int = 1) -> Iterator[Dict[str, Any]]:
    first_uni = unis[0]
    for rep in range(repetitions):
        for person in people:
            yield _build_config(person, first_uni, model_id, rep)

# 6 universities on first person
def unis_first_person(model_id: int, repetitions: int = 1) -> Iterator[Dict[str, Any]]:
    first_person = people[0]
    for rep in range(repetitions):
        for uni in unis:
            yield _build_config(first_person, uni, model_id, rep)

# First person and first university
def single(model_id: int, repetitions: int = 1) -> Iterator[Dict[str, Any]]:
    first_person = people[0]
    first_uni = unis[0]
    for rep in range(repetitions):
        yield _build_config(first_person, first_uni, model_id, rep)


# Return iterator chosen by variant string
def get_configs(variant: str, model_id: int, repetitions: int = 1) -> Iterator[Dict[str, Any]]:
    if variant == "full":
        return full_configs(model_id, repetitions)
    if variant == "persons":
        return persons_first_uni(model_id, repetitions)
    if variant == "unis":
        return unis_first_person(model_id, repetitions)
    if variant == "single":
        return single(model_id, repetitions)
    raise ValueError(f"Unknown variant: {variant}")