"""Utility script that compares telescopes."""

import json
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

EXIT_PUPIL_LOW = 0.5
EXIT_PUPIL_MAX = 6
EXIT_PUPIL_IDEAL = (1, 5)


class Telescope:
    """Represents a telescope."""

    def __init__(self, name: str, diameter: int | float, focal: int | float):
        self.name = name
        self.diameter = diameter
        self.focal = focal

    def compute_stats(self) -> dict:
        """Computes and returns stats of the telescope."""
        # 7 mm for children and 5 mm of old people
        min_zoom = round((self.diameter / 6), 2)
        max_zoom_practical = self.diameter * 1.5
        max_zoom_theorical = self.diameter * 2
        fd = round((self.focal / self.diameter), 2)
        return {
            "min_zoom": min_zoom,
            "max_zoom_practical_range": (self.diameter, max_zoom_practical),
            "max_zoom_theoretical": max_zoom_theorical,
            "fd": fd,
        }


class Ocular:
    """Represents an ocular"""

    def __init__(self, name: str, focal: int | float):
        self.name = name
        self.focal = focal

    def compute_stats(self, telescope: Telescope) -> tuple[int | float]:
        """Computes and returns the zoom and exit pupil as a tuple."""
        zoom = telescope.focal / self.focal
        exit_pupil = round((telescope.diameter / zoom), 2)
        return (zoom, exit_pupil)


def extract_json(json_file: str) -> tuple[list[Telescope], list[Ocular]]:
    """Extracts telescopes and oculars from a JSON file."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    telescopes = []
    oculars = []

    for tel in data["telescopes"]:
        telescopes.append(Telescope(tel["name"], tel["diameter"], tel["focal"]))

    for ocu in data["oculars"]:
        oculars.append(Ocular(ocu["name"], ocu["focal"]))

    return (telescopes, oculars)


def create_tables(telescopes: list[Telescope], oculars: list[Ocular]) -> tuple[Table]:
    """Creates and returns tables of telescopes and oculars as a tuple."""

    telescope_table = Table(title="Comparaison télescopes")
    telescope_table.add_column("Nom")
    telescope_table.add_column("Diamètre")
    telescope_table.add_column("Focale")
    telescope_table.add_column("Rapport F/D")
    telescope_table.add_column("Gross. min.")
    telescope_table.add_column("Gross. max. théorique")
    telescope_table.add_column("Gross. max. pratique")

    ocular_table = Table(title="Comparaison oculaires")
    ocular_table.add_column("Télescope")

    for ocular in oculars:
        ocular_table.add_column(ocular.name)

    for telescope in telescopes:
        stats = telescope.compute_stats()

        max_zoom_practical_low = stats["max_zoom_practical_range"][0]
        max_zoom_practical_high = stats["max_zoom_practical_range"][1]

        telescope_table.add_row(
            telescope.name,
            str(telescope.diameter),
            str(telescope.focal),
            str(stats["fd"]),
            str(stats["min_zoom"]),
            str(stats["max_zoom_theoretical"]),
            f"entre {max_zoom_practical_low} et {max_zoom_practical_high}",
        )

        ocular_data = []
        for ocular in oculars:
            zoom, exit_pupil = ocular.compute_stats(telescope)

            zoom_text = str(zoom)
            pupil_text = str(exit_pupil)

            if zoom > max_zoom_practical_high:
                zoom_text = f"[red]{zoom}[/red]"

            if exit_pupil < EXIT_PUPIL_LOW or exit_pupil > EXIT_PUPIL_MAX:
                pupil_text = f"[red]{exit_pupil}[/red]"

            if EXIT_PUPIL_IDEAL[0] <= exit_pupil <= EXIT_PUPIL_IDEAL[1]:
                pupil_text = f"[green]{exit_pupil}[/green]"

            ocular_data.append(f"Gross. : {zoom_text} - Pupille sortie : {pupil_text}")

        ocular_table.add_row(telescope.name, *ocular_data)

    return (telescope_table, ocular_table)


@app.command()
def compare(json_file: str):
    """Extracts, computes and prints a comparison between telescopes."""

    telescopes, oculars = extract_json(json_file)
    telescopes_table, oculars_table = create_tables(telescopes, oculars)
    console.print(telescopes_table)
    console.print(oculars_table)


@app.command()
def print_parameters():
    """Prints parameters and formulas used to computes data."""

    const_table = Table(title="Constantes")
    const_table.add_column("Constante")
    const_table.add_column("Valeur prise")

    const_table.add_row("Pupille de sortie min.", str(EXIT_PUPIL_LOW))
    const_table.add_row("Pupille de sortie max.", str(EXIT_PUPIL_MAX))
    const_table.add_row(
        "Pupille de sortie idéale",
        f"entre {EXIT_PUPIL_IDEAL[0]} et {EXIT_PUPIL_IDEAL[1]}",
    )

    telescope_table = Table(title="Calculs pour les télescopes")
    telescope_table.add_column("Calcul")
    telescope_table.add_column("Formule utilisée")
    telescope_table.add_row("Rapport F/D", "focale / diamètre")
    telescope_table.add_row("Gross. min.", "diamètre / 6")
    telescope_table.add_row("Gross. max. pratique", "diamètre * 1.5")
    telescope_table.add_row("Gross. max. théorique", "diamètre * 2")

    ocular_table = Table(title="Calculs pour les oculaires")
    ocular_table.add_column("Calcul")
    ocular_table.add_column("Formule utilisée")
    ocular_table.add_row("Gross.", "focale télescope / focale oculaire")
    ocular_table.add_row("Pupille de sortie", "diamètre télescope / grossissement")

    console.print(const_table)
    console.print(telescope_table)
    console.print(ocular_table)


if __name__ == "__main__":
    app()
