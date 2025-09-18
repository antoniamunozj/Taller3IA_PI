import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate and store embeddings for all movies in the database"

    def handle(self, *args, **kwargs):
        # Load OpenAI API key
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # Fetch all movies from the database
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        # Iterate through movies and generate embeddings
        for movie in movies:
            try:
                # Sanitize description to prevent API errors
                sanitized_description = movie.description.encode('utf-8', 'ignore').decode('utf-8')
                emb = get_embedding(sanitized_description)
                
                # Store embedding as binary in the database
                movie.emb = emb.tobytes()
                movie.save()
                
                # Safely print success message
                try:
                    self.stdout.write(self.style.SUCCESS(f"Embedding stored for: {movie.title}"))
                except UnicodeEncodeError:
                    safe_title = movie.title.encode('ascii', 'ignore').decode('ascii')
                    self.stdout.write(self.style.SUCCESS(f"Embedding stored for: {safe_title} (unprintable title)"))

            except Exception as e:
                self.stderr.write(f"Failed to generate embedding for {movie.title}: {e}")

        self.stdout.write(self.style.SUCCESS("Finished generating embeddings for all movies"))