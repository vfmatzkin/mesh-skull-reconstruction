# mesh-skull-reconstruction

https://github.com/vfmatzkin/mesh-skull-reconstruction

A set of algorithms for converting volumetric CT head images into skull registered meshes using deep learning.

## Requirements

### Install Anaconda

[Anaconda installing guide](https://docs.anaconda.com/anaconda/install/)

#### Using the requeriments file

[//]: # (TODO generate env.yml)
You must create a conda environment using the environment.yml file in the root of the repository. 
The creation of the environment is done by the following command:

```
conda env create -f env.yml
```

#### If env.yml doesn't work

Run the following commands:

```
 >> conda create -n msr python=3.8 numpy
 >> conda activate msr
(msr) >> pip install deformetrica
(msr) >> conda install -c conda-forge jupyterlab
(msr) >> conda install -c simpleitk simpleitk
```

## Usage
You can use the several ipynb files in the repository to run the algorithms.