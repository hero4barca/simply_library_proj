import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from library.models import Book, Favorite
from joblib import Memory

# Create a memory object for caching
memory = Memory('./cachedir', verbose=0)


def recommend_books(user, top_n=5):
    """
    Implements books recommendations based on the favorite books for the current user.
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


@memory.cache
def compute_tfidf_matrices(book_df):
    """
    Computes and caches the TF-IDF matrices for descriptions and titles.

    Args:
        book_df (pd.DataFrame): DataFrame containing book descriptions and titles.

    Returns:
        Tuple of TF-IDF matrices for descriptions and titles.
    """
    # Initialize TF-IDF Vectorizer
    tfidf_vectorizer_desc = TfidfVectorizer(stop_words="english")
    tfidf_vectorizer_title = TfidfVectorizer(stop_words="english")

    # Fit and transform descriptions and titles
    desc_matrix = tfidf_vectorizer_desc.fit_transform(book_df["description"])
    title_matrix = tfidf_vectorizer_title.fit_transform(book_df["title"])

    return desc_matrix, title_matrix


def calculate_similarity(book_df, favorite_ids):
    """
    Calculate the similarity between all books and favorite books using precomputed values for efficiency.

    Args:
        book_df (pd.DataFrame): DataFrame containing all books with necessary fields.
        favorite_ids (list): List of favorite book IDs for the user.

    Returns:
        pd.DataFrame: DataFrame containing similarity scores with favorite books as columns.
    """
    # Normalize text data
    book_df["description"] = book_df["description"].fillna("")
    book_df["title"] = book_df["title"].fillna("")

    # Fit and transform descriptions and titles
    desc_matrix, title_matrix = compute_tfidf_matrices(book_df)

    # Initialize similarity_scores DataFrame with float dtype
    similarity_scores = pd.DataFrame(0.0, index=book_df.index, columns=favorite_ids, dtype='float64')

    # Extract favorite books data
    favorite_books_df = book_df[book_df['id'].isin(favorite_ids)].copy()
    fav_indices = favorite_books_df.index.tolist()

    # Precompute favorite books' metadata
    fav_series_ids = favorite_books_df["series_id"].tolist()
    fav_authors = [set(authors) for authors in favorite_books_df["authors"].tolist()]
    fav_publishers = favorite_books_df["publisher"].tolist()

    # Compute cosine similarity for descriptions and titles between all books and favorite books
    desc_similarity = cosine_similarity(desc_matrix, desc_matrix[fav_indices])  # Shape: (n_books, n_favs)
    title_similarity = cosine_similarity(title_matrix, title_matrix[fav_indices])  # Shape: (n_books, n_favs)

    # Iterate over each favorite book and compute similarity scores
    for i, fav_id in enumerate(favorite_ids):
        fav_series_id = fav_series_ids[i]
        fav_authors_set = fav_authors[i]
        fav_publisher = fav_publishers[i]

        # Series similarity: 0.5 if same series_id
        if pd.notna(fav_series_id) and fav_series_id.strip() != "":
            same_series = (book_df["series_id"] == fav_series_id).astype(float) * 0.5
            similarity_scores[fav_id] += same_series

        # Author similarity: 0.3 if any common authors
        if fav_authors_set:
            # Vectorized author similarity using list comprehension
            author_similarity = book_df["authors"].apply(lambda authors: 1.0 if fav_authors_set.intersection(authors) else 0.0)
            similarity_scores[fav_id] += author_similarity * 0.3

        # Publisher similarity: 0.2 if same publisher
        if pd.notna(fav_publisher) and fav_publisher.strip() != "":
            same_publisher = (book_df["publisher"] == fav_publisher).astype(float) * 0.2
            similarity_scores[fav_id] += same_publisher

        # Description similarity: 0.1 * cosine similarity
        similarity_scores[fav_id] += desc_similarity[:, i] * 0.1

        # Title similarity: 0.1 * cosine similarity
        similarity_scores[fav_id] += title_similarity[:, i] * 0.1

    # Optionally, remove favorite books from recommendations by setting their scores to 0
    similarity_scores.loc[favorite_books_df.index] = 0.0

    return similarity_scores
