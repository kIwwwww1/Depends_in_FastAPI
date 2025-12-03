import uvicorn
from typing import Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

app = FastAPI()

async_engine = create_async_engine('sqlite+aiosqlite:///mydb.db')
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] 
    author: Mapped[str] 

class CreateBookModel(BaseModel):
    title: str = Field(min_length=5)
    author: str = Field(min_length=5)

class BookModel(CreateBookModel):
    id: int = Field(ge=1)


async def get_session():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

@app.get('/create-databse')
async def create_database():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return {'True': 'База создана'}
    

@app.post('/create-book')
async def add_book(new_book: CreateBookModel, session: SessionDep):
    session.add(new_book)
    await session.commit()
    return {'True': 'Книга добавлена'}

async def get_pages(limit: int, offset: int, session: SessionDep):
    query = select(Book).limit(limit).offset(offset)
    respons = await session.execute(query)
    return respons

PaginatorDep = Annotated[list[dict], Depends(get_pages)]

@app.get('/get-book_pages')
async def get_books(page_books: PaginatorDep) -> list[dict]:
    return page_books

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)