from dataclasses import dataclass, field


@dataclass
class Director:
    NameId: int
    Name: str
    # lista di tuple (movie_id, title, year, gross_income, genres:set) dei film diretti
    # nel range di anni selezionato dall'utente
    Movies: list = field(default_factory=list)

    def __hash__(self):
        return hash(self.NameId)

    def __eq__(self, other):
        if not isinstance(other, Director):
            return False
        return self.NameId == other.NameId

    def __str__(self):
        return f"{self.Name}"

    def get_genres(self):
        """Ritorna l'insieme di tutti i generi dei film diretti dal regista."""
        genres = set()
        for movie in self.Movies:
            genres |= movie["genres"] # unione di set
        return genres

    def get_total_gross_income(self):
        """Somma degli incassi (worlwide_gross_income) dei film diretti."""
        total = 0
        for movie in self.Movies:
            total += movie["gross_income"]
        return total

    def get_num_movies(self):
        return len(self.Movies)
