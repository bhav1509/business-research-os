from pydantic import BaseModel, Field, field_validator


class ResearchAnalysis(BaseModel):

    demand_score: int = Field(ge=0, le=100)
    competition_score: int = Field(ge=0, le=100)
    profitability_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(ge=0, le=100)

    customer_segments: list[str]
    top_themes: list[str]

    evidence_for: list[str]
    evidence_against: list[str]

    risks: list[str]

    next_test: list[str]

    @field_validator("next_test", mode="before")
    @classmethod
    def normalize_next_test(cls, value):
        if isinstance(value, str):
            return [value]

        return value