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

    # Convert the exposure time into a TimeDelta object and add half of it

    #        dt = datetime.strptime(dateobs,"%Y-%m-%d %H:%M:%S")
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

# Loading the gaia alerts exported data; slightly formatted differently (i.e. Date in UTC format, JD, avg mag)
# thus, we will need to compute the mag_err and the HJD

# Note: gaia alerts will export the data as a .csv file;
# we can simply rename the file type from .csv to .dat file which easier to use
# Note: there are certain rows that have strings as entries for the avg mag; we will need to delete those rows
# Note: the date and JD are both in TCB, will need to take into consideration

# Note: change 'rh6Uodk.dat' filename to your appropriate filename

# Only the Date in JD format (TCB) and avg magnitude columns
gaia = np.genfromtxt('data/rh6Uodk_.dat',delimiter=',',usecols=(1,2))

# will now remove the unnecessary entries/associated rows

reduced_gaia = np.array((0,0))

for i in range(len(gaia)):
    if np.isnan(gaia[i,1]) == False:
        reduced_gaia = np.vstack((reduced_gaia,gaia[i]))

reduced_gaia = np.delete(reduced_gaia,(0),axis=0)   # reduced gaia file without the string entries

# will now compute the magnitude error using the defined func

mag = reduced_gaia[:,1]

err = np.array((0))

for i in range(len(mag)):
    err = np.vstack((err,estimateGaiaError(mag[i])))

err = np.delete(err,(0),axis=0)

reduced_gaia = np.concatenate((reduced_gaia,err),axis=1)   # Now is in JD (TCB), mag, mag_err format, KEEEEYYYYY

##################################################################

# objective now is hjd, mag, mag_err format

times = reduced_gaia[:,0]
t = Time(times,format='jd',scale='tcb')   # Need to change this in actual data
t = t.utc   # conversion of tcb scale factor to utc

# conversion of isot format to mjd (which will be converted to hjd using defined func),
# first parameter for conversion func
gaia_times = t.mjd

gaia_year = np.array((0))

# Converting JD (TCB) to ISOT (TCB) so we can extract year for conversion func

t1 = t.utc
year = t.isot

for i in range(len(year)):
    gaia_year = np.vstack((gaia_year,int(year[i][0:4])))

# array containing the year parameter, second parameter for conversion func

gaia_year = np.delete(gaia_year,(0),axis=0)

gaia_hjd = np.array((0))

for i in range(len(gaia_year)):
    gaia_hjd = np.vstack((gaia_hjd, calc_hjd(gaia_times[i],gaia_year[i])))

gaia_hjd = np.delete(gaia_hjd,(0),axis=0)   # computed hjd for gaia data set

reduced_gaia = np.delete(reduced_gaia,(0),axis=1)   # deleting the date (TCB) column
reduced_gaia = np.concatenate((gaia_hjd,reduced_gaia),axis=1)   # concatenating the hjd column as first

# saving the data array as a .dat file for import

np.savetxt('reduced_gaia.dat',reduced_gaia,fmt='%s')