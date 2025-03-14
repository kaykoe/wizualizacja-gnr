import io
import os
import pandas as pd
import numpy as np
import FreeSimpleGUI as sg
from matplotlib import pyplot as plt

# TODO: split up into more files, this is getting messy


def get_load_df(
    turnaround_time_file_path: str, intensity_time_file_path: str
) -> pd.DataFrame:
    """
    This function takes in paths to two files, one containing turnaround times and the other containing request intensities.
    It returns a DataFrame with the minute, intensity and load columns.
    The load column is calculated as the product of the intensity and the average turnaround time.
    """

    def calculate_average_turnaround_time(path: str) -> float | None:
        """
        This function takes in a path to a file containing turnaround times and returns the average turnaround time.
        The file must be formated in a way where the times are provided one per line and nothing else.
        """
        try:
            df = pd.read_table(path, header=None, index_col=False)
            return df.mean()[0]
        except Exception:
            sg.popup_error(
                "Błąd podczas przetwarzania pliku z czasami obsługi, niepoprawny format"
            )
            return None

    def get_request_intensity_df(path: str) -> pd.DataFrame | None:
        """
        This function takes in a path to a file containing request intensities and returns a DataFrame with the minute and intensity columns.
        The file must be formated in a way where the minute and intensity are provided in two columns separated by whitespace.
        """
        try:
            return pd.read_table(
                path,
                decimal=",",
                header=None,
                sep="\s+",
                names=["minute", "intensity"],
                dtype={"minute": np.int32, "intensity": np.float32},
            )
        except Exception:
            sg.popup_error(
                "Błąd podczas przetwarzania pliku z intensywnością zgłoszeń, niepoprawny format"
            )
            return None

    avg_ta = calculate_average_turnaround_time(turnaround_time_file_path)
    # Go back to the default file if there was an error
    if avg_ta is None:
        turnaround_time_file = "czas.txt"
        avg_ta = calculate_average_turnaround_time(turnaround_time_file)

    # Go back to the default file if there was an error
    req_df = get_request_intensity_df(intensity_time_file_path)
    if req_df is None:
        intensity_time_file = "int.txt"
        req_df = get_request_intensity_df(intensity_time_file)
    return req_df.assign(load=req_df["intensity"] * avg_ta)


def get_GNR(load_df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement this
    pass


def get_plot(load_df: pd.DataFrame) -> plt.Figure:
    # TODO: add GNR to the plot
    plot = load_df.plot(
        x="minute",
        y="load",
        title="Obciążenie systemu",
        figsize=tuple((x / 100 for x in size)),
    ).get_figure()
    plot.set_dpi(100)
    plot.set_layout_engine("constrained")
    return plot


def update_image():
    load_df = get_load_df(turnaround_time_file, intensity_time_file)
    plot = get_plot(load_df)
    img = io.BytesIO()
    plot.savefig(img, format="png")
    window["image"].update(data=img.getvalue())


def is_valid_file(path: str) -> bool:
    return os.path.isfile(path) and path.endswith(".txt")


# TODO: embed default files into exe
turnaround_time_file = "czas.txt"
intensity_time_file = "int.txt"
size = (1280, 720)
sg.theme("LightGrey")

# TODO: add descriptions for different ways of calculating GNR to the help menu
menu_layout = [
    ["Plik", ["Otwórz", "Zamknij"]],
    [
        "Informacje",
        ["O programie", "Sposoby obliczania GNR", ["Wzór 1", "Wzór 2", "Wzór 3"]],
    ],
]

layout = [
    [sg.Menu(menu_layout)],
    [sg.VPush()],
    [sg.Push(), sg.Image(key="image", size=size), sg.Push()],
    [sg.VPush()],
]
window = sg.Window(
    "Wizualizacja GNR",
    layout,
    resizable=True,
    finalize=True,
    element_justification="center",
)

update_image()
window.refresh()
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Otwórz":
        popup_layout = [
            [
                sg.Text("Plik z czasami obsługi:"),
                sg.Input(key="time_file"),
                sg.FileBrowse(file_types=(("Text Files", "*.txt"),)),
            ],
            [
                sg.Text("Plik z intesywnością zgłoszeń"),
                sg.Input(key="int_file"),
                sg.FileBrowse(file_types=(("Text Files", "*.txt"),)),
            ],
            [
                sg.Push(),
                sg.Submit("Zatwierdź", size=(10, 1)),
                sg.Cancel("Anuluj", size=(10, 1)),
                sg.Push(),
            ],
        ]

        event, values = sg.Window(
            "Wybierz dane wejściowe",
            popup_layout,
            size=(610, 120),
            element_justification="right",
        ).read(close=True)

        if event == "Submit":
            not_selected: bool = (
                not values["Submit"]
                or (
                    not values["Submit"]["int_file"]
                    or not values["Submit"]["time_file"]
                )
                or (
                    values["Submit"]["int_file"] == ""
                    or values["Submit"]["time_file"] == ""
                )
            )
            if not_selected:
                sg.popup_error("Nie wybrano pliku/plików")
                continue

            if not is_valid_file(values["Submit"]["time_file"]):
                sg.popup_error(
                    "Niepoprawna ścieżka do pliku z czasami obsługi, upewnij się że plik istnieje i jest w formacie .txt"
                )
                continue
            if not is_valid_file(values["Submit"]["int_file"]):
                sg.popup_error(
                    "Niepoprawna ścieżka do pliku z intensywnością zgłoszeń, upewnij się że plik istnieje i jest w formacie .txt"
                )
                continue
            turnaround_time_file = values["Submit"]["time_file"]
            intensity_time_file = values["Submit"]["int_file"]
        update_image()
        continue

    if event == "Zamknij":
        turnaround_time_file = "czas.txt"
        intensity_time_file = "int.txt"
        update_image()
        continue
