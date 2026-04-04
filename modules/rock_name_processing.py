import re
import pandas as pd


def clean_rock_name(text):
    if pd.isna(text):
        return "unknown"

    text = str(text).strip().lower()
    text = text.replace("?", "")
    text = re.sub(r"\s+", " ", text)

    if text == "":
        return "unknown"

    return text


def extract_rock_context(text):
    if pd.isna(text):
        return "unknown"

    text = str(text).strip().lower()

    if text == "":
        return "unknown"

    context_keywords = [
        "dike", "sill", "intrusion", "plug", "stock",
        "tuff", "breccia", "vitrophyre", "aphanite", "scoria"
    ]

    found = [kw for kw in context_keywords if kw in text]

    if not found:
        return "massive_or_unspecified"

    return ", ".join(found)


def extract_rock_base(text):
    if pd.isna(text):
        return "unknown"

    text = str(text).strip().lower()

    if text == "":
        return "unknown"

    bases = [
        "basaltic andesite",
        "quartz monzodiorite",
        "quartz monzonite",
        "quartz diorite",
        "micro-quartz diorite",
        "microdiorite",
        "granodiorite",
        "granophyre",
        "monzogranite",
        "granite",
        "tonalite",
        "rhyolite",
        "dacite",
        "andesite",
        "basalt",
        "diorite",
        "gabbro",
        "aplite",
        "breccia",
        "intrusion"
    ]

    # Casos compuestos
    if "diorite/andesite" in text:
        return "diorite_and_andesite"
    if "gabbro/diorite" in text:
        return "gabbro_and_diorite"
    if "microdiorite and dacite" in text:
        return "microdiorite_and_dacite"
    if "basaltic andesite/microdiorite" in text:
        return "basaltic_andesite_and_microdiorite"
    if "andesite/microdiorite" in text:
        return "andesite_and_microdiorite"

    for base in bases:
        if base in text:
            return base

    return "other"


def assign_rock_group(base, context):
    volcanic = {"basalt", "basaltic andesite", "andesite", "dacite", "rhyolite"}
    plutonic = {
        "gabbro", "diorite", "quartz diorite", "granodiorite",
        "granite", "tonalite", "quartz monzodiorite",
        "quartz monzonite", "monzogranite", "granophyre", "aplite",
        "microdiorite"
    }

    mixed = {
        "diorite_and_andesite",
        "gabbro_and_diorite",
        "microdiorite_and_dacite",
        "basaltic_andesite_and_microdiorite",
        "andesite_and_microdiorite"
    }

    if pd.isna(base):
        base = "unknown"
    if pd.isna(context):
        context = "unknown"

    base = str(base).strip().lower()
    context = str(context).strip().lower()

    if "tuff" in context:
        return "pyroclastic"
    if "breccia" in context or base == "breccia":
        return "breccia"
    if base in mixed:
        return "mixed_lithology"
    if base in volcanic and any(x in context for x in ["dike", "sill", "plug", "intrusion"]):
        return "subvolcanic"
    if base in volcanic:
        return "volcanic"
    if base in plutonic:
        return "plutonic"
    if base == "intrusion":
        return "ambiguous_intrusion"

    return "other"


def extract_observation(text):
    if pd.isna(text):
        return "none"

    text = str(text).strip().lower()

    observations = []

    if "altered" in text:
        observations.append("altered")
    if "silicic" in text:
        observations.append("silicic")
    if "unknown" in text:
        observations.append("unknown_source")

    if not observations:
        return "none"

    return ", ".join(observations)


def process_rock_names(df):
    df = df.copy()

    if "rock_name" not in df.columns:
        return df

    df["rock_name_clean"] = df["rock_name"].apply(clean_rock_name)
    df["rock_context"] = df["rock_name_clean"].apply(extract_rock_context)
    df["rock_base"] = df["rock_name_clean"].apply(extract_rock_base)
    df["rock_observation"] = df["rock_name_clean"].apply(extract_observation)

    df["rock_group"] = df.apply(
        lambda row: assign_rock_group(row["rock_base"], row["rock_context"]),
        axis=1
    )

    return df