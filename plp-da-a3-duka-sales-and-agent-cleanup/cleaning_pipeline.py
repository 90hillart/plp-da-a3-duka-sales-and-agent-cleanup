"""Reusable, auditable cleaning pipeline for mobile-money agent transactions."""
import numpy as np
import pandas as pd


def clean_agent_data(txns, agents):
    """
    Clean mobile-money transactions and enrich them with agent counties.

    Rules:
    - Remove duplicate txn_id records, keeping the first occurrence.
    - Normalise transaction types to Deposit / Withdrawal; discard unknown labels.
    - Parse amount as numeric; retain an amount_imputed flag and impute invalid
      amounts with the median of valid amounts (documented, reproducible baseline).
    - Parse mixed ISO and slash-separated dates.
    - Flag IQR outliers without deleting them.
    - Left-join the agent register so unknown agents remain visible with missing county.

    Returns
    -------
    clean_df : pandas.DataFrame
        Cleaned transactions, including county and quality flags.
    log : pandas.DataFrame
        Cleaning action, affected row count and details.
    """
    work = txns.copy()
    log_rows = []

    before = len(work)
    work = work.drop_duplicates(subset="txn_id", keep="first").copy()
    log_rows.append({"step": "Remove duplicate transactions",
                     "rows_affected": before - len(work),
                     "detail": "Duplicate txn_id values; first record retained."})

    raw_type = work["txn_type"].astype("string").str.strip().str.lower()
    type_map = {"deposit": "Deposit", "withdrawal": "Withdrawal"}
    mapped = raw_type.map(type_map)
    invalid_type = mapped.isna()
    log_rows.append({"step": "Standardise txn_type",
                     "rows_affected": int(invalid_type.sum()),
                     "detail": "Case/whitespace normalised; unrecognised labels excluded."})
    work = work.loc[~invalid_type].copy()
    work["txn_type"] = mapped.loc[~invalid_type].values

    raw_amount = work["amount"].replace(r"^\s*$", np.nan, regex=True)
    numeric_amount = pd.to_numeric(raw_amount, errors="coerce")
    amount_imputed = numeric_amount.isna()
    median_amount = numeric_amount.median()
    if pd.isna(median_amount):
        raise ValueError("No valid numeric amounts available for median imputation.")
    work["amount_imputed"] = amount_imputed.astype(bool)
    log_rows.append({"step": "Impute missing/invalid amount",
                     "rows_affected": int(amount_imputed.sum()),
                     "detail": f"Missing/invalid amounts replaced with median KES {median_amount:.2f}."})
    work["amount"] = numeric_amount.fillna(median_amount).astype(float)

    date_text = work["txn_date"].astype("string").str.strip().str.replace("/", "-", regex=False)
    parsed_dates = pd.to_datetime(date_text, errors="coerce", format="%Y-%m-%d")
    bad_dates = parsed_dates.isna()
    log_rows.append({"step": "Parse txn_date",
                     "rows_affected": int(bad_dates.sum()),
                     "detail": "Slash-separated dates normalised to ISO before parsing."})
    work["txn_date"] = parsed_dates
    work = work.loc[work["txn_date"].notna()].copy()
    work["txn_date"] = work["txn_date"].dt.strftime("%Y-%m-%d")

    q1, q3 = work["amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    work["is_outlier"] = (work["amount"] < lower) | (work["amount"] > upper)
    log_rows.append({"step": "Flag IQR outliers",
                     "rows_affected": int(work["is_outlier"].sum()),
                     "detail": f"Bounds: KES {lower:.2f} to KES {upper:.2f}; retained for review."})

    agents_copy = agents.copy()
    merged = work.merge(agents_copy[["agent_id", "county"]], on="agent_id",
                        how="left", validate="many_to_one", indicator=True)
    unknown = merged["_merge"].eq("left_only")
    log_rows.append({"step": "Merge agent register",
                     "rows_affected": int(unknown.sum()),
                     "detail": "Left join preserves transactions with unknown agent IDs."})
    merged = merged.drop(columns="_merge")
    merged["txn_date"] = pd.to_datetime(merged["txn_date"]).dt.strftime("%Y-%m-%d")
    clean_df = merged.reset_index(drop=True)
    log = pd.DataFrame(log_rows)
    return clean_df, log
