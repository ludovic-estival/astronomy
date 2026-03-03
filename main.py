"""Utility script that compares telescopes."""

from dataclasses import dataclass
from pathlib import Path
import json
import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer()
console = Console()

EXIT_PUPIL_LOW = 0.5
EXIT_PUPIL_MAX = 6
EXIT_PUPIL_IDEAL = (1, 5)


@dataclass
class Telescope:
    """Represents a telescope."""

    name: str
    diameter: float
    focal: float

    @property
    def f_ratio(self) -> float:
        """Computes focal / diameter ratio."""
        return round(self.focal / self.diameter, 2)

    def get_magnification_range(self) -> dict:
        """
        Computes and returns magnification range.

        Exit pupil is 7 mm for children and 5 mm of old people,
        so we use 6 mm to find the lowest magnification possible.
        """
        return {
            "min": round(self.diameter / 6, 2),
            "practical": (self.diameter, self.diameter * 1.5),
            "theorical": self.diameter * 2,
        }


@dataclass
class Eyepiece:
    """Represents an eyepiece."""

    name: str
    focal: float

    def calculate_performance(self, telescope: Telescope) -> dict:
        """Computes and returns the zoom and exit pupil as a tuple."""
        magnification = telescope.focal / self.focal
        exit_pupil = round(telescope.diameter / magnification, 2)
        return {"magnification": round(magnification, 1), "exit_pupil": exit_pupil}


def extract_json(json_file_path: Path) -> tuple[list[Telescope], list[Eyepiece]]:
    """Extracts telescopes and eyepieces from a JSON file."""
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    telescopes = []
    eyepieces = []

    for t in data["telescopes"]:
        telescopes.append(Telescope(t["name"], t["diameter"], t["focal"]))

    for e in data["eyepieces"]:
        eyepieces.append(Eyepiece(e["name"], e["focal"]))

    return (telescopes, eyepieces)


def create_tables(
    telescopes: list[Telescope], eyepieces: list[Eyepiece]
) -> tuple[Table]:
    """Creates and returns tables of telescopes and eyepieces as a tuple."""

    telescope_table = Table(title="Telescopes comparison")
    telescope_table.add_column("Name")
    telescope_table.add_column("Diameter")
    telescope_table.add_column("Focal")
    telescope_table.add_column("F/D ratio")
    telescope_table.add_column("Lowest magnification")
    telescope_table.add_column("Highest theorical magnification")
    telescope_table.add_column("Highest practical magnification")

    eyepiece_table = Table(title="Eyepieces comparison")
    eyepiece_table.add_column("Telescope")

    for eyepiece in eyepieces:
        eyepiece_table.add_column(eyepiece.name)

    for telescope in telescopes:
        magnifications = telescope.get_magnification_range()
        practical_magnifications = magnifications["practical"]

        telescope_table.add_row(
            telescope.name,
            str(telescope.diameter),
            str(telescope.focal),
            str(telescope.f_ratio),
            str(magnifications["min"]),
            str(magnifications["theorical"]),
            f"Between {practical_magnifications[0]} and {practical_magnifications[1]}",
        )

        eyepiece_data = []
        for eyepiece in eyepieces:
            eyepiece_performances = eyepiece.calculate_performance(telescope)
            magnification = eyepiece_performances["magnification"]
            exit_pupil = eyepiece_performances["exit_pupil"]

            magnification_text = str(magnification)
            pupil_text = str(exit_pupil)

            if magnification > practical_magnifications[1]:
                magnification_text = f"[red]{magnification}[/red]"

            if exit_pupil < EXIT_PUPIL_LOW or exit_pupil > EXIT_PUPIL_MAX:
                pupil_text = f"[red]{exit_pupil}[/red]"

            if EXIT_PUPIL_IDEAL[0] <= exit_pupil <= EXIT_PUPIL_IDEAL[1]:
                pupil_text = f"[green]{exit_pupil}[/green]"

            eyepiece_data.append(
                f"Magnification : {magnification_text} - Exit pupil : {pupil_text}"
            )

        eyepiece_table.add_row(telescope.name, *eyepiece_data)

    return (telescope_table, eyepiece_table)


@app.command()
def compare(json_file_path: str):
    """Extracts, computes and prints a comparison between telescopes."""

    telescopes, eyepieces = extract_json(Path(json_file_path))
    telescopes_table, eyepieces_table = create_tables(telescopes, eyepieces)
    console.print(telescopes_table)
    console.print(eyepieces_table)


@app.command()
def print_parameters():
    """Prints parameters and formulas used to computes data."""

    const_table = Table(title="Constants")
    const_table.add_column("Constant")
    const_table.add_column("Value")

    const_table.add_row("Lowest exit pupil", str(EXIT_PUPIL_LOW))
    const_table.add_row("Highest exit pupil", str(EXIT_PUPIL_MAX))
    const_table.add_row(
        "Ideal exit pupil",
        f"between {EXIT_PUPIL_IDEAL[0]} and {EXIT_PUPIL_IDEAL[1]}",
    )

    telescope_table = Table(title="Telescopes computing")
    telescope_table.add_column("Calculation")
    telescope_table.add_column("Formula")
    telescope_table.add_row("F/D ratio", "focal / diameter")
    telescope_table.add_row("Lowest magnification", "diameter / 6")
    telescope_table.add_row("Highest practical magnification", "diameter * 1.5")
    telescope_table.add_row("Highest theorical magnification", "diameter * 2")

    eyepiece_table = Table(title="Eyepieces computing")
    eyepiece_table.add_column("Calculation")
    eyepiece_table.add_column("Formula")
    eyepiece_table.add_row("Magnification", "focal of telescope / focal of eyepiece")
    eyepiece_table.add_row("Exit pupil", "diameter of telescope / magnification")

    console.print(const_table)
    console.print(telescope_table)
    console.print(eyepiece_table)


if __name__ == "__main__":
    app()
