import flet as ft


class Controller:
    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._directorValue = None

    def handleCreaGrafo(self, e):
        self._view._txt_result.controls.clear()

        date_from = self._view._dpFrom.value.date()
        date_to = self._view._dpTo.value.date()
        if date_from is None or date_to is None:
            self._view.create_alert("Seleziona entrambe le date.")
            return
        if date_from > date_to:
            self._view.create_alert("La data di inizio deve precedere la data di fine.")
            return

        try:
            self._model.buildGraph(date_from, date_to)

            self._view._txt_result.controls.append(
                ft.Text("Grafo correttamente creato.")
            )
            self._view._txt_result.controls.append(
                ft.Text(f"Numero di vertici: {self._model.getNumNodi()}")
            )
            self._view._txt_result.controls.append(
                ft.Text(f"Numero di archi: {self._model.getNumEdges()}")
            )

            self._fillDDDirectors()
            self._view.update_page()
        except Exception as ex:
            self._view.create_alert(f"Errore nella creazione del grafo: {ex}")
            print(ex)

    def handleStampaInfo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodi() == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        try:
            director_max_degree, max_degree = self._model.getDirectorWithMaxDegree()
            self._view._txt_result.controls.append(
                ft.Text(f"Regista con grado maggiore: {director_max_degree} (grado: {max_degree})")
            )

            director_max_weight, max_weight = self._model.getDirectorWithMaxWeightSum()
            self._view._txt_result.controls.append(
                ft.Text(f"Regista con somma pesi incidenti massima: {director_max_weight} (somma: {max_weight})")
            )

            self._view._txt_result.controls.append(ft.Text(""))
            self._view._txt_result.controls.append(ft.Text("Top 5 archi con peso maggiore:"))

            top5 = self._model.getTop5Edges()
            for idx, (r1, r2, peso) in enumerate(top5, start=1):
                self._view._txt_result.controls.append(
                    ft.Text(f"{idx}. {r1} -- {r2} (peso: {peso})")
                )

            self._view.update_page()
        except Exception as ex:
            self._view.create_alert(f"Errore nella stampa delle info: {ex}")

    def handleTrovaGruppo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodi() == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        if self._directorValue is None:
            self._view.create_alert("Seleziona un regista dal menu a tendina.")
            return

        try:
            N = int(self._view._txtInN.value)
            if N <= 0:
                self._view.create_alert("Inserisci un numero intero positivo per N.")
                return
        except (ValueError, TypeError):
            self._view.create_alert("Inserisci un valore numerico valido per N.")
            return

        try:
            best_group, best_gross = self._model.getBestGroup(self._directorValue, N)

            if not best_group:
                self._view._txt_result.controls.append(
                    ft.Text("Nessun gruppo di registi trovato con i vincoli richiesti.")
                )
                self._view.update_page()
                return

            sorted_group = sorted(best_group, key=lambda d: d.Name)

            self._view._txt_result.controls.append(ft.Text("Lista alfabetica dei registi selezionati:"))
            self._view._txt_result.controls.append(ft.Text(""))

            for director in sorted_group:
                self._view._txt_result.controls.append(
                    ft.Text(
                        f"  - {director.Name}: {director.get_num_movies()} film diretti, "
                        f"incasso totale {director.get_total_gross_income():.2f}"
                    )
                )

            self._view._txt_result.controls.append(ft.Text(""))
            self._view._txt_result.controls.append(
                ft.Text(f"Numero totale di registi selezionati: {len(best_group)}")
            )
            self._view._txt_result.controls.append(
                ft.Text(f"Incasso complessivo della soluzione ottima: {best_gross:.2f}")
            )

            self._view.update_page()
        except Exception as ex:
            self._view.create_alert(f"Errore nella ricerca del gruppo di registi: {ex}")


    def _fillDDDirectors(self):
        self._view._ddDirector.options.clear()
        all_directors = self._model.getAllDirectors()

        directorOptions = list(
            map(lambda d: ft.dropdown.Option(data=d, key=str(d), on_click=self._choiceDirector), all_directors)
        )
        self._view._ddDirector.options = directorOptions

        self._view.update_page()

    def _choiceDirector(self, e):
        self._directorValue = e.control.data