import io
import os
import shutil
from enum import StrEnum
from os import path
import pandas as pd
import numpy as np
import FreeSimpleGUI as sg
from matplotlib import pyplot as plt
import typing

# TODO: add the additional days generation from the data provided
# TODO: add 1(minimum) to 3(absolute maximum) ways to calculate the GNR

bundle_path = path.abspath(path.dirname(__file__))
default_turnaround_time_file = path.join(bundle_path, "czas.txt")
int_file = path.join(bundle_path, "int.txt")
def_int_dir = path.join(bundle_path, "int_files")

turnaround_time_file = default_turnaround_time_file
int_dir = def_int_dir

size = (1280, 720)

class Tab(StrEnum):
    WIZUALIZACJA = "wizualizacja"

tab_img_dict: typing.Dict[Tab, str] = {tab: tab.value + "_image" for tab in Tab}
current_tab: Tab = Tab.WIZUALIZACJA

window: sg.Window

def get_intensity_df(file_path: str) -> pd.DataFrame | None:
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
            sep="\\s+",
            names=["intensity"],
            dtype={"intensity": np.float32},
        )
        idx = pd.Index((i + 1 for i in range(int(df.index.max()))))
        df = df.reindex(
            index=idx,
            fill_value=0,
        )
        df.insert(0, "minute", idx)
        return df
    except Exception:
        sg.popup_error(
            "Błąd podczas przetwarzania pliku z intensywnością zgłoszeń, niepoprawny format"
        )
        return None

def get_load_dfs() -> list[pd.DataFrame]:
    """
    This function takes in paths to two files, one containing turnaround times and the other containing request intensities.
    It returns a DataFrame with the minute, intensity and load columns.
    The load column is calculated as the product of the intensity and the average turnaround time.
    """

    def calculate_average_turnaround_time() -> float | None:
        """
        This function takes in a path to a file containing turnaround times and returns the average turnaround time.
        The file must be formated in a way where the times are provided one per line and nothing else.
        """
        try:
            df = pd.read_table(turnaround_time_file, header=None, index_col=False)
            return df.mean()[0]
        except Exception:
            sg.popup_error(
                "Błąd podczas przetwarzania pliku z czasami obsługi, niepoprawny format"
            )
            return None

    def get_int_dfs() -> list[pd.DataFrame] | None:
        """
        This function takes in a directory containing files with request intensities and returns a list of DataFrames with the minute, intensity and load columns.
        The load column is calculated as the product of the intensity and the average turnaround time.
        """
        dfs = []
        for file in os.listdir(int_dir):
            if file.endswith(".txt"):
                df = get_intensity_df(path.join(int_dir, file))
                if df is not None:
                    dfs.append(df.assign(load=df["intensity"] * avg_ta))
                else:
                    sg.popup_error(
                        f"Błąd podczas przetwarzania pliku z intensywnością zgłoszeń {file}, niepoprawny format"
                    )
                    dfs = None
                    break
        return dfs

    avg_ta = calculate_average_turnaround_time()
    int_dfs = get_int_dfs()

    # Go back to the default file if there was an error
    if avg_ta is None or int_dfs is None:
        global turnaround_time_file
        global int_dir
        turnaround_time_file = default_turnaround_time_file
        int_dir = def_int_dir
        avg_ta = calculate_average_turnaround_time()
        int_dfs = get_int_dfs()
    return [int_df.assign(load=int_df["intensity"] * avg_ta) for int_df in int_dfs]

def gen_dfs(df: pd.DataFrame, days: int) -> list[pd.DataFrame]:
    pass

def preprocess_default_data():
    int_df = get_intensity_df(int_file)
    # dfs = gen_dfs(int_df, 7)
    dfs = [int_df] # Placeholder
    if not path.exists(def_int_dir):
        os.mkdir(def_int_dir)
    for i, df in enumerate(dfs):
        df.to_csv(
            path.join(def_int_dir, f"int_{i}.txt"),
            sep="\t",
            decimal=",",
            index=False,
            header=False,
        )

