import pandas as pd
from langchain_core.documents import Document


class CommunitiesReportsContextBuilder:
    def __init__(
        self,
        *,
        context_name: str = "Reports",
        column_delimiter: str = "|",
    ):
        self._context_name = context_name
        self._column_delimiter = column_delimiter

    def __call__(self, communities_reports: pd.DataFrame) -> Document:
        current_context_text = f"-----{self._context_name}-----" + "\n"
        header = ["id", "title", "content"]

        current_context_text += self._column_delimiter.join(header) + "\n"

        for report in communities_reports.itertuples():
            new_context = [
                str(report.community_id),
                report.title,
                report.content,
            ]

            new_context_text = self._column_delimiter.join(new_context) + "\n"
            current_context_text += new_context_text

        return Document(page_content=current_context_text)
