"""Augment the training data."""
from pathlib import Path
from random import choice
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
from PIL import Image
from tqdm import tqdm

from src.agoro_field_boundary_detector.data import (
    NOISE,
    TRANSLATION,
    load_annotations,
    polygons_to_mask,
    transform,
)


def generate(
    field: np.ndarray,
    mask: np.ndarray,
    write_path: Path,
    n_comb: int = 100,
    prefix: str = "",
) -> None:
    """TODO."""
    # Generate n_comb unique transformations
    transformations: Dict[str, List[Any]] = {}
    while len(transformations) < n_comb:
        new = _get_transformation()
        tag = f"{new[0].__name__}{new[1]}{new[2].__name__}{new[3]}"  # type: ignore
        if tag not in transformations:
            transformations[tag] = new

    # Create the transformations
    for idx, transformation in enumerate(
        tqdm(transformations.values(), desc=f"Generating {prefix}")
    ):
        field_t, mask_t = transform(
            field=field,
            mask=mask,
            translation=transformation[0],
            t_idx=transformation[1],
            noise=transformation[2],
            n_idx=transformation[3],
        )
        with open(write_path / f"fields/{prefix}{idx}.npy", "wb") as f:
            np.save(f, field_t)
        with open(write_path / f"masks/{prefix}{idx}.npy", "wb") as f:
            np.save(f, mask_t)


def _get_transformation() -> List[Tuple[Callable[..., Any], int, Callable[..., Any], int]]:
    """Get a random transformation."""
    transformation = []
    f, (a, b) = choice(TRANSLATION)  # noqa S311
    transformation += [f, choice(range(a, b + 1))]  # noqa S311
    f, (a, b) = choice(NOISE)  # noqa S311
    transformation += [f, choice(range(a, b + 1))]  # noqa S311
    return transformation


def main(
    fields: List[np.ndarray],
    masks: List[np.ndarray],
    prefixes: List[str],
    write_folder: Path,
    n_comb: int = 100,
) -> None:
    """Generate and save data augmentations for all the fields and corresponding masks."""
    for field, mask, prefix in zip(fields, masks, prefixes):
        generate(
            field=field,
            mask=mask,
            prefix=prefix,
            n_comb=n_comb,
            write_path=write_folder,
        )


if __name__ == "__main__":
    # Load in the annotations
    DATA_PATH = Path(__file__).parent / "../../data"
    annotations = load_annotations(DATA_PATH / "annotations.json")
    names = [k[:-4] for k in annotations.keys()]  # Cut of the '.png'

    # Load in fields and corresponding masks
    annotated_fields, annotated_masks = [], []
    for name in names:
        boundaries = annotations[f"{name}.png"]
        annotated_fields.append(np.asarray(Image.open(DATA_PATH / f"raw/{name}.png")))
        annotated_masks.append(polygons_to_mask(boundaries))

    # Ensure folders exist
    (DATA_PATH / "augmented/fields").mkdir(exist_ok=True, parents=True)
    (DATA_PATH / "augmented/masks").mkdir(exist_ok=True, parents=True)

    # Export the given coordinates
    main(
        fields=annotated_fields,
        masks=annotated_masks,
        prefixes=names,
        write_folder=DATA_PATH / "augmented",
    )