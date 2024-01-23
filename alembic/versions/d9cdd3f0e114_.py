"""empty message

Revision ID: d9cdd3f0e114
Revises: 
Create Date: 2023-07-13 13:44:03.303790

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd9cdd3f0e114'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('odgenresult')
    op.drop_index('rogueoneresult.run_timestampIDX', table_name='rogueoneresult')
    op.add_column('versionpair', sa.Column('version_deps_download_state', sa.Enum('NotAttempted', 'Started', 'Failed', 'Succeeded', name='versionpairdependencystate'), server_default='NotAttempted', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('versionpair', 'version_deps_download_state')
    op.create_index('rogueoneresult.run_timestampIDX', 'rogueoneresult', ['run_timestamp'], unique=False)
    op.create_table('odgenresult',
    sa.Column('run_timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('disk_location', sa.VARCHAR(length=4096), autoincrement=False, nullable=False),
    sa.Column('error', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('analysis_length', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('json_result', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('version_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['version_id'], ['version.id'], name='odgenresult_version_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='odgenresult_pkey')
    )
    # ### end Alembic commands ###