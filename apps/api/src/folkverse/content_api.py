from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from folkverse.content import (
    approved,
    media_eligible,
    passage_eligible,
    published_artifacts,
    published_exhibits,
)
from folkverse.content_models import (
    Claim,
    ClaimEvidence,
    Exhibit,
    ExhibitRegion,
    Media,
    Passage,
    Region,
    Review,
    Source,
)
from folkverse.errors import ApiError

router = APIRouter(prefix="/api/v1")
Locale = Literal["en", "zh-CN"]


class ReviewInfo(BaseModel):
    reviewer: str
    reviewed_at: datetime
    notes: str
    kind: Literal["editorial"] = "editorial"


class RegionCard(BaseModel):
    id: str
    name: str
    approved_geometry_ref: str | None


class RegionList(BaseModel):
    items: list[RegionCard]


class ExhibitCard(BaseModel):
    id: str
    title: str
    summary: str
    locale: Locale
    themes: list[str]
    estimated_minutes: int
    region_ids: list[str]


class ExhibitPage(BaseModel):
    items: list[ExhibitCard]
    next_cursor: str | None
    total: int


class PassageCard(BaseModel):
    id: str
    text: str
    language: str
    locator: str
    rights_basis: str
    review: ReviewInfo


class SourceCard(BaseModel):
    id: str
    institution: str
    title: str
    canonical_url: str
    fetched_at: datetime
    raw_hash: str
    rights_basis: str
    review: ReviewInfo
    passages: list[PassageCard]


class SourceList(BaseModel):
    items: list[SourceCard]


class ClaimCard(BaseModel):
    id: str
    text: str
    passage_ids: list[str]


class ExhibitDetail(ExhibitCard):
    review: ReviewInfo
    claims: list[ClaimCard]
    sources: list[SourceCard]


class ArtifactCard(BaseModel):
    id: str
    title: str
    catalog_date: str
    medium: str
    origin: dict[str, str]
    current_location: str
    source_id: str
    image_hashes: list[str]


class ArtifactList(BaseModel):
    items: list[ArtifactCard]


def review_info(db: Session, review_id: str | None) -> ReviewInfo:
    record = db.get(Review, review_id)
    if record is None:
        raise ApiError(404, "not_found", "Reviewed record not found.")
    return ReviewInfo(reviewer=record.reviewer, reviewed_at=record.reviewed_at, notes=record.notes)


def card(db: Session, row: Exhibit, locale: Locale) -> ExhibitCard:
    return ExhibitCard(
        id=row.id,
        title=row.title[locale],
        summary=row.summary[locale],
        locale=locale,
        themes=row.themes,
        estimated_minutes=row.estimated_minutes,
        region_ids=list(
            db.scalars(select(ExhibitRegion.region_id).where(ExhibitRegion.exhibit_id == row.id))
        ),
    )


def source_card(db: Session, row: Source) -> SourceCard:
    return SourceCard(
        id=row.id,
        institution=row.institution,
        title=row.title,
        canonical_url=row.canonical_url,
        fetched_at=row.fetched_at,
        raw_hash=row.raw_hash,
        rights_basis=row.rights_basis,
        review=review_info(db, row.review_id),
        passages=[
            PassageCard(
                id=p.id,
                text=p.text,
                language=p.language,
                locator=p.locator,
                rights_basis=p.rights_basis,
                review=review_info(db, p.review_id),
            )
            for p in db.scalars(select(Passage).where(Passage.source_id == row.id))
            if passage_eligible(db, p)
        ],
    )


@router.get("/regions", response_model=RegionList, operation_id="regions")
def regions(request: Request, locale: Locale = "en") -> RegionList:
    with Session(request.app.state.engine) as db:
        eligible_ids = {
            rid for e in published_exhibits(db) for rid in card(db, e, locale).region_ids
        }
        return RegionList(
            items=[
                RegionCard(
                    id=r.id, name=r.names[locale], approved_geometry_ref=r.approved_geometry_ref
                )
                for r in db.scalars(select(Region).order_by(Region.id))
                if r.id in eligible_ids and approved(db, r)
            ]
        )


@router.get("/exhibits", response_model=ExhibitPage, operation_id="exhibits")
def exhibits(
    request: Request,
    locale: Locale = "en",
    region_id: str | None = None,
    themes: str | None = None,
    q: str = Query(default="", max_length=200),
    cursor: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=12, ge=1, le=50),
) -> ExhibitPage:
    with Session(request.app.state.engine) as db:
        items = [card(db, e, locale) for e in published_exhibits(db)]
        items = [
            e
            for e in items
            if (not region_id or region_id in e.region_ids)
            and (not themes or themes in e.themes)
            and q.casefold() in f"{e.title} {e.summary}".casefold()
        ]
        total = len(items)
        after = [e for e in items if not cursor or e.id > cursor]
        return ExhibitPage(
            items=after[:limit],
            total=total,
            next_cursor=after[limit - 1].id if len(after) > limit else None,
        )


@router.get("/exhibits/{identifier}", response_model=ExhibitDetail, operation_id="exhibit")
def exhibit(request: Request, identifier: str, locale: Locale = "en") -> ExhibitDetail:
    with Session(request.app.state.engine) as db:
        row = next((e for e in published_exhibits(db) if e.id == identifier), None)
        if row is None:
            raise ApiError(404, "not_found", "Published exhibit not found.")
        claims = list(db.scalars(select(Claim).where(Claim.exhibit_id == row.id)))
        source_ids: set[str] = set()
        cards = []
        for claim in claims:
            passages = list(
                db.scalars(
                    select(Passage).join(ClaimEvidence).where(ClaimEvidence.claim_id == claim.id)
                )
            )
            source_ids.update(p.source_id for p in passages)
            cards.append(
                ClaimCard(id=claim.id, text=claim.text, passage_ids=[p.id for p in passages])
            )
        sources = list(
            db.scalars(select(Source).where(Source.id.in_(source_ids)).order_by(Source.id))
        )
        return ExhibitDetail(
            **card(db, row, locale).model_dump(),
            review=review_info(db, row.review_id),
            claims=cards,
            sources=[source_card(db, s) for s in sources],
        )


@router.get("/sources", response_model=SourceList, operation_id="sources")
def sources(request: Request) -> SourceList:
    with Session(request.app.state.engine) as db:
        return SourceList(
            items=[
                source_card(db, s)
                for s in db.scalars(select(Source).order_by(Source.id))
                if approved(db, s)
            ]
        )


@router.get("/sources/{identifier}", response_model=SourceCard, operation_id="source")
def source(request: Request, identifier: str) -> SourceCard:
    with Session(request.app.state.engine) as db:
        row = db.get(Source, identifier)
        if row is None or not approved(db, row):
            raise ApiError(404, "not_found", "Published source not found.")
        return source_card(db, row)


@router.get("/artifacts", response_model=ArtifactList, operation_id="artifacts")
def artifacts(request: Request) -> ArtifactList:
    with Session(request.app.state.engine) as db:
        return ArtifactList(
            items=[
                ArtifactCard(
                    id=a.id,
                    title=a.catalog_title,
                    catalog_date=a.catalog_date,
                    medium=a.medium,
                    origin=a.origin,
                    current_location=a.current_location,
                    source_id=a.source_id,
                    image_hashes=[
                        m.hash
                        for m in db.scalars(select(Media).where(Media.artifact_id == a.id))
                        if m.hash and media_eligible(db, m)
                    ],
                )
                for a in published_artifacts(db)
            ]
        )
