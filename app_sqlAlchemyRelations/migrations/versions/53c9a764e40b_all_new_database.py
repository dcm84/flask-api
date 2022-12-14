"""all new database

Revision ID: 53c9a764e40b
Revises: 
Create Date: 2022-08-24 18:12:08.436255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53c9a764e40b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('surname', sa.String(length=32), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quote_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=255), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author_model.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quote_model')
    op.drop_table('author_model')
    # ### end Alembic commands ###
