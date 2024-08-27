from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Book
from bson.objectid import ObjectId 

router = APIRouter()

@router.post("/",response_description="Add a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    new_book = request.app.database["books"].insert_one(book)
    created_book = request.app.database["books"].find_one({"_id": new_book.inserted_id})
    return created_book

@router.get("/", response_description="List all read books", response_model=List[Book])
def list_books(request:Request):
    books = list(request.app.mongodb_database["books"].find(limit=100))
    return books

@router.get("/{id}", response_description="Retrieve a single book by id", response_model=Book)
def get_book(request: Request, id: str):
    book = request.app.mongodb_database["books"].find_one({"_id":ObjectId(id)})
    if book:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No book with id {} found!".format(id))