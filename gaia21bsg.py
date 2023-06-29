import pyLIMA

import numpy as np
import matplotlib.pyplot as plt
import csv

from pyLIMA.fits import DE_fit
from pyLIMA.fits import TRF_fit
from pyLIMA.models import PSPL_model
from pyLIMA.models import USBL_model, pyLIMA_fancy_parameters
from pyLIMA.outputs import pyLIMA_plots

from pyLIMA import event
from pyLIMA import telescopes

your_event = event.Event(ra=262.75616,dec=-21.40123)
your_event.name = 'Gaia21bsg'

data_1 = np.loadtxt('data/star_20957_Gaia21bsg_fs01_ip_reduced.dat')
telescope_1 = telescopes.Telescope(name='Gaia',
                                  camera_filter = 'I',
                                  light_curve = data_1.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_2 = np.loadtxt('data/star_50085_Gaia21bsg_gp_reduced.dat')
telescope_2 = telescopes.Telescope(name='Gaia2',
                                  camera_filter = 'G',
                                  light_curve = data_2.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_3 = np.loadtxt('data/star_79874_Gaia21bsg_ip_reduced.dat')
telescope_3 = telescopes.Telescope(name='Gaia3',
                                  camera_filter = 'I',
                                  light_curve = data_3.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_4 = np.loadtxt('data/atlas_Gaia21bsg_reduced.dat')
data_4[:,0] = data_4[:,0] + 2.4e6
telescope_4 = telescopes.Telescope(name='Atlas',
                                  camera_filter = '',
                                  light_curve = data_4.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

data_5 = np.loadtxt('data/ztf_gaiabsg21_reduced.dat')   # object id for ztf query: 281216400001763
data_5[:,0] = data_5[:,0] + 2.4e6
telescope_5 = telescopes.Telescope(name='ZTF',
                                  camera_filter = '',
                                  light_curve = data_5.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])

your_event.telescopes.append(telescope_1)
your_event.telescopes.append(telescope_2)
your_event.telescopes.append(telescope_3)
your_event.telescopes.append(telescope_4)
your_event.telescopes.append(telescope_5)

your_event.find_survey('Gaia')
your_event.check_event()

from pyLIMA.models import PSPL_model
pspl = PSPL_model.PSPLmodel(your-event)

from pyLIMA.fits import DE_fit

my_fit = DE_fit.DEfit(pspl)
my_fit.fit_parameters

my_fit.fit()

my_fit.fit_results
my_fit.fit_results['best_model']

my_fit.fit_parameters.keys()

from pyLIMA.outputs import pyLIMA_plots
pyLIMA_plots.plot_lightcurves(pspl,my_fit.fit_results['best_model'])
plt.show()

from pyLIMA.fits import LM_fit
my_fit2 = LM_fit.LMfit(pspl)
my_fit2.fit()
my_fit2.fit_results
my_fit.fit_results['best_model']
my_fit2.fit_parameters.keys()

pyLIMA_plots.plot_lightcurves(pspl,my_fit2.fit_results['best_model'])
plt.show()