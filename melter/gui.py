import flet as ft
from functools import lru_cache
from mtpy.meltpool_tomography import MeltpoolTomography
import panel as pn
from time import sleep


URL = "localhost"
PORT = 1234
PBAR_WIDTH = 256


def main(page: ft.Page):
    page.title = "Minimal GUI Test"

    page.window_height = 100.0
    page.window_width = 512.0
    page.max_height = 100.0
    page.max_width = 512.0
    page.max_window_height = 100.0
    page.max_window_width = 512.0
    page.update()
    placeholder = ft.Row(
        [ft.ProgressRing()],
        alignment=ft.MainAxisAlignment.CENTER,
        height=100,
        width=512,
    )
    page.add(placeholder)
    page.window_height = 100.0
    page.window_width = 512.0
    sleep(0.1)
    page.update()

    # webview = ft.WebView(f"http://{URL}:{PORT}")
    pbar = ft.ProgressBar(width=PBAR_WIDTH)
    pbar.value = 0

    def pbar_wrapper(iterator, length=None, *args, **kwargs):
        l = length if length is not None else len(iterator)
        increment = PBAR_WIDTH // l
        pbar.value = 0
        for i in iterator:
            page.update()
            yield i
            pbar.value += increment
            page.update()
        pbar.value = PBAR_WIDTH
        page.update()

    @lru_cache(maxsize=1)
    def get_engine():
        mt = MeltpoolTomography()
        mt.loader.progressbar = pbar_wrapper
        return mt

    mt = get_engine()

    def open_filepicker(_):
        return file_picker.get_directory_path()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        mt.read_layers(e.path)
        plot = mt.scatter2d()
        scatter_pane = pn.pane.HoloViews(plot)
        pn.serve(scatter_pane, PORT, URL, show=True)
        page.update()


    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    file_picker_button = ft.ElevatedButton(
        "Choose files...",
        on_click=open_filepicker,
    )

    page.remove(placeholder)
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        file_picker_button,
                        pbar,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                # webview,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    sleep(0.1)

    page.window_height = 100.0
    page.window_width = 512.0
    page.update()
