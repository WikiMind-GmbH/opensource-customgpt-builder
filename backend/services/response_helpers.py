import mammoth
from pathlib import Path
from typing import Iterable


from dataclasses import dataclass
from typing import List
import math

import tiktoken

embedding_context_size = 8_192

model_context_window_dict = {
    "gpt-4o": 128_000,
    "gpt-4.1": 1_000_000,
    "gpt-4.1-mini": 1_000_000,
}

system_message_smallgpt_with_placeholders = """Anweisungen:

Beantworte die folgende Frage ausschließlich auf Grundlage der Referenzdokumente:

{reference_documents}

Verwende nur Informationen, die ausdrücklich in diesen Dokumenten enthalten sind.
Wenn die benötigte Information nicht in den Referenzdokumenten vorhanden ist, gib an, dass dazu keine Informationen in den Referenzdokumenten vorliegen.

Mache keine Annahmen und verwende kein externes Wissen.
"""


def convert_docs_to_markdown(
    doc_paths: Iterable[str | Path],
    header_template: str = "**Reference Document {n}**\n\n",
) -> str:
    """
    Convert multiple .docx files to a single Markdown string,
    inserting a numbered heading before each one.

    Parameters
    ----------
    doc_paths : iterable of str | Path
        Paths to .docx files.
    header_template : str, optional
        Template for the heading placed before each document’s content.
        Use `{n}` in the template to insert the 1-based index.

    Returns
    -------
    str
        Combined Markdown for all documents.
    """
    sections: list[str] = []

    for idx, path in enumerate(doc_paths, start=1):
        with open(path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            # Clean up Markdown quirks
            md = result.value.replace("\\", "").replace("__", "**").strip()

        heading = header_template.format(n=idx)
        sections.append(f"{heading}{md}")

    return "\n\n".join(sections)


## Example useage
# files = [
#    "HIG-Bot_call.docx",
# ]
# combined_reference_documents_in_md = convert_docs_to_markdown(files)
# print(combined_reference_documents_in_md)


def convert_docs_to_markdown_list(
    doc_paths: Iterable[str | Path],
) -> list[str]:
    """
    Convert multiple .docx files to a list of Markdown strings,
    without any added heading or prefix.

    Parameters
    ----------
    doc_paths : iterable of str | Path
        Paths to .docx files.

    Returns
    -------
    list of str
        Markdown strings, one per document.
    """
    markdown_list = []

    for path in doc_paths:
        with open(path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            # Clean up Markdown quirks
            md = result.value.replace("\\", "").replace("__", "**").strip()

        markdown_list.append(md)

    return markdown_list


## Example usage
# markdown_docs = convert_docs_to_markdown_list(files)


# ── 1.  Dataclass to hold chunk + metadata ─────────────────────────────────────
@dataclass
class DocumentChunk:
    doc_id: int  # index of the source string in the input list
    chunk_id: int  # 0-based position within its document
    token_start: int  # token offset (inclusive)
    token_end: int  # token offset (exclusive)
    text: str  # decoded text of this chunk


# ── 2.  Bucketizer with minimal-overlap logic (token based) ───────────────────
def bucketize_strings_with_overlap(
    strings: List[str],
    bucket_size: int = 8_196,
    encoding_name: str | None = None,
) -> List[DocumentChunk]:
    """
    Split each string into the *fewest* overlapping token buckets of `bucket_size`
    and return them as DocumentChunk objects that track origin metadata.

    Rules (token-level)
    -------------------
    • If #tokens ≤ bucket_size → one chunk (no padding)
    • Else → k = ceil(#tokens / bucket_size) chunks
      – first starts at 0
      – last ends at #tokens
      – intermediate starts evenly spaced to minimise count/overlap
    """
    enc = (
        tiktoken.get_encoding(encoding_name)
        if encoding_name
        else tiktoken.encoding_for_model("gpt-4o-mini")
    )

    chunks: List[DocumentChunk] = []

    for doc_idx, s in enumerate(strings):
        toks = enc.encode(s)
        n = len(toks)

        # ---- Case 1: fits in one bucket --------------------------------------
        if n <= bucket_size:
            chunk_text = enc.decode(toks)
            chunks.append(
                DocumentChunk(
                    doc_id=doc_idx,
                    chunk_id=0,
                    token_start=0,
                    token_end=n,
                    text=chunk_text,
                )
            )
            continue

        # ---- Case 2: needs ≥ 2 buckets ---------------------------------------
        k = math.ceil(n / bucket_size)  # minimal number of buckets
        step = (n - bucket_size) / (k - 1)  # optimal stride between starts

        starts = [int(round(i * step)) for i in range(k - 1)]
        starts.append(n - bucket_size)  # anchor last bucket

        for chunk_idx, start in enumerate(starts):
            end = start + bucket_size
            chunk_text = enc.decode(toks[start:end])
            chunks.append(
                DocumentChunk(
                    doc_id=doc_idx,
                    chunk_id=chunk_idx,
                    token_start=start,
                    token_end=end,
                    text=chunk_text,
                )
            )

    return chunks
