from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Book, BookUpdate
from bson.objectid import ObjectId

router = APIRouter()


@router.post(
    "/",
    response_description="Add a new book",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    book["_id"] = ObjectId(book["_id"])
    new_book = request.app.mongodb_database["books"].insert_one(book)
    created_book = request.app.mongodb_database["books"].find_one(
        {"_id": new_book.inserted_id}
    )
    return created_book


@router.get("/", response_description="List all read books", response_model=List[Book])
def list_books(request: Request):
    txt_query = {k: request.query_params.get(k) for k in ["title","author", "status","category"]}
    num_query = {k: request.query_params.get(k) for k in ["month", "year", "rating", "pages"]}
    query = {k:int(v) for k,v in num_query.items() if v}
    query.update({k:v for k,v in txt_query.items() if v})
    books = list(request.app.mongodb_database["books"].find(query, limit=100))
    return books


@router.get(
    "/{id}", response_description="Retrieve a single book by id", response_model=Book
)
def get_book(request: Request, id: str):
    book = request.app.mongodb_database["books"].find_one({"_id": ObjectId(id)})
    if book:
        return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No book with id {} found!".format(id),
    )


@router.put("/{id}", response_description="Update a book by id", response_model=Book)
def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    book_to_update = request.app.mongodb_database["books"].find_one(
        {"_id": ObjectId(id)}, {"_id": 1}
    )

    if book_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found"
        )

    book = {k: v for k, v in book.model_dump(exclude_unset=True).items()}
    if len(book) >= 1:
        update_res = request.app.mongodb_database["books"].update_one(
            {"_id": ObjectId(id)}, {"$set": book}
        )

        if update_res.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"There was an error while updating book with if {id}. "
                    "It seems it is no longer available or this change has been already be done."
                ),
            )

    if (
        existing_book := request.app.mongodb_database["books"].find_one(
            {"_id": ObjectId(id)}
        )
    ) is not None:
        return existing_book


@router.delete("/{id}", response_description="Delete a book by id")
def delete_book(id: str, request: Request, response: Response):
    delete_res = request.app.mongodb_database["books"].delete_one({"_id": ObjectId(id)})
    if delete_res.deleted_count == 1:
        response.status_code = (
            status.HTTP_204_NO_CONTENT
        )  # successful, no content to return
        return response
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found"
    )
