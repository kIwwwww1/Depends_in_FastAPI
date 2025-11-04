from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

engine = create_async_engine('sqlite+aiosqlite:///books.db')
new_session = async_sessionmaker(engine)

app = FastAPI()

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass


class BookORM(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)

class BookAdd(BaseModel):
    title: str
    author: str

class Book(BaseModel):
    id: int

@app.post('/create_database')
async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {'Ok': 'True'}

@app.post('/create_book')
async def create_new_book(data: BookAdd, session: SessionDep):
    new_book = BookORM(
        title=data.title,
        author=data.author)
    session.add(new_book)
    await session.commit()
    return {'Ok': 'True'}

@app.get('/books')
async def get_books(session: SessionDep, limit:int, offset: int):
    query = select(BookORM).limit(limit).offset(offset)
    respons = await session.execute(query)
    return respons.scalars().all()

