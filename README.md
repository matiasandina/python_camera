# python_camera

## Summary

This app allows the user to select hsv thresholding values take a picture

1. Select a camera to capture from
1. Create HSV thresholding mask
1. Save image, HSV mask, and HSV filter values

## Install

In principle, this app is compatible with python 2.7 and python 3.5+. 
Given the, you should be able to run from console.

### Requirements

These are the modules imported by this script.

```
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
```

## Usage

## Contribute

This is a preliminary release. Please file issues to make this software work better.