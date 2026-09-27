"""Combines per-resume scores into a ranked, sortable table."""
import pandas as pd


def build_ranking_table(
    filenames: list[str],
    tfidf_pct,
    semantic_pct,
    bert_pct,
    final_scores,
    match_labels: list[str],
) -> pd.DataFrame:
    df = pd.DataFrame({
        "Candidate File": filenames,
        "Final Score": final_scores,
        "TF-IDF Score": tfidf_pct,
        "Semantic Score": semantic_pct,
        "BERT Score": bert_pct,
        "Match Category": match_labels,
    })
    df = df.sort_values("Final Score", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df


def shortlist(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    return df[df["Final Score"] >= threshold].reset_index(drop=True)
