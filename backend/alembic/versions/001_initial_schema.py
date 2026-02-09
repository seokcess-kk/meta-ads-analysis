"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ads_raw table
    op.create_table(
        "ads_raw",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ad_id", sa.String(length=255), nullable=False),
        sa.Column("page_name", sa.String(length=255), nullable=True),
        sa.Column("page_id", sa.String(length=255), nullable=True),
        sa.Column("ad_creative_body", sa.Text(), nullable=True),
        sa.Column("ad_creative_link_title", sa.Text(), nullable=True),
        sa.Column("ad_creative_link_description", sa.Text(), nullable=True),
        sa.Column("ad_snapshot_url", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("stop_date", sa.Date(), nullable=True),
        sa.Column("platforms", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("spend_lower", sa.Integer(), nullable=True),
        sa.Column("spend_upper", sa.Integer(), nullable=True),
        sa.Column("impressions_lower", sa.Integer(), nullable=True),
        sa.Column("impressions_upper", sa.Integer(), nullable=True),
        sa.Column("target_country", sa.String(length=10), nullable=True),
        sa.Column("industry", sa.String(length=50), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("image_s3_path", sa.Text(), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ad_id"),
    )
    op.create_index("idx_ads_industry", "ads_raw", ["industry"], unique=False)
    op.create_index("idx_ads_region", "ads_raw", ["region"], unique=False)
    op.create_index("idx_ads_start_date", "ads_raw", ["start_date"], unique=False)
    op.create_index("idx_ads_collected_at", "ads_raw", ["collected_at"], unique=False)

    # ads_analysis_image table
    op.create_table(
        "ads_analysis_image",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ad_id", sa.String(length=255), nullable=False),
        sa.Column("has_person", sa.Boolean(), nullable=True),
        sa.Column("person_type", sa.String(length=50), nullable=True),
        sa.Column("text_ratio", sa.Integer(), nullable=True),
        sa.Column("has_chart", sa.Boolean(), nullable=True),
        sa.Column("logo_position", sa.String(length=50), nullable=True),
        sa.Column("primary_color", sa.String(length=7), nullable=True),
        sa.Column("secondary_color", sa.String(length=7), nullable=True),
        sa.Column("tertiary_color", sa.String(length=7), nullable=True),
        sa.Column("color_tone", sa.String(length=20), nullable=True),
        sa.Column("saturation", sa.String(length=20), nullable=True),
        sa.Column("layout_type", sa.String(length=50), nullable=True),
        sa.Column("atmosphere", sa.String(length=50), nullable=True),
        sa.Column("emphasis_elements", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("mentioned_regions", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("analysis_raw", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ad_id"], ["ads_raw.ad_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ad_id"),
    )

    # ads_analysis_copy table
    op.create_table(
        "ads_analysis_copy",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ad_id", sa.String(length=255), nullable=False),
        sa.Column("headline", sa.Text(), nullable=True),
        sa.Column("headline_length", sa.Integer(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("cta", sa.Text(), nullable=True),
        sa.Column("core_message", sa.String(length=50), nullable=True),
        sa.Column("numbers", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("regions", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("discount_info", sa.String(length=255), nullable=True),
        sa.Column("free_benefit", sa.String(length=255), nullable=True),
        sa.Column("social_proof", sa.String(length=255), nullable=True),
        sa.Column("urgency", sa.String(length=255), nullable=True),
        sa.Column("differentiation", sa.Text(), nullable=True),
        sa.Column("formality", sa.String(length=20), nullable=True),
        sa.Column("emotion", sa.String(length=20), nullable=True),
        sa.Column("style", sa.String(length=20), nullable=True),
        sa.Column("target_audience", sa.String(length=50), nullable=True),
        sa.Column("keywords", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("analysis_raw", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ad_id"], ["ads_raw.ad_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ad_id"),
    )

    # collect_jobs table
    op.create_table(
        "collect_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("keywords", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("industry", sa.String(length=50), nullable=True),
        sa.Column("country", sa.String(length=10), nullable=True),
        sa.Column("target_count", sa.Integer(), nullable=True),
        sa.Column("collected_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )


def downgrade() -> None:
    op.drop_table("collect_jobs")
    op.drop_table("ads_analysis_copy")
    op.drop_table("ads_analysis_image")
    op.drop_index("idx_ads_collected_at", table_name="ads_raw")
    op.drop_index("idx_ads_start_date", table_name="ads_raw")
    op.drop_index("idx_ads_region", table_name="ads_raw")
    op.drop_index("idx_ads_industry", table_name="ads_raw")
    op.drop_table("ads_raw")
