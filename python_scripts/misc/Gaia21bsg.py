#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyLIMA


# In[2]:


get_ipython().run_line_magic('matplotlib', 'notebook')

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


# In[3]:


your_event = event.Event(ra=262.75616,dec=-21.40123)
your_event.name = 'Gaia21bsg'


# In[4]:


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


# In[ ]:


#plt.plot(data_3[:,0],data_3[:,1])


# In[5]:


data_4 = np.loadtxt('data/atlas_c_filter.dat',delimiter=',')   # will need to use func to convert to HDJD
#data_4[:,0] = data_4[:,0] + 2.4e6
telescope_4 = telescopes.Telescope(name='ATLAS_c',
                                  camera_filter = 'C',
                                  light_curve = data_4.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])


# In[ ]:


#plt.plot(data_4[:,0],data_4[:,1],'o')


# In[6]:


data_5 = np.loadtxt('data/atlas_o_filter.dat',delimiter=',')   # will need to use func to convert to HJD
#data_5[:,0] = data_5[:,0] + 2.4e6
telescope_5 = telescopes.Telescope(name='ATLAS_o',
                                  camera_filter = 'O',
                                  light_curve = data_5.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])


# In[ ]:


#plt.plot(data_4[:,0],data_4[:,1])


# In[7]:


data_6 = np.loadtxt('data/ztf_gaiabsg21_reduced.dat',delimiter=',')   # will need to use func to convert HJD
#data_6[:,0] = data_6[:,0] + 2.4e6
telescope_6 = telescopes.Telescope(name='ZTF_r',
                                  camera_filter = 'R',
                                  light_curve = data_6.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD','mag','mag'])


# In[ ]:


#plt.plot(data_5[:,0],data_5[:,1])


# In[8]:


data_7 = np.loadtxt('data/reduced_gaia_data.dat',delimiter=',')    # will need to use func to convert HJD
#data_7[:,0] = data_7[:,0] + 2.4e6
telescope_7 = telescopes.Telescope(name='Gaia_g',
                                  camera_filter = 'G',
                                  light_curve = data_7.astype(float),
                                  light_curve_names = ['time','mag','err_mag'],
                                  light_curve_units = ['JD', 'mag','mag'])


# # object id found via ztf: 281216400001763

# In[9]:


your_event.telescopes.append(telescope_1)
your_event.telescopes.append(telescope_2)
your_event.telescopes.append(telescope_3)
your_event.telescopes.append(telescope_4)
your_event.telescopes.append(telescope_5)
your_event.telescopes.append(telescope_6)
your_event.telescopes.append(telescope_7)


# In[10]:


your_event.find_survey('Gaia')


# In[11]:


your_event.check_event()


# In[12]:


from pyLIMA.models import PSPL_model
pspl = PSPL_model.PSPLmodel(your_event)


# In[13]:


from pyLIMA.fits import DE_fit


# In[14]:


my_fit = DE_fit.DEfit(pspl)


# In[15]:


my_fit.fit_parameters


# In[16]:


my_fit.fit()


# In[17]:


my_fit.fit_results


# In[18]:


my_fit.fit_results['best_model']


# In[19]:


my_fit.fit_parameters.keys()


# In[20]:


from pyLIMA.outputs import pyLIMA_plots
pyLIMA_plots.plot_lightcurves(pspl,my_fit.fit_results['best_model'])
plt.show()


# In[21]:


from pyLIMA.fits import LM_fit


# In[22]:


my_fit2 = LM_fit.LMfit(pspl)


# In[23]:


my_fit2.fit()


# In[24]:


my_fit2.fit_results


# In[25]:


my_fit2.fit_results['best_model']


# In[26]:


my_fit2.fit_parameters.keys()


# In[27]:


pyLIMA_plots.plot_lightcurves(pspl,my_fit2.fit_results['best_model'])
plt.savefig('output1.png')
plt.show()


# In[ ]:




