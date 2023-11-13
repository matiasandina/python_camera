# module version

# This file serves to produce module versions for 
# It's a sort of requirements.txt but to use outside a 


from __future__ import print_function
try:
    # for python 2
    import Tkinter as tkinter
except ImportError:
    # for python 3
    import tkinter as tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
try:
    # for python 2
    import tkMessageBox
except ImportError:
    # for python 3
    from tkinter import messagebox as tkMessageBox
import pandas as pd
import time
import numpy as np  


# make a dictionary
# Getting the "module has no attribute .__version__" for many of the requirements
# Dear python :)

x = {'python': __import__('sys').version,
#'tkinter': tkinter.__version__,
'cv2': cv2.__version__,
'pandas': pd.__version__,
#'time': time.__version__,
'numpy': np.__version__}

print(np.array(x).transpose())