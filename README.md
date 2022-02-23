# AdvNLPTermProject

## Requirements
Install all required dependencies by running:

```pip install -r requirements.txt```

This will install all dependecies required for all portions of this project.

The installation of current versions of tensorflow and keras will conflict with portions of the textgenrnn code. 
To resolve these issues, after installing the dependecies, navigate to the library code for external site packages and modify the textgenrnn.py file.
The changes needed are to modify line 5 to:

```from tensorflow.python.keras.utils.multi_gpu_utils import multi_gpu_model```

And line 14 to: 

```from tensorflow.python.keras.backend import set_session```