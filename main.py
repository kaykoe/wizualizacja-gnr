import io
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


turnaround_time_file = "czas.txt"
intensity_time_file = "int.txt"
size = (1280, 720)
sg.theme("LightGrey")

# TODO: add descriptions for different ways of calculating GNR to the help menu
menu_layout = [["Plik", ["Otwórz", "Zamknij"]], ["Pomoc", ["O programie"]]]
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
                sg.Input(),
                sg.FileBrowse(file_types=(("Text Files", "*.txt"),)),
            ],
            [
                sg.Text("Plik z intesywnością zgłoszeń"),
                sg.Input(),
                sg.FileBrowse(),
            ],
            [
                sg.Push(),
                sg.Submit("Zatwierdź", size=(10, 1)),
                sg.Cancel("Anuluj", size=(10, 1)),
                sg.Push(),
            ],
        ]

        popup_window = sg.Window(
            "Wybierz dane wejściowe",
            popup_layout,
            size=(610, 120),
            element_justification="right",
        )

        event, values = popup_window.read()
        if event == "Submit":
            # TODO: add validation
            turnaround_time_file = values[0]
            intensity_time_file = values[1]
        popup_window.close()
        update_image()
        continue

    if event == "Zamknij":
        turnaround_time_file = "czas.txt"
        intensity_time_file = "int.txt"
        update_image()
        continue
