import pyLIMA

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
import mpld3
from mpld3 import plugins
import cycler
from matplotlib.ticker import MaxNLocator
from bokeh.layouts import gridplot

from pyLIMA.fits import DE_fit
from pyLIMA.fits import TRF_fit
from pyLIMA.models import PSPL_model
from pyLIMA.models import FSPL_model
from pyLIMA.models import USBL_model, pyLIMA_fancy_parameters
from pyLIMA.outputs import pyLIMA_plots
from pyLIMA.toolbox import fake_telescopes, plots

from pyLIMA import event
from pyLIMA import telescopes

MARKER_SYMBOLS = np.array(
    [['o', '.', '*', 'v', '^', '<', '>', 's', 'p', 'd', 'x'] * 10])

thismodule = sys.modules[__name__]


thismodule.list_of_fake_telescopes = []
thismodule.saved_model = None

###################################################################
###################################################################

def plot_residuals(figure_axe, microlensing_model, model_parameters, bokeh_plot=None,
                   plot_unit='Mag'):
    pyLIMA_parameters = microlensing_model.compute_pyLIMA_parameters(model_parameters)

    # plot residuals

    for ind, tel in enumerate(microlensing_model.event.telescopes):

        if tel.lightcurve_flux is not None:
            residus_in_mag = \
                pyLIMA.fits.objective_functions.photometric_residuals_in_magnitude(
                    tel, microlensing_model, pyLIMA_parameters)

            color = plt.rcParams["axes.prop_cycle"].by_key()["color"][ind]
            marker = str(MARKER_SYMBOLS[0][ind])

            plots.plot_light_curve_magnitude(tel.lightcurve_magnitude['time'].value,
                                             residus_in_mag,
                                             tel.lightcurve_magnitude['err_mag'].value,
                                             figure_axe=figure_axe, color=color,
                                             marker=marker, name=tel.name)

        if bokeh_plot is not None:

            bokeh_plot.scatter(tel.lightcurve_magnitude['time'].value,
                               residus_in_mag,
                               color=color,
                               size=5,
                               muted_color=color,
                               muted_alpha=0.2)

            err_xs = []
            err_ys = []

            for x, y, yerr in zip(tel.lightcurve_magnitude['time'].value,
                                  residus_in_mag,
                                  tel.lightcurve_magnitude['err_mag'].value):
                err_xs.append((x, x))
                err_ys.append((y - yerr, y + yerr))

            bokeh_plot.multi_line(err_xs, err_ys, color=color,
                                  muted_color=color,
                                  muted_alpha=0.2)

    figure_axe.set_ylim([-0.1, 0.1])

#######################################################################################
########################################################################################

