"""adding blogs

Revision ID: 06e774081e7e
Revises: 943135202a22
Create Date: 2018-07-22 13:49:16.206807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06e774081e7e'
down_revision = '943135202a22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goat_cheese',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_goat_cheese'))
    )
    op.create_table('zucchini_pasta',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reference_id', sa.Integer(), autoincrement=True, nullable=True),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('draft', sa.Boolean(), nullable=False),
    sa.Column('author', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author'], ['kale_chips.id'], name=op.f('fk_zucchini_pasta_author_kale_chips')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_zucchini_pasta'))
    )
    op.create_table('sushi_burrito',
    sa.Column('goat_cheese_id', sa.Integer(), nullable=True),
    sa.Column('zucchini_pasta_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['goat_cheese_id'], ['goat_cheese.id'], name=op.f('fk_sushi_burrito_goat_cheese_id_goat_cheese')),
    sa.ForeignKeyConstraint(['zucchini_pasta_id'], ['zucchini_pasta.id'], name=op.f('fk_sushi_burrito_zucchini_pasta_id_zucchini_pasta'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sushi_burrito')
    op.drop_table('zucchini_pasta')
    op.drop_table('goat_cheese')
    # ### end Alembic commands ###
