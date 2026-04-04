import re
import pandas as pd


def clean_rock_name(text):
    if pd.isna(text):
        return None

    text = str(text).strip().lower()
    text = text.replace("?", "")
    text = re.sub(r"\s+", " ", text)

    return text


def extract_rock_context(text):
    if text is None:
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
    if text is None:
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

    for base in bases:
        if base in text:
            return base

    return "other"


def assign_rock_group(base, context):
    volcanic = {"basalt", "basaltic andesite", "andesite", "dacite", "rhyolite"}
    plutonic = {
        "gabbro", "diorite", "quartz diorite", "granodiorite",
        "granite", "tonalite", "quartz monzodiorite",
        "quartz monzonite", "monzogranite", "granophyre", "aplite"
    }

    if "tuff" in context:
        return "pyroclastic"
    if "breccia" in context or base == "breccia":
        return "breccia"
    if base in volcanic and any(x in context for x in ["dike", "sill", "plug", "intrusion"]):
        return "subvolcanic"
    if base in volcanic:
        return "volcanic"
    if base in plutonic:
        return "plutonic"
    if base == "intrusion":
        return "ambiguous_intrusion"

    return "other"


def process_rock_names(df):
    df = df.copy()

    df["rock_name_clean"] = df["rock_name"].apply(clean_rock_name)
    df["rock_context"] = df["rock_name_clean"].apply(extract_rock_context)
    df["rock_base"] = df["rock_name_clean"].apply(extract_rock_base)

    df["rock_group"] = df.apply(
        lambda row: assign_rock_group(row["rock_base"], row["rock_context"]),
        axis=1
    )

    return df