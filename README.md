# MindHash

tested on Ubuntu LTS 20.04, python 3.8 , RTX 2060 , cuda-11.6\

use python 3.8/3.9 \
use venv virtual environment \
add `export PYTHONPATH="${PYTHONPATH}:{/absolute/path/to/project}"` to `venv/bin/activate` \
source `venv/bin/activate`\
pip install -r requirements \
install cuda-toolkit 11.6 & `export CUDA_HOME=/usr/local/cuda` or /path/to/your/cuda (folder from root dir)\
install torch & torchvision with:\
`pip3 install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html`
follow installation guide in OpenPCDet (ignore spconv & open3d requirements - right version already installed) \

done