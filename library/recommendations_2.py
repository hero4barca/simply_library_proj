import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from library.models import Book, Favorite
from joblib import Memory
from multiprocessing import Pool, cpu_count


# Create a memory object for caching
memory = Memory('./cachedir', verbose=0)


def recommend_books(user, top_n=5):
    """
    Implements books recommendations based on the favorite books for the current user.
    @Param  user: the authenticated user object
    @Param top_n: the number of recommendation required
    @Return : List of recommended books with length 'top_n'; default 5
    """
    # Get the list of favorite book IDs for the user
    favorite_books = Favorite.objects.filter(user=user).values_list('book_id', flat=True)

    # If the user has no favorite books, return an empty list
    if not favorite_books:
        return []

    # List of favorite book IDs
    favorite_ids = list(favorite_books)

    # Get a dataframe of all books in the database
    book_df = get_books_df()

    # Remove favorite books from the book_df (optional)
    # book_df = book_df[~book_df['id'].isin(favorite_ids)].reset_index(drop=True)

    # Calculate similarity scores with favorite books
    similarity_scores = calculate_similarity(book_df, favorite_ids)

    # Sum similarity scores across all favorite books and sort to select the top N recommendations
    top_recommendations = similarity_scores.sum(axis=1).sort_values(ascending=False).head(top_n)

    # Build a dataframe of recommended books based on the top N indexes
    recommended_books = book_df.loc[top_recommendations.index]
    recommended_books_list = recommended_books.to_dict(orient='records')  # Convert to list of dicts

    return recommended_books_list

@memory.cache
def get_books_df():
    """
    Build a dataframe of all books in the database.
    @Returns dataframe of all books in the DB
    """
    # Use 'prefetch_related' to efficiently load the related authors in a single query.
    books = Book.objects.prefetch_related('authors').all()

    # Create a list of dictionaries, where each dict represents a row in the DataFrame.
    book_data = []
    for book in books:
        # Create a dictionary for each book containing the required fields
        book_dict = {
            'id': book.id,
            'title': book.title,
            'authors': [author.name for author in book.authors.all()],  # Collect all author names
            'author_name': book.authors.first().name if book.authors.exists() else None,  # Primary author name
            'language': book.language,
            'work_id': book.work_id,
            'edition_information': book.edition_information,
            'publisher': book.publisher,
            'num_pages': book.num_pages,
            'series_id': book.series_id,
            'series_name': book.series_name,
            'series_position': book.series_position,
            'description': book.description
        }

        # Append the book dictionary to the list
        book_data.append(book_dict)

    book_df = pd.DataFrame(book_data)
    return book_df


def compute_similarity_for_fav_book(args):
    """Compute similarity scores for a specific favorite book."""
    fav_id, fav_data, book_df, desc_matrix, title_matrix = args
    fav_series_id, fav_authors_set, fav_publisher = fav_data

    similarity_scores = pd.Series(0.0, index=book_df.index)

    # Series similarity: 0.5 if the same series_id
    if pd.notna(fav_series_id) and fav_series_id.strip() != "":
        same_series = (book_df["series_id"] == fav_series_id).astype(float) * 0.5
        similarity_scores += same_series

    # Author similarity: 0.3 if any common authors
    if fav_authors_set:
        author_similarity = book_df["authors"].apply(
            lambda authors: 1.0 if fav_authors_set.intersection(authors) else 0.0
        )
        similarity_scores += author_similarity * 0.3

    # Publisher similarity: 0.2 if same publisher
    if pd.notna(fav_publisher) and fav_publisher.strip() != "":
        same_publisher = (book_df["publisher"] == fav_publisher).astype(float) * 0.2
        similarity_scores += same_publisher

    # Description similarity: 0.1 * cosine similarity
    desc_sim = cosine_similarity(desc_matrix, desc_matrix[fav_data["index"]])
    similarity_scores += desc_sim[:, 0] * 0.1

    # Title similarity: 0.1 * cosine similarity
    title_sim = cosine_similarity(title_matrix, title_matrix[fav_data["index"]])
    similarity_scores += title_sim[:, 0] * 0.1

    return fav_id, similarity_scores



def calculate_similarity_2(book_df, favorite_ids):
    """
    Calculate similarity scores between all books and favorite books using multiprocessing.
    """
    # Preprocessing: Normalize text data
    book_df["description"] = book_df["description"].fillna("")
    book_df["title"] = book_df["title"].fillna("")

    # Initialize TF-IDF Vectorizer
    tfidf_vectorizer_desc = TfidfVectorizer(stop_words="english")
    tfidf_vectorizer_title = TfidfVectorizer(stop_words="english")

    # Cache TF-IDF matrices
    desc_matrix = tfidf_vectorizer_desc.fit_transform(book_df["description"])
    title_matrix = tfidf_vectorizer_title.fit_transform(book_df["title"])

    # Extract favorite books' metadata
    favorite_books_df = book_df[book_df["id"].isin(favorite_ids)].copy()
    fav_indices = favorite_books_df.index.tolist()
    fav_series_ids = favorite_books_df["series_id"].tolist()
    fav_authors = [frozenset(authors) for authors in favorite_books_df["authors"].tolist()]
    fav_publishers = favorite_books_df["publisher"].tolist()

    # Prepare data for parallel computation
    favorite_data = [
        (
            favorite_ids[i],
            {
                "index": fav_indices[i],
                "series_id": fav_series_ids[i],
                "authors_set": fav_authors[i],
                "publisher": fav_publishers[i],
            },
            book_df,
            desc_matrix,
            title_matrix,
        )
        for i in range(len(favorite_ids))
    ]

    # Use multiprocessing to compute similarity scores in parallel
    with Pool(cpu_count()) as pool:
        results = pool.map(compute_similarity_for_fav_book, favorite_data)

    # Initialize the final similarity_scores DataFrame
    similarity_scores = pd.DataFrame(0.0, index=book_df.index, columns=favorite_ids)

    # Collect results into the similarity_scores DataFrame
    for fav_id, scores in results:
        similarity_scores[fav_id] = scores

    # Optionally, remove favorite books from recommendations
    similarity_scores.loc[fav_indices] = 0.0

    return similarity_scores
