"""
report.py
---------

Presentation-layer module: turns the numbers from
:mod:`weatherstats.stats` into a human-readable report. Kept separate so
that swapping the output format (plain text here, could be HTML/Markdown
later) never touches the statistics logic itself.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import pandas as pd

from .stats import descriptive_stats


def generate_summary_report(
    df: pd.DataFrame,
    columns: Optional[Sequence[str]] = None,
    title: str = "Weather Dataset Summary",
) -> Tuple[str, pd.DataFrame]:
    """
    Build a printable descriptive-statistics report for ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
    columns : sequence of str, optional
        Passed through to :func:`weatherstats.stats.descriptive_stats`.
    title : str
        Heading for the report.

    Returns
    -------
    (report_text, stats_table) : tuple[str, pandas.DataFrame]
        ``report_text`` is ready to ``print()``; ``stats_table`` is the
        underlying DataFrame in case the caller wants to export it
        (e.g. to CSV) instead of / in addition to printing it.
    """
    stats_table = descriptive_stats(df, columns=columns)

    lines = [title, "=" * len(title), "", f"Records analyzed: {len(df):,}", ""]
    lines.append(stats_table.round(2).to_string())
    report_text = "\n".join(lines)

    return report_text, stats_table
