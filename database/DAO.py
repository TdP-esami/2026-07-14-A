import re

from database.DB_connect import DBConnect
from model.director import Director


class DAO:

    @staticmethod
    def getDirectorsInDateRange(date_from, date_to):
        conn = DBConnect.get_connection()
        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                select distinct n.id, n.name
                from names n, director_mapping dm, movie m
                where n.id = dm.name_id
                and dm.movie_id = m.id
                and m.date_published BETWEEN %s AND %s
                order by n.name
                """

        cursor.execute(query, (date_from, date_to))

        for row in cursor:
            results.append(Director(row["id"], row["name"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getMoviesForDirectorInRange(director, date_from, date_to):
        """
        dato un director, lo popolo con la lista dei film diretti in range di date.
        i film saranno un dic con questi campi:
        {"movie_id", "title", "year", "gross_income" (float), "genres" (set di stringhe)}.
        """
        conn = DBConnect.get_connection()

        cursor = conn.cursor(dictionary=True)
        query = """
                select m.id, m.title, m.date_published, m.worlwide_gross_income
                from movie m, director_mapping dm
                where m.id = dm.movie_id
                and dm.name_id = %s
                and m.date_published between %s and %s
                """
        cursor.execute(query, (director.NameId, date_from, date_to))
        movie_rows = cursor.fetchall()

        movies = []
        for row in movie_rows:
            genres = DAO._getGenresForMovie(conn, row["id"])
            gross_income = DAO._parseGrossIncome(row["worlwide_gross_income"])
            movies.append({
                "movie_id": row["id"],
                "title": row["title"],
                "date": row["date_published"],
                "gross_income": gross_income,
                "genres": genres,
            })

        director.Movies = movies

        cursor.close()
        conn.close()

    @staticmethod
    def _getGenresForMovie(conn, movie_id):
        """Ritorna genere di un film."""
        cursor = conn.cursor(dictionary=True)
        query = """
                select g.genre
                from genre g
                where g.movie_id = %s
                """
        cursor.execute(query, (movie_id,))
        genres = set(row["genre"] for row in cursor if row["genre"] is not None)
        cursor.close()
        return genres

    @staticmethod
    def _parseGrossIncome(raw_value):
        """
        Questo metodo recupera il worldwide_gross_income, scartando i None ed i valori non numerici del campo (e.g. $).
        I tre casi di film con ricavo in INR vengono esclusi.
        """
        if raw_value is None or raw_value.strip().startswith("INR"):
            return 0.0
        try:
            digits_only = re.sub(r"[^\d.]", "", str(raw_value)) #sostituisco ogni carattere diverso da numeroi o punti con ""
            if digits_only == "":
                return 0.0
            return float(digits_only)
        except (ValueError, TypeError):
            return 0.0
