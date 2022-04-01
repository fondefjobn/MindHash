# MindHash

#How to install

Tested on Ubuntu LTS 20.04, python 3.8 , RTX 2060/GTX 1080 , cuda-11.6

Use python 3.8/3.9

Use venv virtual environment

Pycharm can be used to set up the virtual environment:\
https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html

Add `export PYTHONPATH="${PYTHONPATH}:{/absolute/path/to/project}"` to `venv/bin/activate` 

Source the virtual environment:\
`source venv/bin/activate`

Install required packages:\
`pip install -r requirements.txt` 

Install cuda-toolkit 11.6 & `export CUDA_HOME=/usr/local/cuda` or /path/to/your/cuda (folder from root dir)

Install torch & torchvision with:\
`pip3 install torch==1.10.0+cu113 torchvision==0.11.0+cu113 torchaudio==0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html`

Install OpenPCDet:\
`cd OpenPCDet`\
`python setup.py develop`

Done