def plot_aligned_data(figure_axe, microlensing_model, model_parameters, bokeh_plot=None,
                      plot_unit='Mag'):
    pyLIMA_parameters = microlensing_model.compute_pyLIMA_parameters(model_parameters)

    # plot aligned data
    index = 0

    list_of_telescopes = create_telescopes_to_plot_model(microlensing_model,
                                                         pyLIMA_parameters)

    ref_names = []
    ref_locations = []
    ref_magnification = []
    ref_fluxes = []

    for ref_tel in list_of_telescopes:
        model_magnification = microlensing_model.model_magnification(ref_tel,
                                                                     pyLIMA_parameters)

        microlensing_model.derive_telescope_flux(ref_tel, pyLIMA_parameters,
                                                 model_magnification)

        f_source = getattr(pyLIMA_parameters, 'fsource_' + ref_tel.name)
        f_blend = getattr(pyLIMA_parameters, 'fblend_' + ref_tel.name)

        # model_magnification = (model['photometry']-f_blend)/f_source

        ref_names.append(ref_tel.name)
        ref_locations.append(ref_tel.location)
        ref_magnification.append(model_magnification)
        ref_fluxes.append([f_source, f_blend])

    for ind, tel in enumerate(microlensing_model.event.telescopes):

        if tel.lightcurve_flux is not None:

            if tel.location == 'Earth':

                ref_index = np.where(np.array(ref_locations) == 'Earth')[0][0]

            else:

                ref_index = np.where(np.array(ref_names) == tel.name)[0][0]

            residus_in_mag = \
                pyLIMA.fits.objective_functions.photometric_residuals_in_magnitude(
                    tel, microlensing_model,
                    pyLIMA_parameters)
            if ind == 0:
                reference_source = ref_fluxes[ind][0]
                reference_blend = ref_fluxes[ind][1]
                index += 1

            # time_mask = [False for i in range(len(ref_magnification[ref_index]))]
            time_mask = []
            for time in tel.lightcurve_flux['time'].value:
                time_index = np.where(list_of_telescopes[ref_index].lightcurve_flux[
                                          'time'].value == time)[0][0]
                time_mask.append(time_index)

            # model_flux = ref_fluxes[ref_index][0] * ref_magnification[ref_index][
            #    time_mask] + ref_fluxes[ref_index][1]
            model_flux = reference_source * ref_magnification[ref_index][
                time_mask] + reference_blend
            magnitude = pyLIMA.toolbox.brightness_transformation.ZERO_POINT - 2.5 * \
                        np.log10(model_flux)

            color = plt.rcParams["axes.prop_cycle"].by_key()["color"][ind]
            marker = str(MARKER_SYMBOLS[0][ind])

            plots.plot_light_curve_magnitude(tel.lightcurve_magnitude['time'].value,
                                             magnitude + residus_in_mag,
                                             tel.lightcurve_magnitude['err_mag'].value,
                                             figure_axe=figure_axe, color=color,
                                             marker=marker, name=tel.name)

            if bokeh_plot is not None:

                bokeh_plot.scatter(tel.lightcurve_magnitude['time'].value,
                                   magnitude + residus_in_mag,
                                   color=color,
                                   size=5, legend_label=tel.name,
                                   muted_color=color,
                                   muted_alpha=0.2)

                err_xs = []
                err_ys = []

                for x, y, yerr in zip(tel.lightcurve_magnitude['time'].value,
                                      magnitude + residus_in_mag,
                                      tel.lightcurve_magnitude['err_mag'].value):
                    err_xs.append((x, x))
                    err_ys.append((y - yerr, y + yerr))

                bokeh_plot.multi_line(err_xs, err_ys, color=color,
                                      legend_label=tel.name,
                                      muted_color=color,
                                      muted_alpha=0.2)

#####################################################################################
#####################################################################################