def setup():
    sg.theme("LightGrey")

    menu_layout = [
        ["Plik", ["Otwórz", "Zamknij"]],
        ["Pomoc", ["O programie"]],
    ]

    tab_1_layout = [
        [sg.VPush()],
        [sg.Push(), sg.Image(key=tab_img_dict.get(Tab.WIZUALIZACJA), size=size), sg.Push()],
        [sg.VPush()],
    ]
    # TODO: add more tabs
    # TODO: description tab
    # noinspection PyTypeChecker
    layout = [
        [sg.Menu(menu_layout)],
        [
            sg.TabGroup(
                [[sg.Tab(Tab.WIZUALIZACJA.value, tab_1_layout, key=Tab.WIZUALIZACJA)]],
                expand_x=True,
                expand_y=True,
                enable_events=True,
            )
        ],
    ]

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
    def is_valid_dir(dir_path: str) -> bool:
        return path.isdir(dir_path)
    def contains_txts(dir_path: str) -> bool:
        txts = list(filter(lambda filename: filename.endswith(".txt"), os.listdir(dir_path)))
        return len(txts) > 0

    not_selected: bool = (
        not vals["int_dir"]
        or not vals["time_file"]
        or vals["int_dir"] == ""
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
    if not is_valid_dir(vals["int_dir"]):
        sg.popup_error(
            "Niepoprawna ścieżka do katalogu z intensywnością zgłoszeń, upewnij się że katalog istnieje"
        )
        return None
    if not contains_txts(vals["int_dir"]):
        sg.popup_error(
            "Nie znaleziono plików z intensywnością zgłoszeń w podanym katalogu"
        )
        return None
    return vals["time_file"], vals["int_dir"]


def get_GNR(load_dfs: list[pd.DataFrame]) -> typing.Tuple[int, int]:
    # TODO: implement this, if multiple ways of calculating, just get it from the tab dict
    pass


def get_plot(load_dfs: list[pd.DataFrame]) -> plt.Figure:
    # GNR = get_GNR(load_dfs)
    GNR = (600, 660)  # Placeholder

    load_df = pd.concat(load_dfs).groupby("minute", as_index=False).mean()
    gnr_load = load_df[(load_df["minute"] >= GNR[0]) & (load_df["minute"] <= GNR[1])][
        "load"
    ].sum()

    ax = load_df.plot(
        x="minute",
        y="load",
        title="Obciążenie systemu",
        figsize=tuple((x / 100 for x in size)),
        color="blue",
    )

    ax.set_xlabel("Czas (minuty)", fontsize=12)
    ax.set_ylabel("Obciążenie", fontsize=12)
    ax.set_title("Obciążenie systemu", fontsize=14, fontweight="bold")
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)


    # Add rectangle highlighting GNR
    ax.axvspan(GNR[0], GNR[1], color="red", alpha=0.3, label=f"GNR ({GNR[0]} - {GNR[1]})")

    ax.text(
        (GNR[0] + GNR[1]) / 2,
        load_df["load"].max() * 0.1,
        f"Obciążenie w GNR: {gnr_load:.2f}",
        color="black",
        ha="center",
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"),
    )
    ax.legend(loc="upper left", fontsize=10, frameon=True)

    plot = ax.get_figure()
    plot.set_dpi(100)
    plot.set_layout_engine("constrained")
    return plot


def update_image():
    image = tab_img_dict.get(current_tab)
    load_dfs = get_load_dfs()
    plot = get_plot(load_dfs)
    img = io.BytesIO()
    plot.savefig(img, format="png")
    window[image].update(data=img.getvalue())

def file_popup():
    popup_layout = [
        [
            sg.Text("Plik z czasami obsługi:"),
            sg.Input(key="time_file"),
            sg.FileBrowse(file_types=(("Text Files", "*.txt"),)),
        ],
        [
            sg.Text("Plik z intensywnością zgłoszeń"),
            sg.Input(key="int_dir"),
            sg.FolderBrowse(),
        ],
        [
            sg.Push(),
            sg.Submit("Zatwierdź", size=(10, 1)),
            sg.Cancel("Anuluj", size=(10, 1)),
            sg.Push(),
        ],
    ]
    return sg.Window(
        "Wybierz dane wejściowe",
        popup_layout,
        element_justification="right",
        keep_on_top=True,
    ).read(close=True)

preprocess_default_data()
setup()
update_image()
window.refresh()

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Otwórz":

        event, values = file_popup()

        if event == "Zatwierdź":
            filenames = get_filenames_from_popup(values)
            if filenames is None:
                continue
            turnaround_time_file, int_dir = filenames

        if current_tab in tab_img_dict:
            update_image()
        continue

    if event == "Zamknij":
        turnaround_time_file = default_turnaround_time_file
        int_dir = def_int_dir

        if current_tab in tab_img_dict:
            update_image()
        continue

    if event in tab_img_dict:
        current_tab = event
        update_image()

# cleanup
shutil.rmtree(def_int_dir)
