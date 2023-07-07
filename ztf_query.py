import os
import re
import sys
import time
from io import StringIO

import pandas as pd
import requests

USER = "ezequiel@lco.global"
PASS = "6100514092@Eze"

curl --user ${'ezequiel@lco.global'}:${'6100514092@Eze'} [...] "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=281216400001763"

#wget --auth-no-challenge --user=$USER --pass=$PASS [..] "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID=281216400001763"

with requests.Session() as s:
    textdata = s.get(result_url, headers=headers).text

    # if we'll be making a lot of requests, keep the web queue from being
    # cluttered (and reduce server storage usage) by sending a delete operation
    # s.delete(task_url, headers=headers).json()

dfresult = pd.read_csv(StringIO(textdata.replace("###", "")), delim_whitespace=True)
print(dfresult)