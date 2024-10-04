import csv
import os
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from your_app.models import Book, Author  # Import your models
from django.db import transaction

class Command(BaseCommand):
    help = 'Load books from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be loaded.')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        count = 0

        # Check if the file exists
        if not os.path.exists(csv_file):
            raise CommandError(f"File '{csv_file}' does not exist.")

        # Open the CSV file
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Start a transaction so the operation is atomic
            with transaction.atomic():
                for row in reader:
                    title = row['title'].strip()
                    author_name = row['author_name'].strip() if row['author_name'] else None
                    authors_list = row['authors']
                    language = row['language'].strip() if row['language'] else None
                    work_id = row['work_id'].strip() if row['work_id'] else None
                    edition_information = row['edition_information'].strip() if row['edition_information'] else None
                    publisher = row['publisher'].strip() if row['publisher'] else None
                    num_pages = row['num_pages'].strip() if row['num_pages'] else None
                    series_id = row['series_id'].strip() if row['series_id'] else None
                    series_name = row['series_name'].strip() if row['series_name'] else None
                    series_position = row['series_position'].strip() if row['series_position'] else None
                    description = row['description'].strip() if row['description'] else None

                    soup = BeautifulSoup(description, "html.parser")
                    description = soup.get_text()

                    # Handle the creation of authors
                    author_objs = []
                    if authors_list:
                        try:
                            # Authors field is a list of JSON objects, parse and handle it
                            authors_json = eval(authors_list)  # Use eval or json.loads (if JSON)
                            if len(authors_json) > 1:
                                # More than one author, use the authors list
                                for author_data in authors_json:
                                    author_name_from_list = author_data.get('name', '').strip()
                                    if author_name_from_list:
                                        author_obj, created = Author.objects.get_or_create(name=author_name_from_list)
                                        author_objs.append(author_obj)
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Failed to process authors for book '{title}': {e}"))
                            continue

                    # If no authors in the authors list, use author_name
                    if not author_objs and author_name:
                        author_obj, created = Author.objects.get_or_create(name=author_name)
                        author_objs.append(author_obj)

                    # Ensure there's at least one author for the book
                    if not author_objs:
                        self.stderr.write(self.style.ERROR(f"Skipping book '{title}' because it has no valid authors."))
                        continue

                    # Create or update the book entry
                    try:
                        book, created = Book.objects.update_or_create(
                            title=title,
                            defaults={
                                'language': language,
                                'work_id': work_id,
                                'edition_information': edition_information,
                                'publisher': publisher,
                                'num_pages': num_pages if num_pages else None,
                                'series_id': series_id,
                                'series_name': series_name,
                                'series_position': series_position,
                                'description': description,
                            }
                        )
                        # Assign authors to the book (many-to-many relationship)
                        book.authors.set(author_objs)
                        book.save()

                        if created:
                            # self.stdout.write(self.style.SUCCESS(f"Successfully added book '{title}'"))
                            count = count + 1
                        else:
                            count = count + 1
                            # self.stdout.write(self.style.SUCCESS(f"Successfully updated book '{title}'"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error saving book '{title}': {e}"))
                        continue

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} books"))
