"""Offline tests for the local-only eBird sampling denominator pilot.

Run:
  PYTHONPATH=. python wildlifestats/_pipeline/ebird_sampling/test_pilot.py
"""

from __future__ import annotations

import gzip
import io
import sys
import tarfile
import tempfile
import traceback
from pathlib import Path

from wildlifestats._pipeline.ebird_sampling import pilot

PASSED = 0
FAILED = 0


def case(name):
    def deco(fn):
        global PASSED, FAILED
        try:
            fn()
            PASSED += 1
            print(f"  PASS  {name}")
        except AssertionError as exc:
            FAILED += 1
            print(f"  FAIL  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            FAILED += 1
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")
            traceback.print_exc()
        return fn
    return deco


HEADER = (
    "LAST EDITED DATE\tCOUNTRY\tCOUNTRY CODE\tSTATE\tSTATE CODE\tCOUNTY\tCOUNTY CODE\t"
    "IBA CODE\tBCR CODE\tUSFWS CODE\tATLAS BLOCK\tLOCALITY\tLOCALITY ID\tLOCALITY TYPE\t"
    "LATITUDE\tLONGITUDE\tOBSERVATION DATE\tTIME OBSERVATIONS STARTED\tOBSERVER ID\t"
    "OBSERVER ORCID ID\tSAMPLING EVENT IDENTIFIER\tOBSERVATION TYPE\tPROTOCOL NAME\t"
    "PROTOCOL CODE\tPROJECT NAMES\tPROJECT IDENTIFIERS\tDURATION MINUTES\t"
    "EFFORT DISTANCE KM\tEFFORT AREA HA\tNUMBER OBSERVERS\tALL SPECIES REPORTED\t"
    "GROUP IDENTIFIER\tCHECKLIST COMMENTS\n"
)

ROWS = [
    "2025-01-08 00:00:00\tUnited States\tUS\tVirginia\tUS-VA\tAlbemarle\tUS-VA-003\t\t29\t\t\tYard\tL1\tP\t38.0\t-78.0\t2025-01-08\t08:00:00\tobs1\t\tS1\tStationary\tStationary\tP21\t\t\t15\t\t\t1\t1\t\t\n",
    "2025-01-09 00:00:00\tUnited States\tUS\tVirginia\tUS-VA\tAlbemarle\tUS-VA-003\t\t29\t\t\tTrail\tL2\tP\t38.0\t-78.0\t2025-01-09\t09:00:00\tobs2\t\tS2\tTraveling\tTraveling\tP22\t\t\t45\t1.5\t\t2\t1\t\t\n",
    "2025-01-10 00:00:00\tUnited States\tUS\tVirginia\tUS-VA\tAlbemarle\tUS-VA-003\t\t29\t\t\tArchive\tL3\tP\t38.0\t-78.0\t2025-01-10\t09:00:00\tobs3\t\tS3\tHistorical\tHistorical\tP62\t\t\t\t\t\t1\t1\t\t\n",
    "2025-01-10 00:00:00\tUnited States\tUS\tVirginia\tUS-VA\tAlbemarle\tUS-VA-003\t\t29\t\t\tSkip\tL4\tP\t38.0\t-78.0\t2025-01-10\t09:00:00\tobs4\t\tS4\tStationary\tStationary\tP21\t\t\t10\t\t\t1\t0\t\t\n",
    "2025-01-11 00:00:00\tUnited States\tUS\tMaryland\tUS-MD\tMontgomery\tUS-MD-031\t\t29\t\t\tOther\tL5\tP\t39.0\t-77.0\t2025-01-11\t10:00:00\tobs5\t\tS5\tStationary\tStationary\tP21\t\t\t12\t\t\t1\t1\t\t\n",
]


def _build_archive(path: Path, *, include_data_member: bool = True) -> None:
    body = HEADER + "".join(ROWS)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb") as gz:
        gz.write(body.encode("utf-8"))
    compressed_value = compressed.getvalue()

    with tarfile.open(path, "w") as tf:
        if include_data_member:
            data_info = tarfile.TarInfo(pilot.DATA_MEMBER)
            data_info.size = len(compressed_value)
            tf.addfile(data_info, io.BytesIO(compressed_value))

        for name, text in {
            pilot.CITATION_MEMBER: "eBird Basic Dataset. Version: EBD_relMay-2026.",
            pilot.TERMS_MEMBER: "Derived data must carry the same terms.",
            pilot.PROTOCOLS_MEMBER: "P21\tStationary\n",
        }.items():
            payload = text.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))


print("=" * 60)
print("ebird_sampling denominator pilot")
print("=" * 60)


@case("run_pilot filters to target state and complete checklists only")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        archive_path = tmp_path / "sample.tar"
        csv_path = tmp_path / "out.csv"
        provenance_path = tmp_path / "provenance.yml"
        _build_archive(archive_path)
        run = pilot.run_pilot(
            archive_path,
            state_code="US-VA",
            output_csv_path=csv_path,
            provenance_path=provenance_path,
        )
        assert run.rows_scanned == 5, run.rows_scanned
        assert run.retained_rows == 3, run.retained_rows
        assert run.output_rows == 3, run.output_rows
        csv_text = csv_path.read_text(encoding="utf-8")
        assert "US-VA-003" in csv_text
        assert "US-MD-031" not in csv_text
        assert "Traveling" in csv_text and "Historical" in csv_text
        assert "Derived data must carry the same terms." not in csv_text, "terms text should stay out of CSV"
        provenance = provenance_path.read_text(encoding="utf-8")
        assert "raw_row_redistribution_prohibited: true" in provenance
        assert "retained_complete_checklists: 3" in provenance


@case("require_archive_members rejects archive missing the gz payload")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        archive_path = Path(tmp) / "broken.tar"
        _build_archive(archive_path, include_data_member=False)
        try:
            pilot.run_pilot(archive_path)
            assert False, "expected missing-member failure"
        except ValueError as exc:
            assert pilot.DATA_MEMBER in str(exc)


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)

