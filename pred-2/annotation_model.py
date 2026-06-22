"""Pydantic model for one thread annotation. Single source of truth for the
JSONL the annotator subagents write; imported by validate_annotations.py (the
per-shard gate) and merge_annotations.py (the final build). See ANNOTATION_SCHEMA.md.
"""
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

CATEGORIES = ("deal-contract", "trading-risk", "legal-regulatory", "california-energy",
              "scheduling-logistics", "report-fyi", "internal-admin", "social")

Category = Literal["deal-contract", "trading-risk", "legal-regulatory", "california-energy",
                   "scheduling-logistics", "report-fyi", "internal-admin", "social"]
Outcome = Literal["resolved", "open", "unknown"]
Confidence = Literal["high", "medium", "low"]


class Participant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ref: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    is_executive: Optional[bool] = None


class Annotation(BaseModel):
    # extra="ignore": a stray field never breaks the build, but every declared
    # field is type- and enum-checked, so the parquet schema stays fixed.
    model_config = ConfigDict(extra="ignore")
    thread_id: int
    category: Category
    secondary: Optional[Category] = None
    one_line: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    has_request: bool
    has_decision: bool
    outcome: Outcome
    participants: List[Participant] = []
    entities: List[str] = []
    topics: List[str] = []
    confidence: Confidence
