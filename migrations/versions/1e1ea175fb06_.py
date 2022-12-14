"""empty message

Revision ID: 1e1ea175fb06
Revises: a59d6e982d71
Create Date: 2022-08-12 23:45:38.618086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e1ea175fb06'
down_revision = 'a59d6e982d71'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('is_looking_talent', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'is_looking_talent')
    op.drop_column('artist', 'website_link')
    # ### end Alembic commands ###
