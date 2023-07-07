# Importing necessary libs to solely extract date (HJD), mag, mag_err from usual .dat files

import numpy as np
import csv
import pandas as PD

import matplotlib.pyplot as plt

import math

from astropy.time import Time

import pyslalib.slalib as S

# Defining funcs we will use

def calc_hjd(mjd_utc, year, debug=False):
    """Function to calculate the Heliocentric Julian Date from the parameters
    in a typical image header:

    :params string dateobs: DATE-OBS, Exposure start time in UTC,
                            %Y-%m-%dT%H:%M:%S format
    :params float exptime:  Exposure time in seconds
    :params string RA:      RA in sexigesimal hours format
    :params string Dec:     Dec in sexigesimal degrees format

    Returns:

    :params float HJD:      HJD
    """
    # Convert RA, Dec to radians:

    # 17:31:01.48   -21:24:04.43 ----> 262.75616   -21.40123

    dRA = 262.75616
    dRA = dRA * 15.0 * math.pi / 180.0
    dDec = -21.40123
    dDec = dDec * math.pi / 180.0
    # if debug:
    #    print('RA '+RA+' -> decimal radians '+str(dRA))
    #    print('Dec '+Dec+' -> decimal radians '+str(dDec))    # Convert the timestamp into a DateTime object:
    # if 'T' in dateobs:
    #    try:
    #        dt = datetime.strptime(dateobs,"%Y-%m-%dT%H:%M:%S.%f")
    #    except ValueError:
    #        dt = datetime.strptime(dateobs,"%Y-%m-%dT%H:%M:%S")
    # else:
    #    try:
    #        dt = datetime.strptime(dateobs,"%Y-%m-%d %H:%M:%S.%f")
    #    except ValueError:
    #        dt = datetime.strptime(dateobs,"%Y-%m-%d %H:%M:%S")    # Convert the exposure time into a TimeDelta object and add half of it
    # to the time to get the exposure mid-point:
    # expt = timedelta(seconds=exptime)

    # dt = dt + expt/2.0

    # if debug:
    #   print('DATE-OBS = '+str(dateobs))
    #   print('Exposure time = '+str(expt))
    #   print('Mid-point of exposure = '+dt.strftime("%Y-%m-%dT%H:%M:%S.%f"))
    #   at = Time(dateobs,format='isot', scale='utc')
    #   aexpt = TimeDelta(exptime,format='sec')

    #  adt = at + aexpt/2.0
    #   print('Astropy: mid-point of exposure = '+adt.value)

    # Calculate the MJD (UTC) timestamp:
    # mjd_utc = datetime2mjd_utc(dt)
    # if debug:
    #    print('MJD_UTC = '+str(mjd_utc))
    #    print('Astropy MJD_UTC = '+str(adt.mjd))

    # Correct the MJD to TT:   FROM THIS POINT ONWARDS IF GIVEN MJD

    # will need to take all MJD and convert to UTC format using astropy
    # dt.year = year from UTC conversion

    mjd_tt = mjd_utc2mjd_tt(mjd_utc)
    if debug:
        print('MJD_TT = ' + str(mjd_tt))

        att = adt.tt
        print('Astropy MJD_TT = ' + str(att.mjd))

    # Calculating MJD of 1st January that year:
    (mjd_jan1, iexec) = S.sla_cldj(year, 1, 1)
    if debug:
        print('MJD of Jan 1, ' + str(year) + ' = ' + str(mjd_jan1))

        at_jan1 = Time(str(year) + '-01-01T00:00:00.0', format='isot', scale='utc')
        print('Astropy MJD of Jan 1, ' + str(year) + ' = ' + str(at_jan1.mjd))

    # Calculating the MJD difference between the DateObs and Jan 1 of the same year:
    tdiff = mjd_tt - mjd_jan1
    if debug:
        print('Time difference from Jan 1 - dateobs, ' + \
              str(year) + ' = ' + str(tdiff))

        atdiff = att.mjd - at_jan1.mjd
        print('Astropy time difference = ' + str(atdiff))

        # Calculating the RV and time corrections to the Sun:
    (rv, tcorr) = S.sla_ecor(dRA, dDec, year, int(tdiff), (tdiff - int(tdiff)))
    if debug:
        print('Time correction to the Sun = ' + str(tcorr))

    # Calculating the HJD:
    hjd = mjd_tt + tcorr / 86400.0 + 2400000.5
    if debug:
        print('HJD = ' + str(hjd))

    return hjd

####################################################################################################################

def estimateGaiaError(mag):   # function to compute the mag_err
    a1 = 0.2
    b1 = -5.3  # -5.2
    log_err1 = a1 * mag + b1
    a2 = 0.2625
    b2 = -6.3625  # -6.2625
    log_err2 = a2 * mag + b2

    if (mag < 13.5): expectedStdAtBaselineMag = 10 ** (a1 * 13.5 + b1)
    if (mag >= 13.5 and mag < 17): expectedStdAtBaselineMag = 10 ** log_err1
    if (mag >= 17): expectedStdAtBaselineMag = 10 ** log_err2

    # this works until 21 mag.

    return expectedStdAtBaselineMag

###################################################################################################################

def mjd_utc2mjd_tt(mjd_utc, dbg=False):
    '''Converts a MJD in UTC (MJD_UTC) to a MJD in TT (Terrestial Time) which is
    needed for any position/ephemeris-based calculations.
    UTC->TT consists of: UTC->TAI = 10s offset + 24 leapseconds (last one 2009 Jan 1.)
    	    	    	TAI->TT  = 32.184s fixed offset'''
    # UTC->TT offset
    tt_utc = S.sla_dtt(mjd_utc)
    if dbg:
        print('TT-UTC(s)=' + str(tt_utc))

    # Correct MJD to MJD(TT)
    mjd_tt = mjd_utc + (tt_utc / 86400.0)
    if dbg:
        print('MJD(TT)  =  ' + str(mjd_tt))
    return mjd_tt

#####################################################################################################################

# loading in the ztf data
# Note: ztf data will need a script to be queued and will most likely result in a .tbl
# which will need to be converted to a readable format (e.g. .csv, etc.)

# Note: table had the HJD as the third column, the magnitude as the fifth column, and the mag_err as the sixth column
# (i.e. no need for conversion func)

ztf = np.genfromtxt('data/ztf_raw.csv',delimiter=',',usecols=(2,4,5))
np.savetxt('reduced_ztf.dat',ztf,fmt='%s')   # saving the data array as a .dat file for import