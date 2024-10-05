A simple library API project with django-rest-framework.

 API Endpoints:
    -Books:
    * GET /books - Retrieve a list of all books.
    * GET /books/:id - Retrieve a specific book by ID.
    * POST /books - Create a new book (protected).
    * PUT /books/:id - Update an existing book (protected).
    * DELETE /books/:id - Delete a book (protected).

    -Authors:
    *GET /authors - Retrieve a list of all authors.
    *GET /authors/:id - Retrieve a specific author by ID.
    *POST /authors - Create a new author (protected).
    *PUT /authors/:id - Update an existing author (protected).
    *DELETE /authors/:id - Delete an author (protected).

    -Favorites:
    *GET /favorites - Retrieve a list of all books in a users favorites list (protected)
    *POST /favourites - Add a book to users favorites list, 'book_id' in request body (protected)
    *DELETE /favorites/:book_id - Remove a book from user's favorites list

Authentication:
    *Use JWT for user authentication.
    *Implement registration (POST /register) and login (POST /login) endpoints.
    *Protect endpoints for creating, updating, and deleting books/authors.

Search Functionality:
	*Implement search functionality to find books by title or author name (GET /books?search=query)

Recommendation: Returns a list of recommended titles based on books in a user's favorites list. This feature compares the books in the favorites list to all other books in the db using a similarity algorithm. The book fields - series, author, publisher, title, description - are focused on. Same **series** is weighted 0.3, intersection of **author(s)** is weighted 0.3, same **publisher** is weighted 0.2, cosign similarity for **title** and **description** are weighted 0.1 each. Implementation is optimized to return recommendations in under 1 sec as part of the response to the **POST /favourites ** endpoint.