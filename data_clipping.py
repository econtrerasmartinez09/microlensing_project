import numpy as np
import matplotlib.pyplot as plt
import pandas

from sklearn.utils import resample   # pip install -U scikit-learn
from sklearn.metrics import accuracy_score

################################################################

# Loading in ATLAS_o filter data set, for example

atlas_o_filter = np.loadtxt('atlas_o_filter.dat',delimiter = ',')
x = atlas_o_filter[:,2]   # mag_err column

n_iterations = 1000
n_size = int(len(x))

medians = list()
for i in range(n_iterations):
    s = resample(x,n_samples=n_size);
    m = np.median(s);
    medians.append(m)

plt.hist(medians)
plt.xlabel('Mag Err')

plt.show()

#################################################################

alpha = 0.90   # Confidence percentage
p = ((1.0 - alpha) / 2.0) * 100
lower = numpy.percentile(medians, p)
p = (alpha + ((1.0 - alpha) / 2.0)) * 100
upper = numpy.percentile(medians, p)

print(f"\n{alpha * 100} confidence interval {lower} and {upper}")

mag_err = np.array((0,0,0))

for i in range(len(atlas_o_filter)):
    if atlas_o_filter[i,2] < upper:
        mag_err = np.vstack((mag_err,atlas_o_filter[i]))

mag_err = np.delete(mag_err,(0),axis=0)   # Final data set that is reduced to contain only within 90% confidence interval

np.savetxt('reduced_atlas_o.dat',mag_err,fmt='%s')