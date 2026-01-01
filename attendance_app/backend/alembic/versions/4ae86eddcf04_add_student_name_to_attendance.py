"""add student_name to attendance

Revision ID: 4ae86eddcf04
Revises: 68b73cc01a68
Create Date: 2025-12-30 20:53:26.347810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ae86eddcf04'
down_revision: Union[str, None] = '68b73cc01a68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Backfill existing rows
    op.execute(
        """
        UPDATE attendance
        SET student_name = 'Unknown Student'
        WHERE student_name IS NULL
        """
    )

def downgrade():
    op.drop_column("attendance", "student_name")