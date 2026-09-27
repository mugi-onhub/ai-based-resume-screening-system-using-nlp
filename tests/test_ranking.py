from src.ranking import build_ranking_table, shortlist


def test_ranking_sorted_descending():
    df = build_ranking_table(
        filenames=["a.pdf", "b.pdf"],
        tfidf_pct=[50, 80],
        semantic_pct=[50, 80],
        bert_pct=[50, 80],
        final_scores=[50, 80],
        match_labels=["Moderate match", "Strong match"],
    )
    assert df.iloc[0]["Candidate File"] == "b.pdf"
    assert list(df["Rank"]) == [1, 2]


def test_shortlist_filters_by_threshold():
    df = build_ranking_table(
        filenames=["a.pdf", "b.pdf"],
        tfidf_pct=[50, 80],
        semantic_pct=[50, 80],
        bert_pct=[50, 80],
        final_scores=[40, 80],
        match_labels=["Low match", "Strong match"],
    )
    short = shortlist(df, threshold=60)
    assert len(short) == 1
    assert short.iloc[0]["Candidate File"] == "b.pdf"
