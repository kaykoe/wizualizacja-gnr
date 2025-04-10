import io
from os import path
import pandas as pd
import numpy as np
import FreeSimpleGUI as sg
from matplotlib import pyplot as plt
import typing

# TODO: add zero's where the minutes are missing -> karol
# TODO: add the possibility to load in a full directory of intensity files -> karol
# TODO: add the additional days generation from the data provided
# TODO: add 1(minimum) to 3(absolute maximum) ways to calculate the GNR

bundle_path: str = path.abspath(path.dirname(__file__))
default_turnaround_time_file = path.join(bundle_path, "czas.txt")
turnaround_time_file = default_turnaround_time_file
default_intensity_time_file = path.join(bundle_path, "int.txt")
intensity_time_file = default_intensity_time_file

size = (1280, 720)
current_tab: str = "wizualizacja"

window: sg.Window
tab_img_dict: typing.Dict[str, str]


def setup():
    sg.theme("LightGrey")

    menu_layout = [
        ["Plik", ["Otwórz", "Zamknij"]],
        ["Pomoc", ["O programie"]],
    ]

    tab_1_layout = [
        [sg.VPush()],
        [sg.Push(), sg.Image(key="wizualizacja_image", size=size), sg.Push()],
        [sg.VPush()],
    ]
    # TODO: add more tabs
    # TODO: description tab
    layout = [
        [sg.Menu(menu_layout)],
        [
            sg.TabGroup(
                [[sg.Tab("Wizualizacja", tab_1_layout, key="wizualizacja")]],
                expand_x=True,
                expand_y=True,
                enable_events=True,
            )
        ],
    ]
    global tab_img_dict
    tab_img_dict = {"wizualizacja": "wizualizacja_image"}

    global window
    window = sg.Window(
        "Wizualizacja GNR",
        layout,
        resizable=True,
        finalize=True,
        element_justification="center",
    )


def get_filenames_from_popup(vals: typing.Dict[str, str]) -> (
    str,
    str,
) or None:
    def is_valid_file(file_path: str) -> bool:
        return path.isfile(file_path) and file_path.endswith(".txt")

    not_selected: bool = (
        not vals["int_file"]
        or not vals["time_file"]
        or vals["int_file"] == ""
        or vals["time_file"] == ""
    )
    if not_selected:
        sg.popup_error("Nie wybrano pliku/plików")
        return None

    if not is_valid_file(vals["time_file"]):
        sg.popup_error(
            "Niepoprawna ścieżka do pliku z czasami obsługi, upewnij się że plik istnieje i jest w formacie .txt"
        )
        return None
    if not is_valid_file(vals["int_file"]):
        sg.popup_error(
            "Niepoprawna ścieżka do pliku z intensywnością zgłoszeń, upewnij się że plik istnieje i jest w formacie .txt"
        )
        return None
    return vals["time_file"], vals["int_file"]


def get_load_df(
    turnaround_time_file_path: str, intensity_time_file_path: str
) -> pd.DataFrame:
    """
    This function takes in paths to two files, one containing turnaround times and the other containing request intensities.
    It returns a DataFrame with the minute, intensity and load columns.
    The load column is calculated as the product of the intensity and the average turnaround time.
    """

    def calculate_average_turnaround_time(file_path: str) -> float | None:
        """
        This function takes in a path to a file containing turnaround times and returns the average turnaround time.
        The file must be formated in a way where the times are provided one per line and nothing else.
        """
        try:
            df = pd.read_table(file_path, header=None, index_col=False)
            return df.mean()[0]
        except Exception:
            sg.popup_error(
                "Błąd podczas przetwarzania pliku z czasami obsługi, niepoprawny format"
            )
            return None

    def get_request_intensity_df(file_path: str) -> pd.DataFrame | None:
        """
        This function takes in a path to a file containing request intensities and returns a DataFrame with the minute and intensity columns.
        The file must be formated in a way where the minute and intensity are provided in two columns separated by whitespace.
        """
        try:
            df = pd.read_table(
                file_path,
                index_col=0,
                decimal=",",
                header=None,
                sep="\s+",
                names=["intensity"],
                dtype={"intensity": np.float32},
            )
            idx = pd.Index((i + 1 for i in range(int(df.index.max()))))
            return df.reindex(
                index=idx,
                fill_value=0,
            )
        except Exception:
            sg.popup_error(
                "Błąd podczas przetwarzania pliku z intensywnością zgłoszeń, niepoprawny format"
            )
            return None

    avg_ta = calculate_average_turnaround_time(turnaround_time_file_path)
    # Go back to the default file if there was an error
    if avg_ta is None:
        global turnaround_time_file
        turnaround_time_file = default_turnaround_time_file
        avg_ta = calculate_average_turnaround_time(turnaround_time_file)

    # Go back to the default file if there was an error
    req_df = get_request_intensity_df(intensity_time_file_path)
    if req_df is None:
        global intensity_time_file
        intensity_time_file = default_intensity_time_file
        req_df = get_request_intensity_df(intensity_time_file)
    return req_df.assign(load=req_df["intensity"] * avg_ta)


def get_GNR(load_df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement this, if multiple ways of calculating, just get it from the tab dict
    pass


def get_plot(load_df: pd.DataFrame) -> plt.Figure:
    # TODO: add GNR to the plot -> karol
    # TODO: make the plot look better etc. -> karol
    plot = load_df.plot(
        x="minute",
        y="load",
        title="Obciążenie systemu",
        figsize=tuple((x / 100 for x in size)),
    ).get_figure()
    plot.set_dpi(100)
    plot.set_layout_engine("constrained")
    return plot


def update_image(key: str):
    load_df = get_load_df(turnaround_time_file, intensity_time_file)
    plot = get_plot(load_df)
    img = io.BytesIO()
    plot.savefig(img, format="png")
    window[key].update(data=img.getvalue())


setup()
update_image(tab_img_dict[current_tab])
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
                sg.Text("Plik z intensywnością zgłoszeń"),
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
            element_justification="right",
            keep_on_top=True,
        ).read(close=True)

        if event == "Zatwierdź":
            filenames = get_filenames_from_popup(values)
            if filenames is None:
                continue
            turnaround_time_file, intensity_time_file = filenames

        if tab_img_dict.get(current_tab) is not None:
            update_image(tab_img_dict[current_tab])
        continue

    if event == "Zamknij":
        turnaround_time_file = default_turnaround_time_file
        intensity_time_file = default_intensity_time_file

        if tab_img_dict.get(current_tab) is not None:
            update_image(tab_img_dict[current_tab])
        continue

    if tab_img_dict.get(event) is not None:
        current_tab = event
        update_image(tab_img_dict[current_tab])
