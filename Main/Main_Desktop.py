#!/usr/bin/env python3
# *_* coding: utf-8 *_*

# Kivy module imports
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
# Other python module imports
from Common.MTPy_Modified import MT_Modded as MeltpoolTomography
from Common.threading_decorators import run_in_thread
from Data import Calibration, ThresholdFunctions
from pathlib import Path
from types import SimpleNamespace, FunctionType
from ast import literal_eval
from contextlib import redirect_stdout

# Load kv files
Builder.load_file("Templates/melter_desktop.kv")


# This class contains the main window code
class Main(Screen):
    # Declare variables to be usable in kivy script
    mtpy = ObjectProperty(MeltpoolTomography())
    cache = ObjectProperty(SimpleNamespace())

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        # Then, initialize an MTPy object for data processing
        self.mtpy = MeltpoolTomography(quiet=True)
        # list of shared choosers to keep the same between tabs
        shared_io_choosers = ["io_chooser_dataloading",
                              "io_chooser_buildplate",
                              "io_chooser_sampledetection",
                              "io_chooser_persample",
                              "io_chooser_datasheet"]
        shared_io_choosers = [self.ids[x] for x in shared_io_choosers]
        # Link progress bars in document to their associated functions
        self.mtpy.progress_bars["read_layers"] = self.ids.read_layers_progbar
        self.mtpy.progress_bars["apply_calibration_curve"] = self.ids.cal_curve_progbar  # noqa
        self.mtpy.progress_bars["_layers_to_figures"] = self.ids.layers_to_figures_progbar  # noqa
        self.mtpy.progress_bars["_layers_to_3dplot"] = self.ids.layers_to_3dplot_progbar  # noqa
        self.mtpy.progress_bars["_layers_to_3dplot_interactive"] = self.ids.layers_to_3dplot_interactive_progbar  # noqa
        self.mtpy.progress_bars["samples_to_figures"] = self.ids.samples_to_figures_progbar  # noqa
        self.mtpy.progress_bars["samples_to_3dplot"] = self.ids.samples_to_3dplot_progbar  # noqa
        self.mtpy.progress_bars["samples_to_3dplot_interactive"] = self.ids.samples_to_3dplot_interactive_progbar  # noqa
        self.mtpy.progress_bars["separate_samples"] = self.ids.kmeans_separate_samples_progbar  # noqa
        # self.mtpy.progress_bars["threshold_all_layers"] = self.ids.avgspeed_threshold_progbar  # noqa
        # self.mtpy.progress_bars["threshold_all_layers"] = self.ids.avgtemp_threshold_progbar  # noqa
        self.mtpy.progress_bars["temp_data_to_csv"] = self.ids.kmeans_separate_samples_progbar  # noqa
        # Starting items in cache
        starting_cache = {
            # Shared variables
            "shared_io_choosers": shared_io_choosers,
            "in_path": str(Path("~").expanduser()),  # path to input data
            "out_path": str(Path("~").expanduser()),  # path to output data
            "last_loaded_path": False,  # path to last loaded
            "calibration_curve": False,  # last cal curve used
            # Dropdown population lists
            "printer_types": ("None", "3D Systems", "Aconity", "GE Additive", "Renishaw", "Stratasys"),
            "calibration_curves": [v() for k, v in Calibration.__dict__.items() if "__" not in k],
            "static_fileformats": ("png", "pdf", "ps", "eps", "svg"),  # Allowed static formats
            "thresh_functions": [v() for k, v in ThresholdFunctions.__dict__.items() if "__" not in k],
            # Progress Bars
            "progress_bars": self.mtpy.progress_bars
        }
        self.cache = SimpleNamespace(**starting_cache)
        # Make sure each shared io chooser is aware of others and parent app
        for chooser in self.cache.shared_io_choosers:
            chooser.cache.shared_io_choosers = \
                [x for x in self.cache.shared_io_choosers if x != chooser]
            chooser.cache.parent_app = self
        # Next, populate dropdowns
        # The dropdown for selecting the printer type
        self.ids.printer_type_dropdown.populate_dropdown(self.cache.printer_types)
        # The dropdown for calibration curves
        self.ids.calibration_curve_dropdown.populate_dropdown(self.cache.calibration_curves)
        # The dropdowns for matplotlib filetype options
        static_filetype_dropdowns = (
            self.ids.layers_to_figures_filetype_dropdown,
            self.ids.layers_to_3dplot_filetype_dropdown,
            self.ids.samples_to_figures_filetype_dropdown,
            self.ids.samples_to_3dplot_filetype_dropdown,
        )
        for dropdown in static_filetype_dropdowns:
            dropdown.populate_dropdown(self.cache.static_fileformats)
        # The dropdowns for the thresholding functions
        self.ids.avgtemp_thresh_function_dropdown.populate_dropdown(self.cache.thresh_functions)

    # Property returns a string summarising the status of data processing
    @property
    def data_status(self):
        # if data_dict is present, generate string for data_dict info
        if hasattr(self.mtpy, "data_dict"):
            data_dict = self.mtpy.data_dict
            if len(data_dict) > 0:
                if "layers" not in locals():
                    layers = len(data_dict)
                points_per_layer = round(sum((points.shape[1] for layer, points
                                              in data_dict.items()))
                                         / layers)
                layers_string = f"Layers: {layers}\nAverage Points Per Layer: {points_per_layer}"  # noqa
            else:
                return "No data loaded!"
        # if sample_dict is present, generate string for it
        else:
            layers_string = "Layer data not loaded..."

        if hasattr(self.mtpy, "sample_dict"):
            sample_dict = self.mtpy.sample_dict
            if "layers" not in locals():
                layers = len(sample_dict[sample_dict.keys()[0]])
                if layers_string == "Layer data not loaded...":
                    layers_string += f"Layers: {layers}"
            num_samples = len(sample_dict)
            points_per_sample = round(sum((sum(len(points)
                                               for layer, points in
                                               layer_data.items()) / layers
                                           for sample, layer_data in
                                           sample_dict.items()))
                                      / num_samples)
            samples_string = f"Number of Samples: {num_samples}\nAverage Points Per Sample: {points_per_sample}"  # noqa
        else:
            samples_string = "Samples not separated..."

        # Combine to form overall status string
        outstring = f"{layers_string}\n{samples_string}"
        # and add additional info at the end if present
        if self.cache.calibration_curve:
            outstring += f"\nCalibration Curve: {self.cache.calibration_curve}" # noqa
        return outstring

    # Updates data status displayed in data loading tab
    def update_data_status(self):
        self.ids.dataloading_display.text = self.data_status

    # Parses text field inputs into **kwargs
    def parse_kwargs(self, paramstring: str) -> dict:
        if paramstring == "":
            return dict()
        parsed = []
        neststring = ""  # this string keeps track of level and type of nesting
        prev_split = 0  # keeps track of previous split point
        # This loop splits string at un-nested commas
        for i, c in enumerate(paramstring):
            if c == "," and neststring == "":
                parsed.append(paramstring[prev_split:i])
                prev_split = i + 1
            elif c in ("'", '"'):
                if len(neststring) > 0:
                    if c == neststring[-1]:
                        neststring = neststring[:-1]
                    else:
                        neststring += c
                else:
                    neststring += c
            elif c in ("(", "{", "["):
                neststring += c
            elif c in (")", "}", "]"):
                if (c == ")" and neststring[-1] == "("
                        or c == "}" and neststring[-1] == "{"
                        or c == "]" and neststring[-1] == "["):
                    neststring = neststring[:-1]
        parsed.append(paramstring[prev_split:])

        # parse into pairs of keywords and objects
        parsed = (str.strip(x) for x in parsed)
        parsed = (x.split("=") for x in parsed)
        parsed = ((str.strip(y) for y in x) for x in parsed)
        # Finally, interpret objects in the loop below
        parsed = {kw: literal_eval(val) for kw, val in parsed}

        return parsed

    # Parses layer selection into a layer filter
    def parse_filter(self, filterstring: str) -> FunctionType:
        filterstring = filterstring.strip()
        if filterstring.isdigit():
            return lambda x: x == int(filterstring)
        elif ":" in filterstring:
            return lambda x: x in range(*(int(y) for y in filterstring.split(":")))
        elif "," in filterstring:
            return lambda x: x in (int(y) for y in filterstring.split(","))
        else:
            return lambda x: True

    # This function loads input data only if not already loaded
    @run_in_thread
    def load_data(self):
        if self.cache.in_path != self.cache.last_loaded_path:
            self.mtpy.data_path = self.cache.in_path
            self.cache.last_loaded_path = self.cache.in_path
            self.mtpy.read_layers()
            self.update_data_status()

    # applies calibration curve if has changed
    # NOTE: relies on eval! Function may be dangerous
    @run_in_thread
    def apply_calibration_curve(self):
        cal_curve_selection = self.ids.calibration_curve_dropdown.current_selection
        if (cal_curve_selection.name == "Custom"):
            equation = self.ids.calibration_curve.text
            equation = equation.replace(" ", "")
            if ((equation != self.cache.calibration_curve)
                    and (equation != "y=x")
                    and (equation[:2] == "y=")):
                def func(x):
                    return eval(equation[2:])
                self.mtpy.apply_calibration_curve(func)
                self.cache.calibration_curve = equation
                self.update_data_status()
        else:
            if cal_curve_selection is not self.cache.calibration_curve:
                self.mtpy.apply_calibration_curve(cal_curve_selection)
                self.cache.calibration_curve = cal_curve_selection
                self.update_data_status()

    # A wrapper function translating application state into a call to the
    # mtpy function layers_to_figures
    @run_in_thread
    def layers_to_figures(self):
        # get filetype and if not allowed replace with default (png)
        filetype = self.ids.layers_to_figures_filetype_dropdown.text
        if filetype not in self.cache.static_fileformats:
            filetype = "png"
        # get checkbox parameters
        plot_w = self.ids.layers_to_figures_plot_w.active
        colorbar = self.ids.layers_to_figures_colorbar.active
        # then parse kwarg params
        figureparams = self.parse_kwargs(self.ids.layers_to_figures_figureparams.text)
        scatterparams = self.parse_kwargs(self.ids.layers_to_figures_plotparams.text)
        self.mtpy.layers_to_figures(self.cache.out_path,
                                    filetype=filetype,
                                    plot_w=plot_w,
                                    colorbar=colorbar,
                                    figureparams=figureparams,
                                    scatterparams=scatterparams)

    # A wrapper function translating application state into a call to the
    # mtpy function layers_to_3dplot
    @run_in_thread
    def layers_to_3dplot(self):
        # get filetype and if not allowed replace with default (png)
        filetype = self.ids.layers_to_3dplot_filetype_dropdown.text
        if filetype not in self.cache.static_fileformats:
            filetype = "png"
        # get checkbox parameters
        plot_w = self.ids.layers_to_3dplot_plot_w.active
        colorbar = self.ids.layers_to_3dplot_colorbar.active
        # then parse kwarg params
        figureparams = self.parse_kwargs(
            self.ids.layers_to_3dplot_figureparams.text)
        plotparams = self.parse_kwargs(
            self.ids.layers_to_3dplot_plotparams.text)
        self.mtpy.layers_to_3dplot(self.cache.out_path,
                                   filetype=filetype,
                                   plot_w=plot_w,
                                   colorbar=colorbar,
                                   figureparams=figureparams,
                                   plotparams=plotparams)

    # A wrapper function translating application state into a call to the
    # mtpy function layers_to_3dplot_interactive
    @run_in_thread
    def layers_to_3dplot_interactive(self):
        # get checkbox parameters
        plot_w = self.ids.layers_to_3dplot_interactive_plot_w.active
        sliceable = self.ids.layers_to_3dplot_interactive_sliceable.active
        downsampling = self.ids.layers_to_3dplot_interactive_downsampling.text
        if downsampling == "":
            downsampling = 1
        else:
            downsampling = int(downsampling)
        # then parse kwarg params
        plotparams = self.parse_kwargs(self.ids.layers_to_3dplot_interactive_plotparams.text)  # noqa
        self.mtpy.layers_to_3dplot_interactive(self.cache.out_path,
                                               plot_w=plot_w,
                                               sliceable=sliceable,
                                               downsampling=downsampling,
                                               plotparams=plotparams)

    # A wrapper function translating application state into a call to the
    # mtpy function samples_to_figures
    @run_in_thread
    def samples_to_figures(self):
        # get filetype and if not allowed replace with default (png)
        filetype = self.ids.samples_to_figures_filetype_dropdown.text
        if filetype not in self.cache.static_fileformats:
            filetype = "png"
        # get checkbox parameters
        plot_w = self.ids.samples_to_figures_plot_w.active
        colorbar = self.ids.samples_to_figures_colorbar.active
        # then parse kwarg params
        figureparams = self.parse_kwargs(
            self.ids.samples_to_figures_figureparams.text)
        scatterparams = self.parse_kwargs(
            self.ids.samples_to_figures_plotparams.text)
        self.mtpy.samples_to_figures(self.cache.out_path,
                                     filetype=filetype,
                                     plot_w=plot_w,
                                     colorbar=colorbar,
                                     figureparams=figureparams,
                                     scatterparams=scatterparams)

    # A wrapper function translating application state into a call to the
    # mtpy function samples_to_3dplot
    @run_in_thread
    def samples_to_3dplot(self):
        # get filetype and if not allowed replace with default (png)
        filetype = self.ids.samples_to_3dplot_filetype_dropdown.text
        if filetype not in self.cache.static_fileformats:
            filetype = "png"
        # get checkbox parameters
        plot_w = self.ids.samples_to_3dplot_plot_w.active
        colorbar = self.ids.samples_to_3dplot_colorbar.active
        # then parse kwarg params
        figureparams = self.parse_kwargs(
            self.ids.samples_to_3dplot_figureparams.text)
        plotparams = self.parse_kwargs(
            self.ids.samples_to_3dplot_plotparams.text)
        self.mtpy.samples_to_3dplot(self.cache.out_path,
                                    filetype=filetype,
                                    plot_w=plot_w,
                                    colorbar=colorbar,
                                    figureparams=figureparams,
                                    plotparams=plotparams)

    # A wrapper function translating application state into a call to the
    # mtpy function layers_to_3dplot_interactive
    @run_in_thread
    def samples_to_3dplot_interactive(self):
        # get checkbox parameters
        plot_w = self.ids.samples_to_3dplot_interactive_plot_w.active
        sliceable = self.ids.samples_to_3dplot_interactive_sliceable.active
        downsampling = self.ids.samples_to_3dplot_interactive_downsampling.text
        if downsampling == "":
            downsampling = 1
        else:
            downsampling = int(downsampling)
        # then parse kwarg params
        plotparams = self.parse_kwargs(self.ids.samples_to_3dplot_interactive_plotparams.text)  # noqa
        self.mtpy.samples_to_3dplot_interactive(self.cache.out_path,
                                                plot_w=plot_w,
                                                sliceable=sliceable,
                                                downsampling=downsampling,
                                                plotparams=plotparams)

    # A wrapper function translating application state into a call to the
    # mtpy module to threshold all layers based on speed
    @run_in_thread
    def avgspeed_threshold(self):
        # get input parameters
        thresh_percent = float(self.ids.avgspeed_thresh_thresh_percent.text)
        avgof = int(self.ids.avgspeed_thresh_avgof.text)
        # Link to progress bar (at time of call since this bar is shared)
        self.mtpy.progress_bars["threshold_all_layers"] = self.ids.avgspeed_threshold_progbar  # noqa
        # then call the function
        self.mtpy.threshold_all_layers(
            self.mtpy.avgspeed_threshold,
            {
                "threshold_percent": thresh_percent,
                "avgof": avgof
            }
        )

    # A wrapper function translating application state into a call to the
    # mtpy module to threshold all layers based on temperature
    @run_in_thread
    def avgtemp_threshold(self):
        # get filetype and if not allowed replace with default (png)
        thresh_function = self.ids.avgtemp_thresh_function_dropdown.text
        if thresh_function not in self.cache.thresh_functions.keys():
            thresh_function = ">"
        # get threshold percentage
        thresh_percent = float(self.ids.avgtemp_thresh_thresh_percent.text)
        # Link to progress bar (at time of call since this bar is shared)
        self.mtpy.progress_bars["threshold_all_layers"] = self.ids.avgtemp_threshold_progbar  # noqa
        # then call the function
        self.mtpy.threshold_all_layers(
            self.mtpy.avgw_threshold,
            {
                "threshold_percent": thresh_percent,
                "comparison_func": self.cache.thresh_functions[thresh_function]
            }
        )

    @run_in_thread
    def separate_samples(self):
        # get input parameters
        nsamples = int(self.ids.kmeans_nsamples.text)
        # if only 0 or 1 samples, no need to separate
        if nsamples == 0 or nsamples == 1:
            return
        console_io_buffer = self.ids.kmeans_separate_console_output.io_buffer
        # Temporarily unmute mtpy for console output
        self.mtpy.quiet = False
        with redirect_stdout(console_io_buffer):
            self.mtpy.detect_samples(nsamples)
            print("\nSample detection complete!\n(Separation progress on bar above)")  # noqa
        # Then, remute once finished
        self.mtpy.quiet = True
        # Separate samples. Should use progbar so no need for teminal
        self.mtpy.separate_samples()
        # Finally, update the status string
        self.update_data_status()

    # This function generates datasheets
    @run_in_thread
    def temp_data_to_csv(self):
        confidence_interval = self.ids.temp_data_to_csv_confinterval
        confidence_interval = confidence_interval.strip()
        if confidence_interval.isdigit():
            confidence_interval = float(confidence_interval)
        else:
            confidence_interval = 0.95
        self.mtpy.temp_data_to_csv(f"{self.cache.out_path}",
                                   layers=self.ids.temp_data_to_csv_layers,
                                   samples=self.ids.temp_data_to_csv_samples,
                                   confidence_interval=confidence_interval)