def create_telescopes_to_plot_model(microlensing_model, pyLIMA_parameters):
    if microlensing_model == thismodule.saved_model:

        list_of_fake_telescopes = thismodule.list_of_fake_telescopes

    else:

        list_of_fake_telescopes = []

    if len(list_of_fake_telescopes) == 0:

        # Photometry first
        Earth = True

        for tel in microlensing_model.event.telescopes:

            if tel.lightcurve_flux is not None:

                if tel.location == 'Space':
                    model_time = np.arange(
                        np.min(tel.lightcurve_magnitude['time'].value),
                        np.max(tel.lightcurve_magnitude['time'].value),
                        0.1).round(2)

                    model_time = np.r_[
                        model_time, tel.lightcurve_magnitude['time'].value]

                    model_time.sort()

                if Earth and tel.location == 'Earth':

                    model_time1 = np.arange(np.min((np.min(
                        tel.lightcurve_magnitude['time'].value),
                                                    pyLIMA_parameters.t0 - 5 *
                                                    pyLIMA_parameters.tE)),
                        np.max((np.max(
                            tel.lightcurve_magnitude['time'].value),
                                pyLIMA_parameters.t0 + 5 *
                                pyLIMA_parameters.tE)),
                        1).round(2)

                    model_time2 = np.arange(
                        pyLIMA_parameters.t0 - 1 * pyLIMA_parameters.tE,
                        pyLIMA_parameters.t0 + 1 * pyLIMA_parameters.tE,
                        1).round(2)

                    model_time = np.r_[model_time1, model_time2]

                    for telescope in microlensing_model.event.telescopes:

                        if telescope.location == 'Earth':
                            model_time = np.r_[
                                model_time, telescope.lightcurve_magnitude[
                                    'time'].value]

                            symmetric = 2 * pyLIMA_parameters.t0 - \
                                        telescope.lightcurve_magnitude['time'].value
                            model_time = np.r_[model_time, symmetric]

                    model_time.sort()

                if (tel.location == 'Space') | (Earth and tel.location == 'Earth'):

                    model_time = np.unique(model_time)

                    model_lightcurve = np.c_[
                        model_time, [0] * len(model_time), [0.1] * len(model_time)]
                    model_telescope = fake_telescopes.create_a_fake_telescope(
                        light_curve=model_lightcurve)

                    model_telescope.name = tel.name
                    model_telescope.filter = tel.filter
                    model_telescope.location = tel.location
                    model_telescope.ld_gamma = tel.ld_gamma
                    model_telescope.ld_sigma = tel.ld_sigma
                    model_telescope.ld_a1 = tel.ld_a1
                    model_telescope.ld_a2 = tel.ld_a2
                    model_telescope.location = tel.location

                    if tel.location == 'Space':
                        model_telescope.spacecraft_name = tel.spacecraft_name
                        model_telescope.spacecraft_positions = tel.spacecraft_positions

                    if microlensing_model.parallax_model[0] != 'None':
                        model_telescope.initialize_positions()

                        model_telescope.compute_parallax(
                            microlensing_model.parallax_model,
                            microlensing_model.event.North
                            ,
                            microlensing_model.event.East)  # ,
                        # microlensing_model.event.ra/180*np.pi)

                    list_of_fake_telescopes.append(model_telescope)

                    if tel.location == 'Earth' and Earth:
                        Earth = False

        # Astrometry

        for tel in microlensing_model.event.telescopes:

            if tel.astrometry is not None:

                if tel.location == 'Space':

                    model_time = np.arange(np.min(tel.astrometry['time'].value),
                                           np.max(tel.astrometry['time'].value),
                                           0.1).round(2)
                else:

                    model_time1 = np.arange(
                        np.min((np.min(tel.lightcurve_magnitude['time'].value),
                                pyLIMA_parameters.t0 - 5 * pyLIMA_parameters.tE)),
                        np.max((np.max(tel.lightcurve_magnitude['time'].value),
                                pyLIMA_parameters.t0 + 5 * pyLIMA_parameters.tE)),
                        1).round(2)

                    model_time2 = np.arange(
                        pyLIMA_parameters.t0 - 1 * pyLIMA_parameters.tE,
                        pyLIMA_parameters.t0 + 1 * pyLIMA_parameters.tE,
                        0.1).round(2)

                    model_time = np.r_[model_time1, model_time2]

                    model_time = np.r_[model_time, telescope.astrometry['time'].value]

                    symmetric = 2 * pyLIMA_parameters.t0 - telescope.astrometry[
                        'time'].value
                    model_time = np.r_[model_time, symmetric]
                    model_time.sort()

                model_time = np.unique(model_time)
                model_astrometry = np.c_[
                    model_time, [0] * len(model_time), [0.1] * len(model_time), [
                        0] * len(model_time), [0.1] * len(model_time)]
                model_telescope = fake_telescopes.create_a_fake_telescope(
                    astrometry_curve=model_astrometry,
                    astrometry_unit=tel.astrometry['ra'].unit)

                model_telescope.name = tel.name
                model_telescope.filter = tel.filter
                model_telescope.location = tel.location
                model_telescope.ld_gamma = tel.ld_gamma
                model_telescope.ld_sigma = tel.ld_sigma
                model_telescope.ld_a1 = tel.ld_a1
                model_telescope.ld_a2 = tel.ld_a2
                model_telescope.pixel_scale = tel.pixel_scale

                if tel.location == 'Space':
                    model_telescope.spacecraft_name = tel.spacecraft_name
                    model_telescope.spacecraft_positions = tel.spacecraft_positions

                if microlensing_model.parallax_model[0] != 'None':
                    model_telescope.initialize_positions()

                    model_telescope.compute_parallax(microlensing_model.parallax_model,
                                                     microlensing_model.event.North
                                                     ,
                                                     microlensing_model.event.East)  # ,
                    # microlensing_model.event.ra / 180)# * np.pi)

                list_of_fake_telescopes.append(model_telescope)

        thismodule.saved_model = microlensing_model
        thismodule.list_of_fake_telescopes = list_of_fake_telescopes

    return list_of_fake_telescopes

###################################################################
###################################################################

