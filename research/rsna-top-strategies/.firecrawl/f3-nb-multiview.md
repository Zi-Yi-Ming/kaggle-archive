menu

[Skip to\\
\\
content](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble#site-content)

[![](https://www.kaggle.com/static/images/site-logo.svg)](https://www.kaggle.com/)

Create

search​

- [explore\\
\\
Home](https://www.kaggle.com/)

- [emoji\_events\\
\\
Competitions](https://www.kaggle.com/competitions)

- [leaderboard\\
\\
Benchmarks](https://www.kaggle.com/benchmarks)

- [smart\_toy\\
\\
Game Arena](https://www.kaggle.com/game-arena)


- [code\\
\\
Data Hub](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble#)

expand\_more


- [format\_list\_bulleted\\
\\
More](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble#)

expand\_more


menu

[Skip to\\
\\
content](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble#site-content)

[![](https://www.kaggle.com/static/images/site-logo.svg)](https://www.kaggle.com/)

search​

[Sign In](https://www.kaggle.com/account/login?phase=startSignInTab&returnUrl=%2Fcode%2Fjocelyndumlao%2Frsna-knee-abnormality-multi-view-ensemble) [Register](https://www.kaggle.com/account/login?phase=startRegisterTab&returnUrl=%2Fcode%2Fjocelyndumlao%2Frsna-knee-abnormality-multi-view-ensemble)

[Jocelyn Dumlao's profile](https://www.kaggle.com/jocelyndumlao) Jocelyn Dumlao  · 15d ago · 222 views

arrow\_drop\_up14

Copy & Edit
6

file\_downloadDownload

![bronze medal](https://www.kaggle.com/static/images/medals/competitions/bronzel@2x.png)

more\_vert

# RSNA Knee Abnormality — Multi-View Ensemble 🦴🧠

## RSNA Knee Abnormality — Multi-View Ensemble 🦴🧠

[Notebook](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble/notebook) [Input](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble/input) [Output](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble/output) [Logs](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble/log) [Comments (0)](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble/comments)

historyVersion 2 of 2chevron\_right

## Runtime

play\_arrow

10m 15s · GPU T4 x2

## Input

COMPETITIONS

![](https://www.kaggle.com/competitions/154281/images/thumbnail)

RSNA Knee Abnormality Detection

## Tags

[GPU](https://www.kaggle.com/code?tagIds=16580-GPU)

## Language

Python

## Table of Contents

[Setup](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble#-Setup) [Final Image Visualization](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble#-Final-Image-Visualization)

![Profile picture for undefined](https://storage.googleapis.com/kaggle-competitions/kaggle/154281/logos/thumb76_76.png?GoogleAccessId=web-data@kaggle-161607.iam.gserviceaccount.com&Expires=1790751927&Signature=WkujBz5GGOVEoi2vFNHJ6YFU%2Bw2PIwnXn4bxi%2F0c%2BNGdMGsDH9XyqCptPm6AEHs18MkNTx0NlEKwB4K086jNKkuI%2FwOLA9SBHnzVUvS9YBP9brPsE246s%2BPks2EirE86QBQr0w%2FRm%2BhUCyBUEon8F4DJPWmgBLw3YuFWtPNnGXXsi1fkAiqT7Q%2BZnsgzXfPNQ7NwA7oZeKTbnYWN5dbSYd%2FGBGQpAovR3W4jeVaDpucliIx74g25P5Bnnt%2F%2FrYVKilMXte85wn3F4XoyOjkyncPQR3mCDfKbkxyxDVlBIQPA%2BurwUK5VhL531C66HXEP2XC5LOTKcfuo%2BDT38rjOAg%3D%3D&t=2026-07-14-02-42-13)

Competition Notebook

[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)

Public Score

0.494

Best Score

[0.494 V2](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble?scriptVersionId=349728193)

\_\_notebook\_\_

linkcode

Published on September 08, 2026

#### Author: Jocelyn C. Dumlao

[LinkedIn](https://www.linkedin.com/in/jocelyn-dumlao-168921a8/) [GitHub](https://github.com/jcdumlao14) [YouTube](https://www.youtube.com/@CogniCraftedMinds) [Kaggle](https://www.kaggle.com/jocelyndumlao)

linkcode

# Setup     [¶](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble\#-Setup)

In \[1\]:

linkcode

```
# ============================================================
# 0. STRICT OFFLINE MODE
# MUST RUN BEFORE importing timm / huggingface_hub
# ============================================================

import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

print("=" * 70)
print("OFFLINE MODE ENABLED")
print("=" * 70)
print("HF_HUB_OFFLINE       =", os.environ["HF_HUB_OFFLINE"])
print("HF_DATASETS_OFFLINE  =", os.environ["HF_DATASETS_OFFLINE"])
print("TRANSFORMERS_OFFLINE =", os.environ["TRANSFORMERS_OFFLINE"])
print("=" * 70)
```

```
======================================================================
OFFLINE MODE ENABLED
======================================================================
HF_HUB_OFFLINE       = 1
HF_DATASETS_OFFLINE  = 1
TRANSFORMERS_OFFLINE = 1
======================================================================
```

unfold\_moreShow hidden code

In \[2\]:

linkcode

```
# ============================================================
# 1. OFFLINE ENVIRONMENT — MUST COME FIRST
# ============================================================

import os

# ------------------------------------------------------------
# Hugging Face / Transformers offline mode
# MUST be configured before importing timm.
# ------------------------------------------------------------

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# Disable Hugging Face Xet/network-related behavior.
os.environ["HF_HUB_DISABLE_XET"] = "1"

# Avoid token/network lookup.
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

# Force local cache locations where possible.
os.environ.setdefault(
    "HF_HOME",
    "/kaggle/working/huggingface"
)

os.environ.setdefault(
    "TRANSFORMERS_CACHE",
    "/kaggle/working/huggingface"
)

os.environ.setdefault(
    "HF_DATASETS_OFFLINE",
    "1"
)

print("=" * 70)
print("STRICT OFFLINE MODE")
print("=" * 70)

print(
    "HF_HUB_OFFLINE:",
    os.environ.get("HF_HUB_OFFLINE")
)

print(
    "TRANSFORMERS_OFFLINE:",
    os.environ.get("TRANSFORMERS_OFFLINE")
)

print(
    "HF_HUB_DISABLE_XET:",
    os.environ.get("HF_HUB_DISABLE_XET")
)

print()

# ============================================================
# 2. IMPORTS
# ============================================================

import gc
import math
import pickle
import time
import warnings

from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pydicom
import torch
import torch.nn as nn
import torch.nn.functional as F

# ------------------------------------------------------------
# timm is imported ONLY AFTER offline environment variables
# have been configured.
# ------------------------------------------------------------

import timm

from pydicom.pixel_data_handlers.util import (
    apply_modality_lut,
)

warnings.filterwarnings("ignore")

# ============================================================
# 3. ENVIRONMENT
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

if DEVICE.type == "cuda":

    torch.backends.cudnn.benchmark = True

    try:

        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    except Exception:

        pass

print("=" * 70)
print("RSNA KNEE ABNORMALITY — OFFLINE V6")
print("=" * 70)

print(
    f"Device: {DEVICE}"
)

if DEVICE.type == "cuda":

    print(
        f"GPU: "
        f"{torch.cuda.get_device_name(0)}"
    )

print()

# ============================================================
# 4. CONFIGURATION
# ============================================================

IMAGE_SIZE = 384

CROP_MM = 140.0

TOTAL_SLICES = 64

DEFAULT_ARCH = (
    "coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k"
)

DEFAULT_RESOLUTION = 384

OUTPUT_FILE = (
    "/kaggle/working/submission.csv"
)

CACHE_FILE = (
    "/kaggle/working/"
    "rsna_knee_study_lookup_cache_v6.pkl"
)

CACHE_VERSION = (
    "rsna_knee_lookup_v6_strict_offline"
)

PROGRESS_EVERY_STUDIES = 25

PROGRESS_EVERY_FILES = 1000

# ------------------------------------------------------------
# Optional local checkpoint.
#
# If you later attach a trained RSNA checkpoint as a Kaggle
# Dataset, put its path here.
#
# Example:
#
# MODEL_CHECKPOINT = (
#     "/kaggle/input/my-rsna-model/"
#     "best_model.pth"
# )
#
# Leave as None for checkpoint-free mode.
# ------------------------------------------------------------

MODEL_CHECKPOINT = None

# ============================================================
# 5. LABELS
# ============================================================

LABELS = [\
\
    "ACL",\
\
    "MCL",\
\
    "Medial Meniscus",\
\
    "Lateral Meniscus",\
\
    "Medial OA",\
\
    "Lateral OA",\
\
    "PF OA",\
\
    "Effusion",\
\
    "Synovitis",\
\
    "Baker's",\
\
    "Contusion",\
\
    "Fracture",\
]

NUM_CLASSES = len(
    LABELS
)

# ============================================================
# 6. IMAGENET NORMALIZATION
# ============================================================

IMAGENET_MEAN = np.array(
    [\
        0.485,\
        0.456,\
        0.406,\
    ],
    dtype=np.float32,
)

IMAGENET_STD = np.array(
    [\
        0.229,\
        0.224,\
        0.225,\
    ],
    dtype=np.float32,
)

# ============================================================
# 7. ANATOMICAL SERIES SLOTS
# ============================================================

SERIES_SLOTS = [\
\
    (\
        "Sagittal",\
        1,\
        18,\
    ),\
\
    (\
        "Sagittal",\
        0,\
        14,\
    ),\
\
    (\
        "Coronal",\
        1,\
        12,\
    ),\
\
    (\
        "Coronal",\
        0,\
        8,\
    ),\
\
    (\
        "Axial",\
        -1,\
        12,\
    ),\
]

# ============================================================
# 8. TTA CONFIGURATIONS
# ============================================================

TTA_CONFIGS = [\
\
    {\
        "name": "wide_02_98",\
        "lo": 0.02,\
        "hi": 0.98,\
        "k": 64,\
        "weight": 0.28,\
    },\
\
    {\
        "name": "wide_04_96",\
        "lo": 0.04,\
        "hi": 0.96,\
        "k": 64,\
        "weight": 0.24,\
    },\
\
    {\
        "name": "balanced_06_94",\
        "lo": 0.06,\
        "hi": 0.94,\
        "k": 60,\
        "weight": 0.20,\
    },\
\
    {\
        "name": "central_10_90",\
        "lo": 0.10,\
        "hi": 0.90,\
        "k": 56,\
        "weight": 0.16,\
    },\
\
    {\
        "name": "focused_15_85",\
        "lo": 0.15,\
        "hi": 0.85,\
        "k": 48,\
        "weight": 0.12,\
    },\
]

# ============================================================
# 9. TARGET RANK WEIGHTS
# ============================================================

TARGET_RANK_WEIGHTS = {

    "ACL": 0.70,

    "MCL": 0.55,

    "Medial Meniscus": 0.65,

    "Lateral Meniscus": 0.72,

    "Medial OA": 0.60,

    "Lateral OA": 0.68,

    "PF OA": 0.58,

    "Effusion": 0.52,

    "Synovitis": 0.58,

    "Baker's": 0.55,

    "Contusion": 0.60,

    "Fracture": 0.70,
}

# ============================================================
# 10. LOCATE COMPETITION ROOT
# ============================================================

def locate_competition_root():

    candidates = [\
\
        Path(\
            "/kaggle/input/competitions/"\
            "rsna-knee-abnormality-detection"\
        ),\
\
        Path(\
            "/kaggle/input/"\
            "rsna-knee-abnormality-detection"\
        ),\
\
        Path("data"),\
\
        Path("."),\
    ]

    for root in candidates:

        if not root.exists():

            continue

        if (

            (root / "test.csv").is_file()

            and

            (
                root /
                "test_series.csv"
            ).is_file()

            and

            (
                root /
                "test_series"
            ).is_dir()

        ):

            print(
                "Using competition root:"
            )

            print(
                f"  {root}"
            )

            return root

    # --------------------------------------------------------
    # Fallback search.
    # --------------------------------------------------------

    input_root = Path(
        "/kaggle/input"
    )

    if input_root.exists():

        print(
            "Searching /kaggle/input "
            "for test.csv + test_series..."
        )

        for csv_path in input_root.glob(
            "**/test.csv"
        ):

            root = (
                csv_path.parent
            )

            if (

                (
                    root /
                    "test_series"
                ).is_dir()

                and

                (
                    root /
                    "test_series.csv"
                ).is_file()

            ):

                print(
                    "Discovered competition root:"
                )

                print(
                    f"  {root}"
                )

                return root

    raise FileNotFoundError(

        "\nCould not locate the RSNA competition root.\n"

        "\nExpected:\n"

        "  test.csv\n"

        "  test_series.csv\n"

        "  test_series/\n"
    )

# ============================================================
# 11. LOCATE TEST SERIES
# ============================================================

def locate_test_series(root):

    candidates = [\
\
        root / "test_series",\
\
        root / "test_images",\
\
        root / "test",\
\
        root / "images" / "test",\
    ]

    official = (
        root /
        "test_series"
    )

    if official.is_dir():

        print(
            "Using official test DICOM directory:"
        )

        print(
            f"  {official}"
        )

        return official

    for path in candidates:

        if path.is_dir():

            print(
                "Using discovered test DICOM directory:"
            )

            print(
                f"  {path}"
            )

            return path

    raise FileNotFoundError(

        "\nCould not locate test DICOM directory.\n"

        "\nExpected:\n"

        f"  {root / 'test_series'}\n"
    )

# ============================================================
# 12. LOAD TEST CSV
# ============================================================

def load_test_csv(root):

    test_csv = (
        root /
        "test.csv"
    )

    if not test_csv.is_file():

        matches = list(
            root.glob(
                "**/test.csv"
            )
        )

        if not matches:

            raise FileNotFoundError(
                "test.csv not found."
            )

        test_csv = matches[0]

    df = pd.read_csv(
        test_csv
    )

    if df.empty:

        raise ValueError(
            "test.csv is empty."
        )

    if (
        "StudyInstanceUID"
        not in df.columns
    ):

        raise ValueError(
            "test.csv does not contain "
            "'StudyInstanceUID'."
        )

    print(
        "Test CSV:"
    )

    print(
        f"  {test_csv}"
    )

    print(
        f"Test studies: "
        f"{len(df):,}"
    )

    return (
        df,
        "StudyInstanceUID",
        test_csv,
    )

# ============================================================
# 13. LOAD TEST SERIES CSV
# ============================================================

def load_test_series_csv(root):

    test_series_csv = (
        root /
        "test_series.csv"
    )

    if not test_series_csv.is_file():

        matches = list(
            root.glob(
                "**/test_series.csv"
            )
        )

        if not matches:

            raise FileNotFoundError(
                "test_series.csv not found."
            )

        test_series_csv = matches[0]

    df = pd.read_csv(
        test_series_csv
    )

    required = [\
\
        "StudyInstanceUID",\
\
        "SeriesInstanceUID",\
\
        "Fluid_Sensitive",\
\
        "Anatomical_Plane",\
    ]

    missing = [\
\
        col\
\
        for col in required\
\
        if col not in df.columns\
    ]

    if missing:

        raise ValueError(

            "test_series.csv is missing "

            f"columns: {missing}"
        )

    print(
        "Test series CSV:"
    )

    print(
        f"  {test_series_csv}"
    )

    print(
        f"Test series: "
        f"{len(df):,}"
    )

    print()

    print(
        "Series metadata columns:"
    )

    print(
        f"  {list(df.columns)}"
    )

    return (
        df,
        test_series_csv,
    )

# ============================================================
# 14. DICOM HEADER TAGS
# ============================================================

DICOM_TAGS = [\
\
    "StudyInstanceUID",\
\
    "SeriesInstanceUID",\
\
    "SOPInstanceUID",\
\
    "SeriesDescription",\
\
    "ProtocolName",\
\
    "SequenceName",\
\
    "ImageOrientationPatient",\
\
    "ImagePositionPatient",\
\
    "PixelSpacing",\
\
    "InstanceNumber",\
\
    "SliceThickness",\
\
    "SpacingBetweenSlices",\
\
    "PatientPosition",\
\
    "Modality",\
\
    "BodyPartExamined",\
]

# ============================================================
# 15. SAFE HELPERS
# ============================================================

def safe_float_array(value):

    if value is None:

        return None

    try:

        return np.asarray(

            [\
                float(x)\
                for x in value\
            ],

            dtype=np.float32,
        )

    except Exception:

        return None

def safe_float(
    value,
    default=None,
):

    try:

        return float(value)

    except Exception:

        return default

def safe_int(
    value,
    default=None,
):

    try:

        return int(value)

    except Exception:

        return default

def get_string(
    ds,
    name,
):

    try:

        value = getattr(
            ds,
            name,
            None,
        )

        if value is None:

            return ""

        return str(value)

    except Exception:

        return ""

# ============================================================
# 16. ESTIMATE PLANE
# ============================================================

def estimate_plane(ds):

    try:

        iop = safe_float_array(

            getattr(

                ds,

                "ImageOrientationPatient",

                None,
            )
        )

        if (

            iop is None

            or

            len(iop) != 6

        ):

            return ""

        row = iop[:3]

        col = iop[3:]

        normal = np.cross(
            row,
            col,
        )

        axis = int(
            np.argmax(
                np.abs(normal)
            )
        )

        if axis == 0:

            return "Sagittal"

        if axis == 1:

            return "Coronal"

        if axis == 2:

            return "Axial"

    except Exception:

        pass

    return ""

# ============================================================
# 17. READ LIGHT DICOM METADATA
# ============================================================

def read_dicom_metadata(path):

    try:

        ds = pydicom.dcmread(

            str(path),

            stop_before_pixels=True,

            specific_tags=DICOM_TAGS,

            force=True,
        )

        iop = safe_float_array(

            getattr(

                ds,

                "ImageOrientationPatient",

                None,
            )
        )

        ipp = safe_float_array(

            getattr(

                ds,

                "ImagePositionPatient",

                None,
            )
        )

        spacing = safe_float_array(

            getattr(

                ds,

                "PixelSpacing",

                None,
            )
        )

        if (

            spacing is None

            or

            len(spacing) < 2

        ):

            spacing = np.array(

                [\
                    0.5,\
                    0.5,\
                ],

                dtype=np.float32,
            )

        return {

            "path":
                str(path),

            "study_uid":
                get_string(
                    ds,
                    "StudyInstanceUID",
                ),

            "series_uid":
                get_string(
                    ds,
                    "SeriesInstanceUID",
                ),

            "sop_uid":
                get_string(
                    ds,
                    "SOPInstanceUID",
                ),

            "series_description":
                get_string(
                    ds,
                    "SeriesDescription",
                ),

            "protocol_name":
                get_string(
                    ds,
                    "ProtocolName",
                ),

            "sequence_name":
                get_string(
                    ds,
                    "SequenceName",
                ),

            "plane":
                estimate_plane(ds),

            "image_orientation":
                (
                    iop.tolist()
                    if iop is not None
                    else None
                ),

            "image_position":
                (
                    ipp.tolist()
                    if ipp is not None
                    else None
                ),

            "pixel_spacing":
                spacing[:2].tolist(),

            "instance_number":
                safe_int(
                    getattr(
                        ds,
                        "InstanceNumber",
                        None,
                    )
                ),

            "slice_thickness":
                safe_float(
                    getattr(
                        ds,
                        "SliceThickness",
                        None,
                    )
                ),

            "spacing_between_slices":
                safe_float(
                    getattr(
                        ds,
                        "SpacingBetweenSlices",
                        None,
                    )
                ),

            "patient_position":
                get_string(
                    ds,
                    "PatientPosition",
                ),

            "modality":
                get_string(
                    ds,
                    "Modality",
                ),

            "body_part":
                get_string(
                    ds,
                    "BodyPartExamined",
                ),
        }

    except Exception as exc:

        return {

            "error":
                str(exc),

            "path":
                str(path),
        }

# ============================================================
# 18. SORT SERIES
# ============================================================

def sort_series_records(records):

    if not records:

        return records

    orientation = None

    for record in records:

        value = record.get(
            "image_orientation"
        )

        if value is None:

            continue

        try:

            arr = np.asarray(

                value,

                dtype=np.float32,
            )

            if len(arr) == 6:

                orientation = arr

                break

        except Exception:

            pass

    if orientation is not None:

        try:

            row = orientation[:3]

            col = orientation[3:]

            normal = np.cross(
                row,
                col,
            )

            norm = np.linalg.norm(
                normal
            )

            if norm > 0:

                normal = (
                    normal /
                    norm
                )

                def projection(record):

                    pos = record.get(
                        "image_position"
                    )

                    if pos is None:

                        return float(
                            "inf"
                        )

                    try:

                        return float(

                            np.dot(

                                np.asarray(
                                    pos,
                                    dtype=np.float32,
                                ),

                                normal,
                            )
                        )

                    except Exception:

                        return float(
                            "inf"
                        )

                return sorted(

                    records,

                    key=projection,
                )

        except Exception:

            pass

    return sorted(

        records,

        key=lambda x: (

            x.get(
                "instance_number"
            )

            if x.get(
                "instance_number"
            ) is not None

            else 10**9
        )
    )

# ============================================================
# 19. CACHE SIGNATURE
# ============================================================

def make_cache_signature(
    test_csv,
    test_series_csv,
    test_studies,
):

    signature = {

        "version":
            CACHE_VERSION,

        "study_count":
            len(test_studies),

        "study_ids":
            tuple(
                str(x)
                for x in test_studies
            ),
    }

    try:

        stat = test_csv.stat()

        signature[\
            "test_csv_size"\
        ] = stat.st_size

        signature[\
            "test_csv_mtime"\
        ] = stat.st_mtime_ns

    except Exception:

        pass

    try:

        stat = test_series_csv.stat()

        signature[\
            "test_series_csv_size"\
        ] = stat.st_size

        signature[\
            "test_series_csv_mtime"\
        ] = stat.st_mtime_ns

    except Exception:

        pass

    return signature

# ============================================================
# 20. LOAD CACHE
# ============================================================

def load_lookup_cache(
    cache_file,
    signature,
):

    path = Path(
        cache_file
    )

    if not path.exists():

        return None

    try:

        print()
        print(
            "=" * 70
        )

        print(
            "CHECKING STUDY LOOKUP CACHE"
        )

        print(
            "=" * 70
        )

        with open(
            path,
            "rb",
        ) as f:

            payload = pickle.load(
                f
            )

        if not isinstance(
            payload,
            dict,
        ):

            return None

        if (
            payload.get(
                "signature"
            )
            != signature
        ):

            print(
                "Cache signature changed."
            )

            print(
                "Rebuilding lookup..."
            )

            return None

        lookup = payload.get(
            "lookup"
        )

        if lookup is None:

            return None

        print(
            "Cache found:"
        )

        print(
            f"  {path}"
        )

        print(
            f"Cached studies: "
            f"{len(lookup):,}"
        )

        return lookup

    except Exception as exc:

        print(
            "Cache could not be loaded:"
        )

        print(
            f"  {exc}"
        )

        return None

# ============================================================
# 21. SAVE CACHE
# ============================================================

def save_lookup_cache(
    cache_file,
    signature,
    lookup,
):

    path = Path(
        cache_file
    )

    try:

        payload = {

            "signature":
                signature,

            "lookup":
                lookup,
        }

        temp = path.with_suffix(
            ".tmp"
        )

        with open(
            temp,
            "wb",
        ) as f:

            pickle.dump(

                payload,

                f,

                protocol=
                    pickle.HIGHEST_PROTOCOL,
            )

        os.replace(
            temp,
            path,
        )

        print()
        print(
            "Lookup cache saved:"
        )

        print(
            f"  {path}"
        )

    except Exception as exc:

        print(
            "Warning: could not save cache:"
        )

        print(
            f"  {exc}"
        )

# ============================================================
# 22. DICOM FILE DISCOVERY
# ============================================================

def discover_dicom_files(
    series_dir
):

    if not series_dir.is_dir():

        return []

    files = []

    try:

        for path in series_dir.iterdir():

            if not path.is_file():

                continue

            if (
                path.suffix.lower()
                == ".dcm"
            ):

                files.append(
                    path
                )

                continue

            if path.suffix == "":

                files.append(
                    path
                )

    except Exception:

        return []

    return sorted(

        files,

        key=lambda p: p.name,
    )

# ============================================================
# 23. CREATE SERIES LOOKUP
# ============================================================

def create_series_lookup_optimized(
    test_series_root,
    test_studies,
    test_series_df,
    test_csv,
    test_series_csv,
    cache_file=CACHE_FILE,
):

    test_studies = [\
\
        str(x)\
\
        for x in test_studies\
    ]

    signature = make_cache_signature(

        test_csv,

        test_series_csv,

        test_studies,
    )

    cached = load_lookup_cache(

        cache_file,

        signature,
    )

    if cached is not None:

        return cached

    print()
    print(
        "=" * 70
    )

    print(
        "BUILDING TEST SERIES LOOKUP"
    )

    print(
        "=" * 70
    )

    print(
        f"Studies: "
        f"{len(test_studies):,}"
    )

    print(
        "Test DICOM root:"
    )

    print(
        f"  {test_series_root}"
    )

    print()

    lookup = {}

    total_files = 0

    valid_files = 0

    bad_files = 0

    missing_studies = 0

    missing_series = 0

    start_time = time.time()

    metadata = (
        test_series_df.copy()
    )

    metadata[\
        "StudyInstanceUID"\
    ] = metadata[\
        "StudyInstanceUID"\
    ].astype(str)

    metadata[\
        "SeriesInstanceUID"\
    ] = metadata[\
        "SeriesInstanceUID"\
    ].astype(str)

    metadata[\
        "Fluid_Sensitive"\
    ] = pd.to_numeric(

        metadata[\
            "Fluid_Sensitive"\
        ],

        errors="coerce",

    ).fillna(
        0
    ).astype(
        int
    )

    metadata[\
        "Anatomical_Plane"\
    ] = metadata[\
        "Anatomical_Plane"\
    ].astype(str)

    for (
        study_index,
        study_id,
    ) in enumerate(

        test_studies,

        start=1,
    ):

        study_dir = (

            test_series_root /
            study_id
        )

        if not study_dir.is_dir():

            missing_studies += 1

            lookup[\
                study_id\
            ] = {}

            print(

                f"[{study_index}/"\
                f"{len(test_studies)}] "
                f"WARNING: missing study "
                f"{study_id}"
            )

            continue

        study_meta = metadata[\
\
            metadata[\
                "StudyInstanceUID"\
            ]\
            ==\
            study_id\
        ]

        series_lookup = {}

        for _, row in (
            study_meta.iterrows()
        ):

            series_uid = str(

                row[\
                    "SeriesInstanceUID"\
                ]
            )

            series_dir = (

                study_dir /
                series_uid
            )

            if not series_dir.is_dir():

                flat_candidate = (

                    test_series_root /
                    series_uid
                )

                if flat_candidate.is_dir():

                    series_dir = (
                        flat_candidate
                    )

                else:

                    missing_series += 1

                    continue

            dcm_files = (
                discover_dicom_files(
                    series_dir
                )
            )

            if not dcm_files:

                missing_series += 1

                continue

            records = []

            for dcm_path in dcm_files:

                total_files += 1

                record = (
                    read_dicom_metadata(
                        dcm_path
                    )
                )

                if "error" in record:

                    bad_files += 1

                    continue

                valid_files += 1

                records.append(
                    record
                )

                if (

                    total_files
                    %
                    PROGRESS_EVERY_FILES
                    ==
                    0

                ):

                    elapsed = (
                        time.time()
                        -
                        start_time
                    )

                    rate = (

                        total_files
                        /
                        max(
                            elapsed,
                            1e-6,
                        )
                    )

                    print(

                        f"  Files: "
                        f"{total_files:,} | "
                        f"Valid: "
                        f"{valid_files:,} | "
                        f"Bad: "
                        f"{bad_files:,} | "
                        f"{rate:.1f} files/s"
                    )

            if not records:

                continue

            records = (
                sort_series_records(
                    records
                )
            )

            plane = str(

                row[\
                    "Anatomical_Plane"\
                ]
            ).strip()

            fluid_sensitive = int(

                row[\
                    "Fluid_Sensitive"\
                ]
            )

            fat_suppression = int(

                row.get(
                    "Fat_Suppression",
                    0,
                )
            )

            first = records[0]

            series_info = {

                "series_uid":
                    series_uid,

                "series_dir":
                    str(
                        series_dir
                    ),

                "plane":
                    plane,

                "fluid_sensitive":
                    fluid_sensitive,

                "fat_suppression":
                    fat_suppression,

                "series_description":
                    first.get(
                        "series_description",
                        "",
                    ),

                "protocol_name":
                    first.get(
                        "protocol_name",
                        "",
                    ),

                "sequence_name":
                    first.get(
                        "sequence_name",
                        "",
                    ),

                "pixel_spacing":
                    first.get(
                        "pixel_spacing",
                        [0.5, 0.5],
                    ),

                "body_part":
                    first.get(
                        "body_part",
                        "",
                    ),

                "modality":
                    first.get(
                        "modality",
                        "",
                    ),

                "records":
                    records,

                "image_count":
                    len(records),
            }

            series_lookup[\
                series_uid\
            ] = series_info

        lookup[\
            study_id\
        ] = series_lookup

        if (

            study_index == 1

            or

            study_index
            %
            PROGRESS_EVERY_STUDIES
            ==
            0

            or

            study_index
            ==
            len(test_studies)

        ):

            elapsed = (
                time.time()
                -
                start_time
            )

            rate = (

                study_index
                /
                max(
                    elapsed,
                    1e-6,
                )
            )

            remaining = (

                len(test_studies)
                -
                study_index
            )

            eta = (

                remaining
                /
                max(
                    rate,
                    1e-6,
                )
            )

            series_count = sum(

                len(x)

                for x in lookup.values()
            )

            print()

            print(

                f"[{study_index:,}/"\
                f"{len(test_studies):,}] "
                f"studies | "
                f"Series: "
                f"{series_count:,} | "
                f"Files: "
                f"{total_files:,} | "
                f"Bad: "
                f"{bad_files:,} | "
                f"ETA: "
                f"{eta / 60:.2f} min"
            )

    save_lookup_cache(

        cache_file,

        signature,

        lookup,
    )

    elapsed = (
        time.time()
        -
        start_time
    )

    print()
    print(
        "=" * 70
    )

    print(
        "LOOKUP COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Studies indexed: "
        f"{len(lookup):,}"
    )

    print(
        f"Missing studies: "
        f"{missing_studies:,}"
    )

    print(
        f"Missing series: "
        f"{missing_series:,}"
    )

    print(
        f"Valid DICOMs: "
        f"{valid_files:,}"
    )

    print(
        f"Malformed DICOMs: "
        f"{bad_files:,}"
    )

    print(
        f"Total files: "
        f"{total_files:,}"
    )

    print(
        f"Elapsed: "
        f"{elapsed / 60:.2f} minutes"
    )

    if elapsed > 0:

        print(

            f"File rate: "
            f"{total_files / elapsed:.1f} files/s"
        )

    return lookup

# ============================================================
# 24. CHOOSE SERIES
# ============================================================

def choose_series(
    series_lookup,
    plane,
    fluid_preference=None,
):

    if not series_lookup:

        return None

    candidates = []

    for (
        series_uid,
        series,
    ) in series_lookup.items():

        if (

            str(
                series.get(
                    "plane",
                    "",
                )
            ).lower()

            !=

            str(
                plane
            ).lower()

        ):

            continue

        candidates.append(
            series
        )

    if not candidates:

        return None

    if fluid_preference is not None:

        desired = (

            1

            if fluid_preference

            else 0
        )

        fluid_candidates = [\
\
            series\
\
            for series in candidates\
\
            if int(\
                series.get(\
                    "fluid_sensitive",\
                    0,\
                )\
            )\
            ==\
            desired\
        ]

        if fluid_candidates:

            candidates = (
                fluid_candidates
            )

    return max(

        candidates,

        key=lambda x: int(

            x.get(
                "image_count",
                0,
            )
        ),
    )

# ============================================================
# 25. READ DICOM PIXELS
# ============================================================

def read_dicom_pixels(path):

    ds = pydicom.dcmread(

        str(path),

        force=True,
    )

    image = ds.pixel_array

    try:

        image = apply_modality_lut(

            image,

            ds,
        )

    except Exception:

        pass

    image = np.asarray(

        image,

        dtype=np.float32,
    )

    if (

        str(

            getattr(

                ds,

                "PhotometricInterpretation",

                "",
            )
        ).upper()

        ==

        "MONOCHROME1"

    ):

        image = (

            np.max(image)
            -
            image
        )

    image = np.nan_to_num(

        image,

        nan=0.0,

        posinf=0.0,

        neginf=0.0,
    )

    return image

# ============================================================
# 26. PERCENTILE NORMALIZATION
# ============================================================

def normalize_percentile(
    image
):

    image = np.asarray(

        image,

        dtype=np.float32,
    )

    valid = np.isfinite(
        image
    )

    if not valid.any():

        return np.zeros_like(

            image,

            dtype=np.float32,
        )

    values = image[\
        valid\
    ]

    lo, hi = np.percentile(

        values,

        [\
            2,\
            98,\
        ],
    )

    if hi <= lo:

        lo = float(
            values.min()
        )

        hi = float(
            values.max()
        )

    if hi <= lo:

        return np.zeros_like(

            image,

            dtype=np.float32,
        )

    image = (

        image - lo

    ) / (

        hi - lo
    )

    return np.clip(

        image,

        0.0,

        1.0,

    ).astype(
        np.float32
    )

# ============================================================
# 27. CENTRAL PHYSICAL CROP
# ============================================================

def central_physical_crop(
    image,
    pixel_spacing,
    crop_mm,
):

    h, w = image.shape[:2]

    try:

        sy = float(
            pixel_spacing[0]
        )

        sx = float(
            pixel_spacing[1]
        )

    except Exception:

        sy = 0.5

        sx = 0.5

    if sy <= 0:

        sy = 0.5

    if sx <= 0:

        sx = 0.5

    crop_h = max(

        1,

        int(

            round(
                crop_mm / sy
            )
        ),
    )

    crop_w = max(

        1,

        int(

            round(
                crop_mm / sx
            )
        ),
    )

    crop_h = min(
        crop_h,
        h,
    )

    crop_w = min(
        crop_w,
        w,
    )

    y0 = max(

        0,

        (h - crop_h) // 2,
    )

    x0 = max(

        0,

        (w - crop_w) // 2,
    )

    return image[\
\
        y0:\
        y0 + crop_h,\
\
        x0:\
        x0 + crop_w,\
    ]

# ============================================================
# 28. RESIZE
# ============================================================

def resize_image(
    image,
    size,
):

    if (

        image.shape[0]
        ==
        size

        and

        image.shape[1]
        ==
        size

    ):

        return image.astype(
            np.float32
        )

    return cv2.resize(

        image,

        (
            size,
            size,
        ),

        interpolation=
            cv2.INTER_AREA,

    ).astype(
        np.float32
    )

# ============================================================
# 29. BUILD VOLUME
# ============================================================

def build_volume(
    series_lookup,
    total_slices=TOTAL_SLICES,
):

    volume = np.zeros(

        (

            total_slices,

            IMAGE_SIZE,

            IMAGE_SIZE,
        ),

        dtype=np.float32,
    )

    valid = np.zeros(

        total_slices,

        dtype=bool,
    )

    cursor = 0

    for (

        plane,
        fluid_flag,
        count,

    ) in SERIES_SLOTS:

        count = min(

            int(count),

            total_slices - cursor,
        )

        if count <= 0:

            break

        fluid_preference = (

            None

            if fluid_flag == -1

            else bool(fluid_flag)
        )

        series = choose_series(

            series_lookup,

            plane,

            fluid_preference,
        )

        if series is None:

            cursor += count

            continue

        records = series.get(

            "records",

            [],
        )

        if not records:

            cursor += count

            continue

        n = len(records)

        if n == 1:

            indices = np.zeros(

                count,

                dtype=int,
            )

        else:

            indices = (

                np.linspace(

                    0,

                    n - 1,

                    count,
                )

                .round()

                .astype(int)
            )

        for (

            local_idx,
            src_idx,

        ) in enumerate(indices):

            dst_idx = (

                cursor
                +
                local_idx
            )

            if dst_idx >= total_slices:

                break

            record = records[\
                int(src_idx)\
            ]

            try:

                image = (
                    read_dicom_pixels(
                        record["path"]
                    )
                )

                image = (
                    normalize_percentile(
                        image
                    )
                )

                spacing = (

                    record.get(

                        "pixel_spacing",

                        [\
                            0.5,\
                            0.5,\
                        ],
                    )
                )

                image = (
                    central_physical_crop(

                        image,

                        spacing,

                        CROP_MM,
                    )
                )

                image = (
                    resize_image(

                        image,

                        IMAGE_SIZE,
                    )
                )

                volume[\
                    dst_idx\
                ] = image

                valid[\
                    dst_idx\
                ] = True

            except Exception:

                pass

        cursor += count

    return (
        volume,
        valid,
    )

# ============================================================
# 30. MAKE SLICE CENTERS
# ============================================================

def make_centers(
    valid_mask,
    k,
    lo,
    hi,
):

    valid_indices = np.where(
        valid_mask
    )[0]

    if len(valid_indices) == 0:

        return (

            np.linspace(

                0,

                TOTAL_SLICES - 1,

                k,
            )

            .round()

            .astype(int)
        )

    first = int(
        valid_indices[0]
    )

    last = int(
        valid_indices[-1]
    )

    lo_idx = int(

        round(

            first

            +

            lo
            *
            (
                last - first
            )
        )
    )

    hi_idx = int(

        round(

            first

            +

            hi
            *
            (
                last - first
            )
        )
    )

    lo_idx = max(

        first,

        min(
            lo_idx,
            last,
        ),
    )

    hi_idx = max(

        lo_idx,

        min(
            hi_idx,
            last,
        ),
    )

    centers = (

        np.linspace(

            lo_idx,

            hi_idx,

            k,
        )

        .round()

        .astype(int)
    )

    return centers

# ============================================================
# 31. CREATE 2.5D RGB WINDOWS
# ============================================================

def create_windows(
    volume,
    centers,
):

    windows = []

    for center in centers:

        center = int(
            center
        )

        prev_idx = max(

            0,

            center - 1,
        )

        next_idx = min(

            volume.shape[0] - 1,

            center + 1,
        )

        rgb = np.stack(

            [\
\
                volume[\
                    prev_idx\
                ],\
\
                volume[\
                    center\
                ],\
\
                volume[\
                    next_idx\
                ],\
            ],

            axis=0,
        )

        rgb = np.clip(

            rgb,

            0.0,

            1.0,

        ).astype(
            np.float32
        )

        rgb = (

            rgb

            -

            IMAGENET_MEAN[\
                :,\
                None,\
                None,\
            ]

        ) / (

            IMAGENET_STD[\
                :,\
                None,\
                None,\
            ]
        )

        windows.append(
            rgb
        )

    if not windows:

        return np.empty(

            (

                0,

                3,

                IMAGE_SIZE,

                IMAGE_SIZE,
            ),

            dtype=np.float32,
        )

    return np.stack(

        windows,

        axis=0,
    )

# ============================================================
# 32. MODEL
# ============================================================

class CheckpointFreeKneeModel(
    nn.Module
):

    def __init__(
        self,
        arch=DEFAULT_ARCH,
        num_classes=NUM_CLASSES,
        pretrained=False,
    ):

        super().__init__()

        print()
        print(
            "Creating CoAtNet:"
        )

        print(
            f"  Architecture: {arch}"
        )

        print(
            f"  Pretrained: {pretrained}"
        )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # This call is offline-safe when pretrained=False.
        #
        # We NEVER let timm attempt an online download.
        # ----------------------------------------------------

        self.backbone = (
            timm.create_model(

                arch,

                pretrained=pretrained,

                num_classes=num_classes,

                in_chans=3,
            )
        )

        self.num_classes = (
            num_classes
        )

    def forward(
        self,
        x,
    ):

        return self.backbone(x)

# ============================================================
# 33. FIND LOCAL CHECKPOINTS
# ============================================================

def find_local_model_files():

    candidates = []

    # --------------------------------------------------------
    # Explicit checkpoint first.
    # --------------------------------------------------------

    if MODEL_CHECKPOINT is not None:

        path = Path(
            MODEL_CHECKPOINT
        )

        if path.is_file():

            candidates.append(
                path
            )

    # --------------------------------------------------------
    # Search Kaggle input for common model files.
    # --------------------------------------------------------

    kaggle_input = Path(
        "/kaggle/input"
    )

    if kaggle_input.exists():

        patterns = [\
\
            "*.pth",\
\
            "*.pt",\
\
            "*.bin",\
\
            "*.safetensors",\
        ]

        for pattern in patterns:

            try:

                candidates.extend(

                    kaggle_input.glob(
                        f"**/{pattern}"
                    )
                )

            except Exception:

                pass

    # --------------------------------------------------------
    # Search working directory.
    # --------------------------------------------------------

    working = Path(
        "/kaggle/working"
    )

    if working.exists():

        patterns = [\
\
            "*.pth",\
\
            "*.pt",\
\
            "*.bin",\
\
            "*.safetensors",\
        ]

        for pattern in patterns:

            try:

                candidates.extend(

                    working.glob(
                        f"**/{pattern}"
                    )
                )

            except Exception:

                pass

    # --------------------------------------------------------
    # Remove duplicates.
    # --------------------------------------------------------

    unique = []

    seen = set()

    for path in candidates:

        try:

            key = str(
                path.resolve()
            )

        except Exception:

            key = str(path)

        if key in seen:

            continue

        seen.add(key)

        unique.append(
            path
        )

    return unique

# ============================================================
# 34. INSPECT CHECKPOINT
# ============================================================

def checkpoint_looks_compatible(
    checkpoint_path
):

    try:

        checkpoint = torch.load(

            checkpoint_path,

            map_location="cpu",

            weights_only=False,
        )

    except Exception as exc:

        print()
        print(
            "Could not inspect checkpoint:"
        )

        print(
            f"  {checkpoint_path}"
        )

        print(
            f"  {exc}"
        )

        return False

    state_dict = None

    if isinstance(
        checkpoint,
        dict,
    ):

        # Common formats.
        for key in [\
\
            "state_dict",\
\
            "model_state_dict",\
\
            "model",\
\
            "weights",\
        ]:

            if key in checkpoint:

                candidate = (
                    checkpoint[key]
                )

                if isinstance(
                    candidate,
                    dict,
                ):

                    state_dict = (
                        candidate
                    )

                    break

        if state_dict is None:

            # Could itself be a state_dict.
            if all(

                isinstance(
                    k,
                    str,
                )

                for k in checkpoint.keys()

            ):

                state_dict = checkpoint

    if state_dict is None:

        print(
            "Checkpoint format not recognized."
        )

        return False

    # --------------------------------------------------------
    # Look for a classifier tensor.
    # --------------------------------------------------------

    possible_heads = []

    for key, value in (
        state_dict.items()
    ):

        if not torch.is_tensor(
            value
        ):

            continue

        if value.ndim != 2:

            continue

        if (
            value.shape[0]
            ==
            NUM_CLASSES
        ):

            possible_heads.append(
                (
                    key,
                    tuple(
                        value.shape
                    ),
                )
            )

    print()
    print(
        "Checkpoint inspection:"
    )

    print(
        f"  File: {checkpoint_path}"
    )

    print(
        f"  Candidate 12-class heads:"
        f" {len(possible_heads)}"
    )

    for key, shape in (
        possible_heads[:10]
    ):

        print(
            f"    {key}: {shape}"
        )

    return len(
        possible_heads
    ) > 0

# ============================================================
# 35. LOAD CHECKPOINT STATE
# ============================================================

def load_checkpoint_state(
    model,
    checkpoint_path,
):

    print()
    print(
        "=" * 70
    )

    print(
        "LOADING LOCAL CHECKPOINT"
    )

    print(
        "=" * 70
    )

    print(
        f"Checkpoint:"
    )

    print(
        f"  {checkpoint_path}"
    )

    checkpoint = torch.load(

        checkpoint_path,

        map_location="cpu",

        weights_only=False,
    )

    state_dict = None

    if isinstance(
        checkpoint,
        dict,
    ):

        for key in [\
\
            "state_dict",\
\
            "model_state_dict",\
\
            "model",\
\
            "weights",\
        ]:

            if key in checkpoint:

                candidate = (
                    checkpoint[key]
                )

                if isinstance(
                    candidate,
                    dict,
                ):

                    state_dict = (
                        candidate
                    )

                    break

        if state_dict is None:

            if all(

                isinstance(
                    k,
                    str,
                )

                for k in checkpoint.keys()

            ):

                state_dict = checkpoint

    if state_dict is None:

        raise RuntimeError(

            "Could not locate a state_dict "
            "inside the checkpoint."
        )

    # --------------------------------------------------------
    # Remove DataParallel prefix.
    # --------------------------------------------------------

    cleaned = {}

    for key, value in (
        state_dict.items()
    ):

        if key.startswith(
            "module."
        ):

            key = key[\
                len("module.") :\
            ]

        cleaned[key] = value

    state_dict = cleaned

    # --------------------------------------------------------
    # Try strict loading first.
    # --------------------------------------------------------

    try:

        result = model.load_state_dict(

            state_dict,

            strict=True,
        )

        print(
            "Checkpoint loaded with "
            "strict=True."
        )

        return True

    except Exception as exc:

        print()
        print(
            "Strict checkpoint loading failed:"
        )

        print(
            str(exc)[:3000]
        )

    # --------------------------------------------------------
    # Try non-strict loading.
    # --------------------------------------------------------

    try:

        result = model.load_state_dict(

            state_dict,

            strict=False,
        )

        print()
        print(
            "Checkpoint loaded with "
            "strict=False."
        )

        print(
            f"Missing keys: "
            f"{len(result.missing_keys)}"
        )

        print(
            f"Unexpected keys: "
            f"{len(result.unexpected_keys)}"
        )

        return True

    except Exception as exc:

        print()
        print(
            "Non-strict checkpoint loading "
            "also failed:"
        )

        print(
            str(exc)[:3000]
        )

        return False

# ============================================================
# 36. LOAD MODEL — STRICTLY OFFLINE
# ============================================================

def load_model():

    print()
    print(
        "=" * 70
    )

    print(
        "LOADING OFFLINE MODEL"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # STEP A
    # Look for an actual trained local checkpoint.
    # --------------------------------------------------------

    local_files = (
        find_local_model_files()
    )

    if local_files:

        print()
        print(
            "Local model files found:"
        )

        for path in local_files[:20]:

            print(
                f"  {path}"
            )

        # ----------------------------------------------------
        # Prefer explicit MODEL_CHECKPOINT.
        # ----------------------------------------------------

        ordered = []

        if MODEL_CHECKPOINT is not None:

            explicit = Path(
                MODEL_CHECKPOINT
            )

            if explicit in local_files:

                ordered.append(
                    explicit
                )

        for path in local_files:

            if path not in ordered:

                ordered.append(
                    path
                )

        # ----------------------------------------------------
        # Try compatible checkpoints.
        # ----------------------------------------------------

        for checkpoint_path in ordered:

            if not checkpoint_path.is_file():

                continue

            try:

                if not checkpoint_looks_compatible(
                    checkpoint_path
                ):

                    continue

                model = (
                    CheckpointFreeKneeModel(

                        arch=DEFAULT_ARCH,

                        num_classes=NUM_CLASSES,

                        pretrained=False,
                    )
                )

                loaded = (
                    load_checkpoint_state(

                        model,

                        checkpoint_path,
                    )
                )

                if loaded:

                    model = model.to(
                        DEVICE
                    )

                    model.eval()

                    print()
                    print(
                        "SUCCESS:"
                    )

                    print(
                        "Using local trained "
                        "RSNA checkpoint."
                    )

                    return model

            except Exception as exc:

                print()
                print(
                    "Checkpoint attempt failed:"
                )

                print(
                    f"  {checkpoint_path}"
                )

                print(
                    f"  {exc}"
                )

    # --------------------------------------------------------
    # STEP B
    #
    # IMPORTANT:
    #
    # We DO NOT call:
    #
    # timm.create_model(..., pretrained=True)
    #
    # because that can attempt Hugging Face access.
    #
    # Instead, we create the architecture locally.
    # --------------------------------------------------------

    print()
    print(
        "No compatible local RSNA checkpoint found."
    )

    print()
    print(
        "Creating CoAtNet with pretrained=False."
    )

    print(
        "This guarantees no Hugging Face download."
    )

    model = (
        CheckpointFreeKneeModel(

            arch=DEFAULT_ARCH,

            num_classes=NUM_CLASSES,

            pretrained=False,
        )
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    print()
    print(
        "WARNING:"
    )

    print(
        "The current model has randomly initialized "
        "weights."
    )

    print(
        "It is NOT a trained RSNA 12-label model."
    )

    print()
    print(
        "The pipeline is now completely offline."
    )

    return model

# ============================================================
# 37. PREDICT WINDOWS
# ============================================================

@torch.inference_mode()
def predict_windows(
    model,
    windows,
    batch_size=16,
):

    if len(windows) == 0:

        return np.zeros(

            NUM_CLASSES,

            dtype=np.float32,
        )

    predictions = []

    for start in range(

        0,

        len(windows),

        batch_size,
    ):

        batch = torch.from_numpy(

            windows[\
\
                start:\
                start + batch_size\
            ]
        ).to(

            DEVICE,

            non_blocking=True,
        )

        try:

            if DEVICE.type == "cuda":

                with torch.autocast(

                    device_type="cuda",

                    dtype=torch.float16,
                ):

                    logits = model(
                        batch
                    )

            else:

                logits = model(
                    batch
                )

        except Exception:

            logits = model(
                batch
            )

        if logits.ndim == 1:

            logits = logits.unsqueeze(
                0
            )

        probs = torch.sigmoid(

            logits.float()
        )

        predictions.append(

            probs.detach()
            .cpu()
            .numpy()
        )

    predictions = np.concatenate(

        predictions,

        axis=0,
    )

    return predictions.mean(

        axis=0

    ).astype(
        np.float32
    )

# ============================================================
# 38. TTA FUSION
# ============================================================

def fuse_tta(
    predictions,
    weights,
):

    predictions = np.asarray(

        predictions,

        dtype=np.float32,
    )

    weights = np.asarray(

        weights,

        dtype=np.float32,
    )

    weight_sum = weights.sum()

    if weight_sum <= 0:

        weights = np.ones_like(
            weights
        )

        weight_sum = weights.sum()

    weights = (

        weights
        /
        weight_sum
    )

    probabilities = np.clip(

        predictions,

        1e-6,

        1.0 - 1e-6,
    )

    logits = np.log(

        probabilities

        /

        (
            1.0
            -
            probabilities
        )
    )

    fused_logits = np.sum(

        logits
        *
        weights[:, None],

        axis=0,
    )

    fused_probs = (

        1.0

        /

        (

            1.0
            +
            np.exp(
                -fused_logits
            )
        )
    )

    direct_probs = np.sum(

        probabilities
        *
        weights[:, None],

        axis=0,
    )

    fused = (

        0.60
        *
        fused_probs

        +

        0.40
        *
        direct_probs
    )

    return np.clip(

        fused,

        0.0,

        1.0,

    ).astype(
        np.float32
    )

# ============================================================
# 39. PREDICT ONE STUDY
# ============================================================

def predict_study(
    model,
    series_lookup,
):

    volume, valid = (
        build_volume(

            series_lookup,

            TOTAL_SLICES,
        )
    )

    valid_count = int(
        valid.sum()
    )

    if valid_count == 0:

        print(
            "WARNING: study contains "
            "no valid DICOM slices."
        )

        return np.full(

            NUM_CLASSES,

            0.5,

            dtype=np.float32,
        )

    tta_predictions = []

    tta_weights = []

    for config in TTA_CONFIGS:

        centers = make_centers(

            valid,

            config["k"],

            config["lo"],

            config["hi"],
        )

        windows = create_windows(

            volume,

            centers,
        )

        prediction = (
            predict_windows(

                model,

                windows,
            )
        )

        tta_predictions.append(
            prediction
        )

        tta_weights.append(
            config["weight"]
        )

        del windows

        if DEVICE.type == "cuda":

            torch.cuda.empty_cache()

    result = fuse_tta(

        tta_predictions,

        tta_weights,
    )

    del volume

    del valid

    return result

# ============================================================
# 40. FINAL RANK CALIBRATION
# ============================================================

def final_rank_calibration(
    predictions,
):

    predictions = np.asarray(

        predictions,

        dtype=np.float32,
    ).copy()

    if len(predictions) <= 1:

        return np.clip(

            predictions,

            0.0,

            1.0,
        )

    for j, label in enumerate(
        LABELS
    ):

        values = predictions[\
            :,\
            j,\
        ]

        order = np.argsort(

            np.argsort(
                values
            )
        )

        ranks = (

            order.astype(
                np.float32
            )

            /

            max(

                len(values) - 1,

                1,
            )
        )

        weight = (

            TARGET_RANK_WEIGHTS.get(

                label,

                0.0,
            )
        )

        predictions[\
\
            :,\
\
            j\
\
        ] = (

            (

                1.0
                -
                weight
            )

            *

            values

            +

            weight

            *

            ranks
        )

    return np.clip(

        predictions,

        0.0,

        1.0,
    )

# ============================================================
# 41. SAMPLE SUBMISSION
# ============================================================

def load_sample_submission(
    root
):

    path = (

        root /

        "sample_submission.csv"
    )

    if path.is_file():

        return pd.read_csv(
            path
        )

    matches = list(

        root.glob(

            "**/sample_submission.csv"
        )
    )

    if matches:

        return pd.read_csv(
            matches[0]
        )

    return None

# ============================================================
# 42. VALIDATE SUBMISSION
# ============================================================

def validate_submission(
    submission,
    sample_submission=None,
):

    if submission.empty:

        raise ValueError(
            "Submission is empty."
        )

    id_col = (
        submission.columns[0]
    )

    expected_columns = [\
\
        id_col\
\
    ] + LABELS

    missing = [\
\
        col\
\
        for col in expected_columns\
\
        if col not in submission.columns\
    ]

    if missing:

        raise ValueError(

            f"Missing columns: {missing}"
        )

    prediction_values = (

        submission[\
            LABELS\
        ].to_numpy()
    )

    if not np.isfinite(
        prediction_values
    ).all():

        raise ValueError(

            "Submission contains "
            "NaN or infinite values."
        )

    if (

        prediction_values.min()
        <
        0

        or

        prediction_values.max()
        >
        1

    ):

        raise ValueError(

            "Predictions must be "
            "between 0 and 1."
        )

    if sample_submission is not None:

        expected = list(

            sample_submission.columns
        )

        actual = list(

            submission.columns
        )

        if expected != actual:

            raise ValueError(

                "\nSubmission columns do not "
                "match sample_submission.\n"

                f"Expected: {expected}\n"

                f"Actual:   {actual}"
            )

        if (

            len(submission)

            !=

            len(sample_submission)

        ):

            raise ValueError(

                "Submission row count does "
                "not match sample_submission."
            )

        id_col = expected[0]

        actual_ids = (

            submission[\
                id_col\
            ].astype(str)
        )

        expected_ids = (

            sample_submission[\
                id_col\
            ].astype(str)
        )

        if not actual_ids.equals(
            expected_ids
        ):

            raise ValueError(

                "Submission IDs/order do "
                "not match sample_submission."
            )

    print(
        "Submission validation: PASSED"
    )

# ============================================================
# 43. SANITY CHECK LOOKUP
# ============================================================

def sanity_check_lookup(
    lookup,
    test_studies,
):

    print()
    print(
        "=" * 70
    )

    print(
        "LOOKUP SANITY CHECK"
    )

    print(
        "=" * 70
    )

    total_series = 0

    total_slices = 0

    studies_with_data = 0

    for study_id in test_studies:

        study = lookup.get(

            str(study_id),

            {},
        )

        series_count = len(
            study
        )

        slice_count = sum(

            int(

                s.get(

                    "image_count",

                    0,
                )
            )

            for s in study.values()
        )

        total_series += (
            series_count
        )

        total_slices += (
            slice_count
        )

        if slice_count > 0:

            studies_with_data += 1

        print(

            f"Study {study_id}: "

            f"{series_count} series | "

            f"{slice_count} slices"
        )

    print()

    print(

        f"Studies with DICOMs: "

        f"{studies_with_data}/"

        f"{len(test_studies)}"
    )

    print(

        f"Total series: "

        f"{total_series:,}"
    )

    print(

        f"Total DICOM slices: "

        f"{total_slices:,}"
    )

    if (

        studies_with_data

        ==

        0

    ):

        raise RuntimeError(

            "\nNO TEST DICOM DATA FOUND.\n"

            "\n"

            "Check that the competition input "
            "contains test_series/.\n"
        )

    print(
        "Lookup sanity check: PASSED"
    )

# ============================================================
# 44. BUILD TEST LOOKUP
# ============================================================

def build_lookup_for_test(
    root,
    test_df,
    id_col,
):

    test_series_root = (
        locate_test_series(
            root
        )
    )

    (
        test_series_df,
        test_series_csv,
    ) = (

        load_test_series_csv(
            root
        )
    )

    test_studies = (

        test_df[\
            id_col\
        ]

        .astype(str)

        .tolist()
    )

    lookup = (

        create_series_lookup_optimized(

            test_series_root,

            test_studies,

            test_series_df,

            root / "test.csv",

            test_series_csv,

            CACHE_FILE,
        )
    )

    sanity_check_lookup(

        lookup,

        test_studies,
    )

    return lookup

# ============================================================
# 45. OFFLINE STATUS CHECK
# ============================================================

def print_offline_status():

    print()
    print(
        "=" * 70
    )

    print(
        "OFFLINE STATUS CHECK"
    )

    print(
        "=" * 70
    )

    print(
        "Hugging Face offline:",
        os.environ.get(
            "HF_HUB_OFFLINE"
        )
    )

    print(
        "Transformers offline:",
        os.environ.get(
            "TRANSFORMERS_OFFLINE"
        )
    )

    print(
        "Xet disabled:",
        os.environ.get(
            "HF_HUB_DISABLE_XET"
        )
    )

    print()

    print(
        "No internet download will be "
        "attempted by this pipeline."
    )

# ============================================================
# 46. MAIN
# ============================================================

def main():

    total_start = time.time()

    # --------------------------------------------------------
    # OFFLINE STATUS
    # --------------------------------------------------------

    print_offline_status()

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 1 — LOCATING DATA"
    )

    print(
        "=" * 70
    )

    root = (
        locate_competition_root()
    )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 2 — READING TEST CSV"
    )

    print(
        "=" * 70
    )

    (
        test_df,
        id_col,
        test_csv,
    ) = load_test_csv(
        root
    )

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 3 — BUILDING TEST SERIES LOOKUP"
    )

    print(
        "=" * 70
    )

    lookup = (
        build_lookup_for_test(

            root,

            test_df,

            id_col,
        )
    )

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 4 — LOADING OFFLINE MODEL"
    )

    print(
        "=" * 70
    )

    model = load_model()

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 5 — RUNNING OFFLINE INFERENCE"
    )

    print(
        "=" * 70
    )

    predictions = []

    study_ids = (

        test_df[\
            id_col\
        ]

        .astype(str)

        .tolist()
    )

    inference_start = time.time()

    for (

        index,

        study_id,

    ) in enumerate(

        study_ids,

        start=1,
    ):

        series_lookup = (

            lookup.get(

                study_id,

                {},
            )
        )

        try:

            prediction = (

                predict_study(

                    model,

                    series_lookup,
                )
            )

        except Exception as exc:

            print()

            print(

                f"WARNING: inference failed "
                f"for study {study_id}"
            )

            print(
                f"Reason: {exc}"
            )

            prediction = np.full(

                NUM_CLASSES,

                0.5,

                dtype=np.float32,
            )

        predictions.append(
            prediction
        )

        if (

            index == 1

            or

            index
            %
            PROGRESS_EVERY_STUDIES
            ==
            0

            or

            index
            ==
            len(study_ids)

        ):

            elapsed = (

                time.time()
                -
                inference_start
            )

            rate = (

                index
                /
                max(
                    elapsed,
                    1e-6,
                )
            )

            remaining = (

                len(study_ids)
                -
                index
            )

            eta = (

                remaining
                /
                max(
                    rate,
                    1e-6,
                )
            )

            print(

                f"[{index:,}/"\
                f"{len(study_ids):,}] "

                f"studies | "

                f"{rate:.3f} studies/s | "

                f"ETA: "
                f"{eta / 60:.2f} min"
            )

        gc.collect()

    predictions = np.vstack(
        predictions
    )

    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 6 — FINAL RANK CALIBRATION"
    )

    print(
        "=" * 70
    )

    calibrated = (

        final_rank_calibration(

            predictions
        )
    )

    # --------------------------------------------------------
    # STEP 7
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "STEP 7 — CREATING OFFLINE SUBMISSION"
    )

    print(
        "=" * 70
    )

    submission = pd.DataFrame(

        calibrated,

        columns=LABELS,
    )

    submission.insert(

        0,

        id_col,

        test_df[\
            id_col\
        ].values,
    )

    sample_submission = (

        load_sample_submission(
            root
        )
    )

    validate_submission(

        submission,

        sample_submission,
    )

    submission.to_csv(

        OUTPUT_FILE,

        index=False,
    )

    print()
    print(
        "Submission saved:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print()

    print(
        submission.head()
    )

    # --------------------------------------------------------
    # Prediction statistics
    # --------------------------------------------------------

    print()
    print(
        "Prediction statistics:"
    )

    print()

    stats = pd.DataFrame({

        "label":
            LABELS,

        "min":
            calibrated.min(
                axis=0
            ),

        "mean":
            calibrated.mean(
                axis=0
            ),

        "max":
            calibrated.max(
                axis=0
            ),
    })

    print(

        stats.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # STEP 8
    # --------------------------------------------------------

    total_elapsed = (

        time.time()
        -
        total_start
    )

    print()
    print(
        "=" * 70
    )

    print(
        "PIPELINE COMPLETE"
    )

    print(
        "=" * 70
    )

    print(

        f"Studies: "
        f"{len(submission):,}"
    )

    print(

        f"Labels: "
        f"{NUM_CLASSES}"
    )

    print()

    print(
        "Output:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print()

    print(
        "Total runtime:"
    )

    print(
        f"  {total_elapsed / 60:.2f} minutes"
    )

    print()

    print(
        "OFFLINE SUBMISSION READY."
    )

    return submission

# ============================================================
# 47. RUN
# ============================================================

if __name__ == "__main__":

    submission = main()
```

```
======================================================================
STRICT OFFLINE MODE
======================================================================
HF_HUB_OFFLINE: 1
TRANSFORMERS_OFFLINE: 1
HF_HUB_DISABLE_XET: 1

======================================================================
RSNA KNEE ABNORMALITY — OFFLINE V6
======================================================================
Device: cuda
GPU: Tesla T4

======================================================================
OFFLINE STATUS CHECK
======================================================================
Hugging Face offline: 1
Transformers offline: 1
Xet disabled: 1

No internet download will be attempted by this pipeline.

======================================================================
STEP 1 — LOCATING DATA
======================================================================
Using competition root:
  /kaggle/input/competitions/rsna-knee-abnormality-detection

======================================================================
STEP 2 — READING TEST CSV
======================================================================
Test CSV:
  /kaggle/input/competitions/rsna-knee-abnormality-detection/test.csv
Test studies: 3

======================================================================
STEP 3 — BUILDING TEST SERIES LOOKUP
======================================================================
Using official test DICOM directory:
  /kaggle/input/competitions/rsna-knee-abnormality-detection/test_series
Test series CSV:
  /kaggle/input/competitions/rsna-knee-abnormality-detection/test_series.csv
Test series: 15

Series metadata columns:
  ['StudyInstanceUID', 'SeriesInstanceUID', 'Fluid_Sensitive', 'Fat_Suppression', 'Anatomical_Plane']

======================================================================
BUILDING TEST SERIES LOOKUP
======================================================================
Studies: 3
Test DICOM root:
  /kaggle/input/competitions/rsna-knee-abnormality-detection/test_series

[1/3] studies | Series: 5 | Files: 284 | Bad: 0 | ETA: 0.14 min

[3/3] studies | Series: 15 | Files: 557 | Bad: 0 | ETA: 0.00 min

Lookup cache saved:
  /kaggle/working/rsna_knee_study_lookup_cache_v6.pkl

======================================================================
LOOKUP COMPLETE
======================================================================
Studies indexed: 3
Missing studies: 0
Missing series: 0
Valid DICOMs: 557
Malformed DICOMs: 0
Total files: 557
Elapsed: 0.11 minutes
File rate: 86.2 files/s

======================================================================
LOOKUP SANITY CHECK
======================================================================
Study 1.2.826.0.1.3680043.8.498.10047035057544427318018579121635276191: 5 series | 284 slices
Study 1.2.826.0.1.3680043.8.498.10062861783145312629332250977456991776: 5 series | 135 slices
Study 1.2.826.0.1.3680043.8.498.10067514707072572280263481548497591402: 5 series | 138 slices

Studies with DICOMs: 3/3
Total series: 15
Total DICOM slices: 557
Lookup sanity check: PASSED

======================================================================
STEP 4 — LOADING OFFLINE MODEL
======================================================================

======================================================================
LOADING OFFLINE MODEL
======================================================================

No compatible local RSNA checkpoint found.

Creating CoAtNet with pretrained=False.
This guarantees no Hugging Face download.

Creating CoAtNet:
  Architecture: coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k
  Pretrained: False

WARNING:
The current model has randomly initialized weights.
It is NOT a trained RSNA 12-label model.

The pipeline is now completely offline.

======================================================================
STEP 5 — RUNNING OFFLINE INFERENCE
======================================================================
[1/3] studies | 0.052 studies/s | ETA: 0.65 min
[3/3] studies | 0.094 studies/s | ETA: 0.00 min

======================================================================
STEP 6 — FINAL RANK CALIBRATION
======================================================================

======================================================================
STEP 7 — CREATING OFFLINE SUBMISSION
======================================================================
Submission validation: PASSED

Submission saved:
  /kaggle/working/submission.csv

                                    StudyInstanceUID       ACL       MCL  \
0  1.2.826.0.1.3680043.8.498.10047035057544427318...  0.514888  0.505839
1  1.2.826.0.1.3680043.8.498.10062861783145312629...  0.867631  0.786998
2  1.2.826.0.1.3680043.8.498.10067514707072572280...  0.150061  0.189596

   Medial Meniscus  Lateral Meniscus  Medial OA  Lateral OA     PF OA  \
0         0.476607          0.834297   0.472002    0.466512  0.775818
1         0.801705          0.112823   0.164246    0.122468  0.484018
2         0.140578          0.473186   0.810894    0.833237  0.176349

   Effusion  Synovitis   Baker's  Contusion  Fracture
0  0.262288   0.500591  0.486269   0.521062  0.490836
1  0.785951   0.791754  0.206193   0.824707  0.140275
2  0.524742   0.196758  0.801379   0.206940  0.844353

Prediction statistics:

           label      min     mean      max
             ACL 0.150061 0.510860 0.867631
             MCL 0.189596 0.494144 0.786998
 Medial Meniscus 0.140578 0.472963 0.801705
Lateral Meniscus 0.112823 0.473435 0.834297
       Medial OA 0.164246 0.482381 0.810894
      Lateral OA 0.122468 0.474072 0.833237
           PF OA 0.176349 0.478728 0.775818
        Effusion 0.262288 0.524327 0.785951
       Synovitis 0.196758 0.496368 0.791754
         Baker's 0.206193 0.497947 0.801379
       Contusion 0.206940 0.517570 0.824707
        Fracture 0.140275 0.491821 0.844353

======================================================================
PIPELINE COMPLETE
======================================================================
Studies: 3
Labels: 12

Output:
  /kaggle/working/submission.csv

Total runtime:
  9.56 minutes

OFFLINE SUBMISSION READY.
```

linkcode

# Final Image Visualization     [¶](https://www.kaggle.com/code/jocelyndumlao/rsna-knee-abnormality-multi-view-ensemble\#-Final-Image-Visualization)

unfold\_moreShow hidden code

In \[3\]:

linkcode

```
#  FINAL IMAGE VISUALIZATIONS

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# BASIC VALIDATION
# ============================================================

print()
print("=" * 70)
print("FINAL IMAGE VISUALIZATIONS")
print("=" * 70)

# ------------------------------------------------------------
# Validate submission
# ------------------------------------------------------------

if "submission" not in globals():
    raise NameError(
        "The `submission` DataFrame does not exist. "
        "Please run the prediction/submission cells first."
    )

if "LABELS" not in globals():
    raise NameError(
        "The `LABELS` variable is not defined. "
        "Please run the label-definition cell first."
    )

if len(submission) == 0:
    raise ValueError(
        "The submission DataFrame is empty."
    )

# ============================================================
# AUTOMATICALLY FIND ID COLUMN
# ============================================================

# Common ID column names used in RSNA-style datasets.
possible_id_columns = [\
    "StudyInstanceUID",\
    "study_id",\
    "studyId",\
    "StudyID",\
    "id",\
    "ID",\
    "patient_id",\
    "PatientID",\
]

id_col = None

for candidate in possible_id_columns:

    if candidate in submission.columns:

        id_col = candidate
        break

# ------------------------------------------------------------
# Fallback:
# use the first column that is NOT a prediction label
# ------------------------------------------------------------

if id_col is None:

    non_label_columns = [\
        col\
        for col in submission.columns\
        if col not in LABELS\
    ]

    if len(non_label_columns) > 0:

        id_col = non_label_columns[0]

# ------------------------------------------------------------
# Stop with a clear message if no ID column exists
# ------------------------------------------------------------

if id_col is None:

    raise ValueError(
        "Could not identify the submission ID column.\n"
        f"Available columns: {list(submission.columns)}"
    )

print()
print(f"Submission rows : {len(submission):,}")
print(f"ID column       : {id_col}")
print(f"Prediction cols : {len(LABELS)}")

# ============================================================
# VALIDATE LABEL COLUMNS
# ============================================================

missing_labels = [\
    label\
    for label in LABELS\
    if label not in submission.columns\
]

if len(missing_labels) > 0:

    raise ValueError(
        "The following LABELS are missing from submission:\n"
        f"{missing_labels}\n\n"
        f"Available columns:\n"
        f"{list(submission.columns)}"
    )

# ============================================================
# OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR = "/kaggle/working"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)

# ============================================================
# VISUALIZATION 1
# Prediction Distribution
# ============================================================

print()
print("=" * 70)
print("VISUALIZATION 1 — PREDICTION DISTRIBUTION")
print("=" * 70)

plt.figure(
    figsize=(12, 6)
)

for label in LABELS:

    values = pd.to_numeric(
        submission[label],
        errors="coerce",
    ).dropna()

    plt.hist(
        values,
        bins=30,
        alpha=0.35,
        label=label,
    )

plt.xlabel(
    "Predicted probability"
)

plt.ylabel(
    "Number of studies"
)

plt.title(
    "Distribution of Predicted Knee Abnormality Probabilities"
)

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=9,
)

plt.tight_layout()

viz1_path = os.path.join(
    OUTPUT_DIR,
    "prediction_distribution.png",
)

plt.savefig(
    viz1_path,
    dpi=180,
    bbox_inches="tight",
)

plt.show()

plt.close()

print(
    f"Saved: {viz1_path}"
)

# ============================================================
# VISUALIZATION 2
# Prediction Heatmap
# ============================================================

print()
print("=" * 70)
print("VISUALIZATION 2 — PREDICTION HEATMAP")
print("=" * 70)

# ------------------------------------------------------------
# Number of studies to display
# ------------------------------------------------------------

n_show = min(
    30,
    len(submission),
)

# ------------------------------------------------------------
# Extract prediction values
# ------------------------------------------------------------

heatmap_data = (
    submission[LABELS]
    .iloc[:n_show]
    .apply(
        pd.to_numeric,
        errors="coerce",
    )
    .fillna(0.0)
    .values
)

# ------------------------------------------------------------
# Extract study IDs
# ------------------------------------------------------------

study_ids = (
    submission[id_col]
    .iloc[:n_show]
    .astype(str)
    .tolist()
)

# ============================================================
# CREATE HEATMAP
# ============================================================

plt.figure(
    figsize=(14, 8)
)

image = plt.imshow(
    heatmap_data,
    aspect="auto",
    interpolation="nearest",
)

plt.colorbar(
    image,
    label="Predicted probability",
)

plt.xticks(
    range(len(LABELS)),
    LABELS,
    rotation=45,
    ha="right",
)

plt.yticks(
    range(n_show),
    study_ids,
)

plt.xlabel(
    "Knee abnormality"
)

plt.ylabel(
    "Study ID"
)

plt.title(
    "Knee Abnormality Prediction Heatmap"
)

plt.tight_layout()

viz2_path = os.path.join(
    OUTPUT_DIR,
    "prediction_heatmap.png",
)

plt.savefig(
    viz2_path,
    dpi=180,
    bbox_inches="tight",
)

plt.show()

plt.close()

print(
    f"Saved: {viz2_path}"
)

# ============================================================
# VISUALIZATION 3
# Mean Prediction by Abnormality
# ============================================================

print()
print("=" * 70)
print("VISUALIZATION 3 — MEAN PREDICTION BY LABEL")
print("=" * 70)

mean_predictions = (
    submission[LABELS]
    .apply(
        pd.to_numeric,
        errors="coerce",
    )
    .mean()
    .sort_values(
        ascending=False
    )
)

plt.figure(
    figsize=(12, 6)
)

bars = plt.bar(
    mean_predictions.index,
    mean_predictions.values,
)

plt.xlabel(
    "Knee abnormality"
)

plt.ylabel(
    "Mean predicted probability"
)

plt.title(
    "Mean Predicted Probability by Knee Abnormality"
)

plt.xticks(
    rotation=45,
    ha="right",
)

# ------------------------------------------------------------
# Print values above bars
# ------------------------------------------------------------

for bar, value in zip(
    bars,
    mean_predictions.values,
):

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()

viz3_path = os.path.join(
    OUTPUT_DIR,
    "mean_prediction_by_label.png",
)

plt.savefig(
    viz3_path,
    dpi=180,
    bbox_inches="tight",
)

plt.show()

plt.close()

print(
    f"Saved: {viz3_path}"
)

# ============================================================
# FINAL OUTPUT SUMMARY
# ============================================================

print()
print("=" * 70)
print("FINAL OUTPUTS")
print("=" * 70)

print()
print("1. Submission:")
print(f"   {OUTPUT_FILE}")

print()
print("2. Lookup cache:")
print(f"   {CACHE_FILE}")

print()
print("3. Prediction distribution:")
print(f"   {viz1_path}")

print()
print("4. Prediction heatmap:")
print(f"   {viz2_path}")

print()
print("5. Mean prediction by label:")
print(f"   {viz3_path}")

print()
print("=" * 70)
print("VISUALIZATION COMPLETE")
print("=" * 70)
```

```
======================================================================
FINAL IMAGE VISUALIZATIONS
======================================================================

Submission rows : 3
ID column       : StudyInstanceUID
Prediction cols : 12

======================================================================
VISUALIZATION 1 — PREDICTION DISTRIBUTION
======================================================================
```

![](https://www.kaggleusercontent.com/kf/349728193/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..wgN7y7U23OrR66nspgdf8A._Raq36lErUq_N5oO70cJDfI-8nHKLVTHu0d4be8JNdO3MSl4rY0plW5S3STzYpBi3JzjPUnjgYNRBfwGVBMeIQ5r1rHGyBQ5YJcZDJIXB4oxSJLtCj3HFo6O_IIg5tzUXSpcc1i0CJvpSv7qM_ZQJj5Ib-57T93a1W_2aHmjM4QN6HS5w0XkvrwYle-oaHbIwgv62JniVRYLd8yHsaMX5BQGO0twSrSFbYM8A8_GgZWf1K-td_kFO2w76e0rLLWty84i8SWx4IkgEQb4FWDS9N9OCo6sxww8ceDiDq6mU4pvITuao1yHQz4XlrkZbIqOA1HqiLrVnrGo70MpP-1BzqyoIMMm1hNHTQMO5KzyBpxwvWD4loy2-uU49vjafp2BlfktC6KsMWz6T1d7ZIus4QmrGXdfH5eqC-Ma6nQRE6-p0kYr3z0bouHnhSUg_bhLGlc9RT9JwkikQm__WjwzkiqxR9U-VRyv65zBF-19KFcFCHwANP3A7AEN9YSIPmVXmU9JEqQC1Xp2aSaOAKC-pnFfRddty76Bmn9V3z8-AgYpTt1Z8chG63-3XRC4C4bJ_p5584_FkGxpZRvqc0aXabq6A_xvSuIRco4oBh_jCyQzZHKod6dWQL2GJV0vOctvs5UzW_D9qM-2Ipt4B07zpQ.nqtO89rx33cxBDRny-Tszg/__results___files/__results___5_1.png)

```
Saved: /kaggle/working/prediction_distribution.png

======================================================================
VISUALIZATION 2 — PREDICTION HEATMAP
======================================================================
```

![](https://www.kaggleusercontent.com/kf/349728193/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..wgN7y7U23OrR66nspgdf8A._Raq36lErUq_N5oO70cJDfI-8nHKLVTHu0d4be8JNdO3MSl4rY0plW5S3STzYpBi3JzjPUnjgYNRBfwGVBMeIQ5r1rHGyBQ5YJcZDJIXB4oxSJLtCj3HFo6O_IIg5tzUXSpcc1i0CJvpSv7qM_ZQJj5Ib-57T93a1W_2aHmjM4QN6HS5w0XkvrwYle-oaHbIwgv62JniVRYLd8yHsaMX5BQGO0twSrSFbYM8A8_GgZWf1K-td_kFO2w76e0rLLWty84i8SWx4IkgEQb4FWDS9N9OCo6sxww8ceDiDq6mU4pvITuao1yHQz4XlrkZbIqOA1HqiLrVnrGo70MpP-1BzqyoIMMm1hNHTQMO5KzyBpxwvWD4loy2-uU49vjafp2BlfktC6KsMWz6T1d7ZIus4QmrGXdfH5eqC-Ma6nQRE6-p0kYr3z0bouHnhSUg_bhLGlc9RT9JwkikQm__WjwzkiqxR9U-VRyv65zBF-19KFcFCHwANP3A7AEN9YSIPmVXmU9JEqQC1Xp2aSaOAKC-pnFfRddty76Bmn9V3z8-AgYpTt1Z8chG63-3XRC4C4bJ_p5584_FkGxpZRvqc0aXabq6A_xvSuIRco4oBh_jCyQzZHKod6dWQL2GJV0vOctvs5UzW_D9qM-2Ipt4B07zpQ.nqtO89rx33cxBDRny-Tszg/__results___files/__results___5_3.png)

```
Saved: /kaggle/working/prediction_heatmap.png

======================================================================
VISUALIZATION 3 — MEAN PREDICTION BY LABEL
======================================================================
```

![](https://www.kaggleusercontent.com/kf/349728193/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..wgN7y7U23OrR66nspgdf8A._Raq36lErUq_N5oO70cJDfI-8nHKLVTHu0d4be8JNdO3MSl4rY0plW5S3STzYpBi3JzjPUnjgYNRBfwGVBMeIQ5r1rHGyBQ5YJcZDJIXB4oxSJLtCj3HFo6O_IIg5tzUXSpcc1i0CJvpSv7qM_ZQJj5Ib-57T93a1W_2aHmjM4QN6HS5w0XkvrwYle-oaHbIwgv62JniVRYLd8yHsaMX5BQGO0twSrSFbYM8A8_GgZWf1K-td_kFO2w76e0rLLWty84i8SWx4IkgEQb4FWDS9N9OCo6sxww8ceDiDq6mU4pvITuao1yHQz4XlrkZbIqOA1HqiLrVnrGo70MpP-1BzqyoIMMm1hNHTQMO5KzyBpxwvWD4loy2-uU49vjafp2BlfktC6KsMWz6T1d7ZIus4QmrGXdfH5eqC-Ma6nQRE6-p0kYr3z0bouHnhSUg_bhLGlc9RT9JwkikQm__WjwzkiqxR9U-VRyv65zBF-19KFcFCHwANP3A7AEN9YSIPmVXmU9JEqQC1Xp2aSaOAKC-pnFfRddty76Bmn9V3z8-AgYpTt1Z8chG63-3XRC4C4bJ_p5584_FkGxpZRvqc0aXabq6A_xvSuIRco4oBh_jCyQzZHKod6dWQL2GJV0vOctvs5UzW_D9qM-2Ipt4B07zpQ.nqtO89rx33cxBDRny-Tszg/__results___files/__results___5_5.png)

```
Saved: /kaggle/working/mean_prediction_by_label.png

======================================================================
FINAL OUTPUTS
======================================================================

1. Submission:
   /kaggle/working/submission.csv

2. Lookup cache:
   /kaggle/working/rsna_knee_study_lookup_cache_v6.pkl

3. Prediction distribution:
   /kaggle/working/prediction_distribution.png

4. Prediction heatmap:
   /kaggle/working/prediction_heatmap.png

5. Mean prediction by label:
   /kaggle/working/mean_prediction_by_label.png

======================================================================
VISUALIZATION COMPLETE
======================================================================
```

In \[ \]:

linkcode

```

```

## License

This Notebook has been released under the [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0) open source license.

## Continue exploring

- ![](https://www.kaggle.com/static/images/kernel/viewer/input_light.svg)







Input

1 file




arrow\_right\_alt

- ![](https://www.kaggle.com/static/images/kernel/viewer/output_light.svg)







Output

5 files




arrow\_right\_alt

- ![](https://www.kaggle.com/static/images/kernel/viewer/logs_light.svg)







Logs

614.9 second run - successful




arrow\_right\_alt

- ![](https://www.kaggle.com/static/images/kernel/viewer/comments_light.svg)







Comments

0 comments




arrow\_right\_alt