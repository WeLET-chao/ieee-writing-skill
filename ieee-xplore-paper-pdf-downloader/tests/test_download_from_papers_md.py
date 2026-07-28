import tempfile
import unittest
from pathlib import Path
import sys
from unittest import mock

SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.download_from_papers_md import (
    PaperRecord,
    extract_article_number_from_url,
    extract_doi_from_url,
    finalize_record_paths,
    limit_pending_records,
    mark_existing_records,
    parse_papers_md,
    resolve_article_number,
    resolve_repo_root,
    summarize_records,
    target_path_for_paper,
)
from scripts.ieee_pdf_downloader import CONCURRENCY_ERROR_MARKER, response_indicates_concurrency_block
from scripts.acm_pdf_downloader import extract_acm_doi_from_url, is_acm_dl_link
from scripts.arxiv_pdf_downloader import extract_arxiv_id, is_arxiv_link


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
REPO_ROOT = SKILL_ROOT.parents[2]


class PapersMdBatchDownloadTests(unittest.TestCase):
    def test_response_indicates_concurrency_block(self):
        response = mock.Mock()
        response.url = "https://ieeexplore.ieee.org/document/123?reason=concurrency"
        response.status_code = 200
        response.headers = {"content-type": "text/html;charset=UTF-8"}
        response.text = ""
        self.assertTrue(response_indicates_concurrency_block(response))

    def test_concurrency_marker_constant(self):
        self.assertIn("CONCURRENCY", CONCURRENCY_ERROR_MARKER)

    def test_extract_article_number_from_document_url(self):
        self.assertEqual(
            extract_article_number_from_url("https://ieeexplore.ieee.org/document/11223063"),
            "11223063",
        )

    def test_extract_doi_from_searchresult_url(self):
        self.assertEqual(
            extract_doi_from_url(
                "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=10.1109/jssc.2025.3560578"
            ),
            "10.1109/jssc.2025.3560578",
        )

    def test_acm_link_detection_and_doi_extraction(self):
        url = "https://dl.acm.org/doi/pdf/10.1145/3676536.3676816"
        self.assertTrue(is_acm_dl_link(url))
        self.assertEqual(extract_acm_doi_from_url(url), "10.1145/3676536.3676816")

    def test_arxiv_link_detection_and_id_extraction(self):
        url = "https://arxiv.org/pdf/2406.18770"
        self.assertTrue(is_arxiv_link(url))
        self.assertEqual(extract_arxiv_id(url), "2406.18770")

    def test_target_path_for_nested_layout(self):
        path = target_path_for_paper(REPO_ROOT, "sar-adc-lab", "example-title", explicit_layout=True)
        self.assertTrue(str(path).endswith("sar-adc-lab/papers/example-title/paper.pdf"))

    def test_target_path_for_flat_layout(self):
        path = target_path_for_paper(REPO_ROOT, "cdac-lab", "example-title")
        self.assertTrue(str(path).endswith("cdac-lab/papers/example-title.pdf"))

    def test_parse_papers_md_extracts_flat_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage_dir = Path(tmpdir) / "stage"
            stage_dir.mkdir()
            path = FIXTURES_DIR / "flat-lab" / "docs" / "PAPERS.md"
            records = parse_papers_md(path, stage_dir, FIXTURES_DIR)

        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].lab_name, "flat-lab")
        self.assertEqual(records[0].article_number, "11111111")
        self.assertTrue(records[0].target_file.endswith(".pdf"))

    def test_parse_papers_md_extracts_nested_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage_dir = Path(tmpdir) / "stage"
            stage_dir.mkdir()
            path = FIXTURES_DIR / "nested-lab" / "docs" / "PAPERS.md"
            records = parse_papers_md(path, stage_dir, FIXTURES_DIR)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].lab_name, "nested-lab")
        self.assertTrue(records[0].target_file.endswith("nested-lab/papers/example-nested-paper/paper.pdf"))

    @mock.patch("scripts.download_from_papers_md.requests.get")
    def test_resolve_article_number_from_doi_redirect(self, mock_get):
        mock_get.return_value.url = "https://ieeexplore.ieee.org/document/12345678"
        mock_get.return_value.text = ""

        article_number, error = resolve_article_number(
            "https://doi.org/10.1109/example.2025.12345678",
            "https://doi.org/10.1109/example.2025.12345678",
        )

        self.assertEqual(article_number, "12345678")
        self.assertEqual(error, "")

    @mock.patch("scripts.download_from_papers_md.requests.get")
    def test_resolve_article_number_from_page_text(self, mock_get):
        mock_get.return_value.url = "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=10.1109/example"
        mock_get.return_value.text = '{"articleNumber":"87654321"}'

        article_number, error = resolve_article_number(
            "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=10.1109/example",
            "https://doi.org/10.1109/example",
        )

        self.assertEqual(article_number, "87654321")
        self.assertEqual(error, "")

    @mock.patch("scripts.download_from_papers_md.requests.get")
    def test_resolve_article_number_prefers_doi_for_searchresult_links(self, mock_get):
        mock_get.return_value.url = "https://ieeexplore.ieee.org/document/99887766"
        mock_get.return_value.text = ""

        article_number, error = resolve_article_number(
            "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=10.1109/example",
            "https://doi.org/10.1109/example",
        )

        self.assertEqual(article_number, "99887766")
        self.assertEqual(error, "")
        mock_get.assert_called_once_with(
            "https://doi.org/10.1109/example",
            headers=mock.ANY,
            timeout=30,
            allow_redirects=True,
        )

    def test_finalize_record_paths_disambiguates_collisions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage_dir = Path(tmpdir)
            base = PaperRecord(
                lab_name="cdac-lab",
                papers_md="cdac-lab/docs/PAPERS.md",
                title="Example",
                title_slug="example",
                doi="10.1109/example.1",
                doi_url="https://doi.org/10.1109/example.1",
                pdf_label="IEEE Xplore",
                pdf_source_link="https://ieeexplore.ieee.org/document/111",
                article_number="111",
                staging_file=str(stage_dir / "cdac-lab" / "example.pdf"),
                target_file=str(target_path_for_paper(REPO_ROOT, "cdac-lab", "example")),
            )
            other = PaperRecord(
                **{
                    **base.__dict__,
                    "doi": "10.1109/example.2",
                    "doi_url": "https://doi.org/10.1109/example.2",
                    "pdf_source_link": "https://ieeexplore.ieee.org/document/222",
                    "article_number": "222",
                }
            )

            finalized = finalize_record_paths([base, other], stage_dir, REPO_ROOT, explicit_layout=False)

        self.assertEqual(len({record.target_file for record in finalized}), 2)

    def test_resolve_repo_root_finds_circuit_work(self):
        circuit_work = Path(__file__).resolve().parents[4]
        repo_root = resolve_repo_root(str(circuit_work))
        self.assertTrue(list(repo_root.glob("*-lab/docs/PAPERS.md")))

    def test_limit_pending_records_caps_download_batch(self):
        records = [
            PaperRecord(
                lab_name="flat-lab",
                papers_md="flat-lab/docs/PAPERS.md",
                title=f"Paper {index}",
                title_slug=f"paper-{index}",
                doi=f"10.1109/example.{index}",
                doi_url=f"https://doi.org/10.1109/example.{index}",
                pdf_label="IEEE Xplore",
                pdf_source_link=f"https://ieeexplore.ieee.org/document/{index}",
                article_number=str(index),
                staging_file=f"/tmp/stage/flat-lab/paper-{index}.pdf",
                target_file=f"/tmp/repo/flat-lab/papers/paper-{index}.pdf",
            )
            for index in range(5)
        ]

        limited = limit_pending_records(records, 2)
        pending = [record for record in limited if record.status == "pending"]

        self.assertEqual(len(pending), 2)

    @mock.patch("scripts.download_from_papers_md.verify_pdf", return_value=True)
    def test_mark_existing_records_skips_valid_target_pdf(self, _mock_verify):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "cdac-lab" / "papers" / "example.pdf"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"%PDF-1.4\n% fake pdf for test\n")

            record = PaperRecord(
                lab_name="cdac-lab",
                papers_md="cdac-lab/docs/PAPERS.md",
                title="Example",
                title_slug="example",
                doi="10.1109/example.1",
                doi_url="https://doi.org/10.1109/example.1",
                pdf_label="IEEE Xplore",
                pdf_source_link="https://ieeexplore.ieee.org/document/111",
                article_number="111",
                staging_file=str(Path(tmpdir) / "stage" / "example.pdf"),
                target_file=str(target),
            )

            mark_existing_records([record])

        self.assertEqual(record.status, "existing")

    def test_summarize_records_marks_complete_when_nothing_pending(self):
        records = [
            PaperRecord(
                lab_name="flat-lab",
                papers_md="flat-lab/docs/PAPERS.md",
                title="Done",
                title_slug="done",
                doi="10.1109/example.1",
                doi_url="https://doi.org/10.1109/example.1",
                pdf_label="IEEE Xplore",
                pdf_source_link="https://ieeexplore.ieee.org/document/111",
                article_number="111",
                staging_file="/tmp/stage/done.pdf",
                target_file="/tmp/repo/done.pdf",
                status="existing",
            )
        ]

        summary = summarize_records(records)

        self.assertTrue(summary.complete)
        self.assertEqual(summary.pending, 0)

    def test_finalize_record_paths_marks_exact_duplicates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage_dir = Path(tmpdir)
            base = PaperRecord(
                lab_name="cdac-lab",
                papers_md="cdac-lab/docs/PAPERS.md",
                title="Example",
                title_slug="example",
                doi="10.1109/example.1",
                doi_url="https://doi.org/10.1109/example.1",
                pdf_label="IEEE Xplore",
                pdf_source_link="https://ieeexplore.ieee.org/document/111",
                article_number="111",
                staging_file=str(stage_dir / "cdac-lab" / "example.pdf"),
                target_file=str(target_path_for_paper(REPO_ROOT, "cdac-lab", "example")),
            )
            duplicate = PaperRecord(**base.__dict__)

            finalized = finalize_record_paths([base, duplicate], stage_dir, REPO_ROOT, explicit_layout=False)

        self.assertEqual(sorted(record.status for record in finalized), ["duplicate", "pending"])


if __name__ == "__main__":
    unittest.main()
