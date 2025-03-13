import pandas as pd
import numpy as np
import FreeSimpleGUI as sg
from matplotlib import pyplot as plt


def get_load_df(
    turnaround_time_file_path: str, intensity_time_file_path: str
) -> pd.DataFrame:
    """
    This function takes in paths to two files, one containing turnaround times and the other containing request intensities.
    It returns a DataFrame with the minute, intensity and load columns.
    The load column is calculated as the product of the intensity and the average turnaround time.
    """

    def calculate_average_turnaround_time(path: str) -> float:
        """
        This function takes in a path to a file containing turnaround times and returns the average turnaround time.
        The file must be formated in a way where the times are provided one per line and nothing else.
        """
        df = pd.read_table(path, header=None, index_col=False)
        return df.mean()[0]

    def get_request_intensity_df(path: str) -> pd.DataFrame:
        """
        This function takes in a path to a file containing request intensities and returns a DataFrame with the minute and intensity columns.
        The file must be formated in a way where the minute and intensity are provided in two columns separated by whitespace.
        """
        return pd.read_table(
            path,
            decimal=",",
            header=None,
            sep="\s+",
            names=["minute", "intensity"],
            dtype={"minute": np.int32, "intensity": np.float32},
        )

    avg_ta = calculate_average_turnaround_time(turnaround_time_file)
    req_df = get_request_intensity_df(intensity_time_file)
    return req_df.assign(load=req_df["intensity"] * avg_ta)


def get_GNR(load_df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement this
    return None


def get_plot(load_df: pd.DataFrame) -> plt.Figure:
    # TODO: implement this
    return None


turnaround_time_file = "czas.txt"
intensity_time_file = "int.txt"

load_df = get_load_df(turnaround_time_file, intensity_time_file)

# TODO: add descriptions for different ways of calculating GNR to the help menu
menu_layout = [["Plik", ["Otwórz", "Zamknij"]], ["Pomoc", ["Pomoc", "O programie"]]]
layout = [[sg.Menu(menu_layout)], [sg.Canvas()]]
# TODO: implement plot rendering inside the canvas

plot = get_plot(load_df)

window = sg.Window("Wizualizacja GNR", layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Otwórz":
        popup_layout = [
            [
                sg.Text("Plik z czasami obsługi:", size=(8, 1)),
                sg.Input(),
                sg.FileBrowse(),
            ],
            [
                sg.Text("Plik z intesywnością zgłoszeń", size=(8, 1)),
                sg.Input(),
                sg.FileBrowse(),
            ],
            [sg.Submit(), sg.Cancel()],
        ]

        popup_window = sg.Window("Wybierz dane wejściowe", popup_layout)

        _, values = popup_window.read()
        turnaround_time_file = values[0]
        intensity_time_file = values[1]
        popup_window.close()
        load_df = get_load_df(turnaround_time_file, intensity_time_file)
        # rerender here
        continue

    if event == "Zamknij":
        turnaround_time_file = "czas.txt"
        intensity_time_file = "int.txt"
        load_df = get_load_df(turnaround_time_file, intensity_time_file)
        # rerender here
        continue
