from pydantic import BaseModel, Field


class Author(BaseModel):
    name: str
    affiliation: str = ""


class Manuscript(BaseModel):
    title: str = "無題"
    authors: list[Author] = Field(default_factory=list)
    abstract: str = ""
    body_markdown: str = ""
    bibliography: str = ""
    warnings: list[str] = Field(default_factory=list)


class PdfRequest(BaseModel):
    manuscript: Manuscript
    font_size: float = Field(default=10.5, ge=8, le=14)
    margin_mm: int = Field(default=22, ge=15, le=35)
