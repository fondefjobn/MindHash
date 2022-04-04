# MindHash
@Authors: Radu Rebeja, Nevis King

*Project tested on Ubuntu LTS 20.04, python 3.8 , RTX 2060 , cuda-11.6*
*Project requires a CUDA capable GPU *
### Installation
**Interpreter**:  
- python 3.8/3.9

**Virtual Environment:**
- use *venv*
- add `export PYTHONPATH="${PYTHONPATH}:{/absolute/path/to/project/Mindhash}"` to `venv/bin/activate` script
- run `source venv/bin/activate`
- run `pip install -r requirements.txt`

**CUDA**:
- install cuda-toolkit 11.6 & `export CUDA_HOME=/usr/local/cuda` or `/path/to/your/cuda` (folder from root dir)

**TORCH & TORCHVISION**
- Install torch & torchvision with:\
`pip3 install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html`

**OpenPCDet**
- To use the machine learning evaluation tools users require installing OpenPCDet framework inside the project root folder named
`OpenPCDet` (**CASE SENSITIVE!**) (e.g. folder structure  `Mindhash-main/OpenPCDet/pcdet/...`)
- follow installation guide in OpenPCDet (ignore spconv & open3d requirements - right version are specified in root `requirements.txt`) 
- copy files inside `Mindhash-main/_pcdet_files` to `Mindhash-main/OpenPCDet/tools/` 

**Models**
- pre-trained models can be downloaded by referring to OpenPCDet/README.md (Model Zoo)
- the path to the model is specified with `--mlpath /your/path/to/model.pth` at execution time 

**Running**
- To run the project : cli/exec_cli.py
- Argument documentation for running the script is provided by running `python exec_cli.py -h` 
- Example : `python3 exec_cli.py --sensor ouster --eval --visual --mlpath ../resources/trained_models/pv_rcnn.pth --ml PVRCNN --export predictions`
- We are experimenting with multiple models and compare their performances. Currently, we tested PVRCNN, PointPillars, PartA2 and PointRCNN.
When executing the script you must specify the correct model name alongside its .pth file path - choices are provided by
the ArgumentParser documentation

****
**Directories**

| **Package**            | **Description**                                                                                                           |
|------------------------|---------------------------------------------------------------------------------------------------------------------------|
| OpenPCDet.tools        | Enables the training and evaluation of models.                                                                            |
| OpenPCDet.pcdet.models | Allows many different models to be run with the same code.                                                                |
| cli                    | Command line interface from which the program is executed                                                                 |
| eval.api               | Django webserver which allows those who dont meet the system requirements to remotely run the model on some given data.   |
| sensor                 | controller for lidar camera. Contains functions for reading datastreams from the scanner as well as doing post processing |
| statistic              | Runs statistical analysis to compare the efficacy of various models                                                       |
| streamproccessor       | Provides functionalities for data filtering and augmentation tasks                                                        |
| tools                  | Pipeline and utilities                                                                                                    |
| visualizer             | Visualizer for lidar data as well as the bounding boxes produced by the models                                            |



