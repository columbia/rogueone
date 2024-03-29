"""empty message

Revision ID: 21bc17386dfc
Revises: b9754ef6f798
Create Date: 2023-08-31 08:54:55.428567

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '21bc17386dfc'
down_revision = 'b9754ef6f798'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dependentdependency', sa.Column('transitive', sa.Boolean(), nullable=True))
    op.alter_column('package', 'author_name',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=300),
               existing_nullable=True)
    op.alter_column('package', 'author_email',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=300),
               existing_nullable=True)
    op.alter_column('package', 'author_url',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=300),
               existing_nullable=True)
    #op.alter_column('taskmodel', 'state',
    #           existing_type=postgresql.ENUM('NotStarted', 'Running', 'CompletedSuccess', 'CompletedError', 'ExceptionCaught', 'TimedOut', name='taskmodelstate'),
    #           type_=sa.Enum('NotStarted', 'Running', 'CompletedSuccess', 'CompletedError', 'ExceptionCaught', 'TimedOut', name='state'),
    #           existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    #op.alter_column('taskmodel', 'state',
    #           existing_type=sa.Enum('NotStarted', 'Running', 'CompletedSuccess', 'CompletedError', 'ExceptionCaught', 'TimedOut', name='state'),
    #           type_=postgresql.ENUM('NotStarted', 'Running', 'CompletedSuccess', 'CompletedError', 'ExceptionCaught', 'TimedOut', name='taskmodelstate'),
    #           existing_nullable=False)
    op.alter_column('package', 'author_url',
               existing_type=sa.String(length=300),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
    op.alter_column('package', 'author_email',
               existing_type=sa.String(length=300),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
    op.alter_column('package', 'author_name',
               existing_type=sa.String(length=300),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
    op.drop_column('dependentdependency', 'transitive')
    # ### end Alembic commands ###