def plot_photometric_models(figure_axe, microlensing_model, model_parameters,
                            bokeh_plot=None, plot_unit='Mag'):
    pyLIMA_parameters = microlensing_model.compute_pyLIMA_parameters(model_parameters)

    list_of_telescopes = create_telescopes_to_plot_model(microlensing_model,
                                                         pyLIMA_parameters)
    telescopes_names = np.array([i.name for i in microlensing_model.event.telescopes])

    # plot models
    index = 0

    for tel in list_of_telescopes:

        if tel.lightcurve_flux is not None:

            magni = microlensing_model.model_magnification(tel, pyLIMA_parameters)
            microlensing_model.derive_telescope_flux(tel, pyLIMA_parameters, magni)

            f_source = getattr(pyLIMA_parameters, 'fsource_' + tel.name)
            f_blend = getattr(pyLIMA_parameters, 'fblend_' + tel.name)

            if index == 0:
                ref_source = f_source
                ref_blend = f_blend
                index += 1

            magnitude = pyLIMA.toolbox.brightness_transformation.ZERO_POINT - 2.5 * \
                        np.log10(ref_source * magni + ref_blend)

            # delta_mag = -2.5 * np.log10(f_source + f_blend) + 2.5 * np.log10(
            ##     ref_source + ref_blend)
            # magnitude -= delta_mag

            name = tel.name

            index_color = np.where(name == telescopes_names)[0][0]
            color = plt.rcParams["axes.prop_cycle"].by_key()["color"][index_color]

            if tel.location == 'Earth':

                name = tel.location
                linestyle = '-'

            else:

                linestyle = '--'

            plots.plot_light_curve_magnitude(tel.lightcurve_magnitude['time'].value,
                                             magnitude, figure_axe=figure_axe,
                                             name=name, color=color,
                                             linestyle=linestyle)

            if bokeh_plot is not None:
                bokeh_plot.line(tel.lightcurve_magnitude['time'].value, magnitude,
                                legend_label=name, color=color)

###############################################################################
###############################################################################

def initialize_light_curves_plot(plot_unit='Mag', event_name='A microlensing event'):
    fig_size = [10, 10]
    mat_figure, mat_figure_axes = plt.subplots(2, 1, sharex=True,
                                               gridspec_kw={'height_ratios': [3, 1]},
                                               figsize=(fig_size[0], fig_size[1]),
                                               dpi=75)
    plt.subplots_adjust(top=0.8, bottom=0.15, left=0.2, right=0.9, wspace=0.1,
                        hspace=0.1)
    mat_figure_axes[0].grid()
    mat_figure_axes[1].grid()
    # mat_figure.suptitle(event_name, fontsize=30 * fig_size[0] / len(event_name))

    mat_figure_axes[0].set_ylabel('Mag',
                                  fontsize=5 * fig_size[1] * 3 / 4.0)
    mat_figure_axes[0].yaxis.set_major_locator(MaxNLocator(4))
    mat_figure_axes[0].tick_params(axis='y', labelsize=10)

    mat_figure_axes[0].text(0.01, 0.96, 'provided by pyLIMA', style='italic',
                            fontsize=10,
                            transform=mat_figure_axes[0].transAxes)

    mat_figure_axes[1].set_xlabel('JD', fontsize=5 * fig_size[0] * 3 / 4.0)
    mat_figure_axes[1].xaxis.set_major_locator(MaxNLocator(3))
    mat_figure_axes[1].yaxis.set_major_locator(MaxNLocator(4, min_n_ticks=3))

    mat_figure_axes[1].ticklabel_format(useOffset=False, style='plain')
    mat_figure_axes[1].set_ylabel('Delta_M', fontsize=5 * fig_size[1] * 2 / 4.0)
    mat_figure_axes[1].tick_params(axis='x', labelsize=10)
    mat_figure_axes[1].tick_params(axis='y', labelsize=10)

    return mat_figure, mat_figure_axes

#######################################################################
########################################################################

