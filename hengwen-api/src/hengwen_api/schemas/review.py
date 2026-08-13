from pydantic import Field

from hengwen_api.schemas.common import CamelModel


class ReviewSettingsCreate(CamelModel):
    org_name: str = Field(default="", max_length=255)
    standard: str = Field(
        default="本科毕业论文规范（默认）",
        min_length=1,
        max_length=255,
    )
    check_format: bool = True
    check_citation: bool = True
    check_plagiarism: bool = False
    auto_report: bool = True


class ReviewTaskCreate(CamelModel):
    document_id: int = Field(gt=0)
    settings: ReviewSettingsCreate = Field(default_factory=ReviewSettingsCreate)
