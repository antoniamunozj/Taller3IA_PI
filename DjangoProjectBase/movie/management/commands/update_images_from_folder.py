from django.core.management.base import BaseCommand
from movie.models import Movie
import os

class Command(BaseCommand):
    help = 'Update movie image paths in the database from the media folder.'

    def handle(self, *args, **kwargs):
        movies = Movie.objects.all()
        updated_count = 0
        self.stdout.write('Starting image path update...')

        for movie in movies:
            # Construct the image path based on the movie title
            image_filename = f'm_{movie.title}.png'
            image_db_path = os.path.join('movie/images', image_filename)

            # Assign the path to the movie's image field
            movie.image = image_db_path
            movie.save()
            updated_count += 1
            
            # Safely write the output to the console
            try:
                self.stdout.write(self.style.SUCCESS(f'Updated image path for: {movie.title}'))
            except UnicodeEncodeError:
                # If printing the title fails, encode it safely for the console
                safe_title = movie.title.encode('ascii', 'ignore').decode('ascii')
                self.stdout.write(self.style.SUCCESS(f'Updated image path for: {safe_title} (title had unprintable characters)'))

        self.stdout.write(self.style.SUCCESS(f'Finished. Updated paths for {updated_count} movies.'))