"""
Nova Engine — saas/tenant_store.py

Tenant-isolated read access to the parent's exported training dataset.

This is the hard isolation boundary for the SaaS child: a store is BOUND to one
tenant_id at construction, and every read is scoped to that tenant. The boundary
is fail-closed — a record without a tenant_id, or one belonging to a different
tenant, raises rather than leaking. No customer's data can enter another
tenant's model context.
"""
from __future__ import annotations

import json
from typing import Optional


class TenantIsolationError(RuntimeError):
    """Raised when a cross-tenant or untagged record is encountered."""


class TenantTrainingStore:
    """Read-only, single-tenant view over parent training records.

    Each record is a dict as produced by `Ledger.training_samples()` /
    `export_training_jsonl()`, augmented with a `tenant_id`.
    """

    def __init__(self, tenant_id: str, records: list[dict], *, stamp: bool = False):
        """Bind a store to one tenant.

        Args:
            tenant_id: the only tenant this store will ever serve.
            records: training records (dicts).
            stamp: if True, assign this tenant_id to records that lack one
                (used when ingesting a single operator's export, which is by
                definition that tenant's data). If False, every record MUST
                already carry a matching tenant_id or construction fails.
        """
        if not tenant_id:
            raise TenantIsolationError("tenant_id is required")
        self.tenant_id = tenant_id
        self._records: list[dict] = []
        for r in records:
            rid = r.get("tenant_id")
            if rid is None:
                if not stamp:
                    raise TenantIsolationError(
                        "record missing tenant_id (fail-closed); pass stamp=True "
                        "only when ingesting a single operator's own export")
                r = {**r, "tenant_id": tenant_id}
            elif rid != tenant_id:
                raise TenantIsolationError(
                    f"cross-tenant record: {rid!r} in store for {tenant_id!r}")
            self._records.append(r)

    @classmethod
    def from_parent_export(cls, path: str, tenant_id: str) -> "TenantTrainingStore":
        """Load a parent's JSONL export and bind it to one tenant.

        A parent export belongs wholly to one operator, so untagged rows are
        stamped with this tenant_id.
        """
        records = []
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return cls(tenant_id, records, stamp=True)

    def samples(self, *, book_id: Optional[str] = None,
                acted_only: bool = False, with_outcome: bool = False) -> list[dict]:
        """Return this tenant's records, optionally filtered.

        Args:
            book_id: restrict to one book.
            acted_only: only decisions that resulted in a trade.
            with_outcome: only records whose trade outcome has been backfilled.
        """
        out = []
        for r in self._records:
            if book_id is not None and r.get("book_id") != book_id:
                continue
            if acted_only and not r.get("acted"):
                continue
            if with_outcome and r.get("realized_pnl") is None:
                continue
            out.append(r)
        return out

    def __len__(self) -> int:
        return len(self._records)