def plot_lightcurves(microlensing_model, model_parameters, bokeh_plot=None):
    # Change matplotlib default colors
    n_telescopes = len(microlensing_model.event.telescopes)
    color = plt.cm.jet(
        np.linspace(0.01, 0.99, n_telescopes))  # This returns RGBA; convert:
    # hexcolor = map(lambda rgb: '#%02x%02x%02x' % (rgb[0] * 255, rgb[1] * 255,
    # rgb[2] * 255),
    #                tuple(color[:, 0:-1]))
    hexcolor = ['#' + format(int(i[0] * 255), 'x').zfill(2) + format(int(i[1] * 255),
                                                                     'x').zfill(2) +
                format(int(i[2] * 255), 'x').zfill(2) for i in color]

    matplotlib.rcParams['axes.prop_cycle'] = cycler.cycler(color=hexcolor)

    mat_figure, mat_figure_axes = initialize_light_curves_plot(
        event_name=microlensing_model.event.name)

    if bokeh_plot is not None:

        bokeh_lightcurves = figure(figsize=(800,600), toolbar_location=None,
                                   y_axis_label='Mag')
        bokeh_residuals = figure(figsize=(800,600),
                                 x_range=bokeh_lightcurves.x_range,
                                 y_range=(0.18, -0.18), toolbar_location=None,
                                 x_axis_label='JD', y_axis_label='Delta_M')

        bokeh_lightcurves.xaxis.minor_tick_line_color = None
        bokeh_lightcurves.xaxis.major_tick_line_color = None
        bokeh_lightcurves.xaxis.major_label_text_font_size = '0pt'
        bokeh_lightcurves.y_range.flipped = True
        bokeh_lightcurves.xaxis.formatter = BasicTickFormatter(use_scientific=False)

        bokeh_residuals.xaxis.formatter = BasicTickFormatter(use_scientific=False)
        bokeh_residuals.xaxis.major_label_orientation = np.pi / 4
        bokeh_residuals.xaxis.minor_tick_line_color = None

    else:

        bokeh_lightcurves = None
        bokeh_residuals = None

    if len(model_parameters) != len(microlensing_model.model_dictionnary):
        telescopes_fluxes = microlensing_model.find_telescopes_fluxes(model_parameters)
        telescopes_fluxes = [getattr(telescopes_fluxes, key) for key in
                             telescopes_fluxes._fields]

        model_parameters = np.r_[model_parameters, telescopes_fluxes]

    plot_photometric_models(mat_figure_axes[0], microlensing_model, model_parameters,
                            plot_unit='Mag',
                            bokeh_plot=bokeh_lightcurves)

    plot_aligned_data(mat_figure_axes[0], microlensing_model, model_parameters,
                      plot_unit='Mag',
                      bokeh_plot=bokeh_lightcurves)

    plot_residuals(mat_figure_axes[1], microlensing_model, model_parameters,
                   plot_unit='Mag',
                   bokeh_plot=bokeh_residuals)

    mat_figure_axes[0].invert_yaxis()
    mat_figure_axes[1].invert_yaxis()
    mat_figure_axes[0].legend(shadow=True, fontsize='large',
                              bbox_to_anchor=(0, 1.02, 1, 0.2),
                              loc="lower left",
                              mode="expand", borderaxespad=0, ncol=3)

    try:
        bokeh_lightcurves.legend.click_policy = "mute"
        # legend = bokeh_lightcurves.legend[0]

    except AttributeError:

        pass

    #figure_bokeh = gridplot([[bokeh_lightcurves], [bokeh_residuals]], toolbar_location=None, width=1200, height=1000)

    return mat_figure, bokeh_lightcurves, bokeh_residuals

##################################################################################################
#################################################################################################

your_event = event.Event(ra=262.75616,dec=-21.40123)
your_event_name = 'Gaia21bsg_binary'

data_1 = np.loadtxt('data/star_20957_Gaia21bsg_fs01_ip_reduced.dat')
telescope_1 = telescopes.Telescope(name='Gaia_20957_i',
                                  camera_filter = 'I',
                                  light_curve = data_1.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_2 = np.loadtxt('data/star_50085_Gaia21bsg_gp_reduced.dat')
telescope_2 = telescopes.Telescope(name='Gaia__50085_g',
                                  camera_filter = 'G',
                                  light_curve = data_2.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_3 = np.loadtxt('data/star_79874_Gaia21bsg_ip_reduced.dat')
telescope_3 = telescopes.Telescope(name='Gaia_79874_i',
                                  camera_filter = 'I',
                                  light_curve = data_3.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_4 = np.loadtxt('data/reduced_ztf.dat',delimiter=' ')
telescope_4 = telescopes.Telescope(name='ZTF_r',
                                  camera_filter = 'R',
                                  light_curve = data_4.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_5 = np.loadtxt('data/reduced_gaia.dat',delimiter=' ')
telescope_5 = telescopes.Telescope(name='Gaia_g',
                                  camera_filter = 'G',
                                  light_curve = data_5.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD', 'mag','mag'])

your_event.telescopes.append(telescope_1)
your_event.telescopes.append(telescope_2)
your_event.telescopes.append(telescope_3)
your_event.telescopes.append(telescope_4)
your_event.telescopes.append(telescope_5)

your_event.find_survey('Gaia')

your_event.check_event()

fspl = FSPL_model.FSPLmodel(your_event)

fit_1 = DE_fit.DEfit(fspl)
fit_1.model_paramter_guess = [2.45935387e+06, 9.99973673e-01, 1.12609326e+00]
fit_1.fit()
fit_1.fit_results['best_model']
fit_1.fit_results.keys()


plot_lightcurves(fspl, fit_1.fit_results['best_model'])   # changed to standalone def func


mpld3.show()