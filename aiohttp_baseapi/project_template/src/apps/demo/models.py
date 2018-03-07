# -*- coding: utf-8 -*-

import sqlalchemy as sa
from core.database import BaseModel


class Author(BaseModel):
    __tablename__ = 'authors'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    surname = sa.Column(sa.String)


class Book(BaseModel):
    __tablename__ = 'books'
    __table_args__ = (
        sa.UniqueConstraint('category', 'name', name='unique_book_name_in_category'),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    category = sa.Column(sa.String(100), nullable=False, index=True)
    name = sa.Column(sa.String(255), nullable=True)
    is_available = sa.Column(sa.Boolean)
    author_id = sa.Column(sa.Integer, sa.ForeignKey(Author.id, onupdate='CASCADE', ondelete='CASCADE'), index=True)
