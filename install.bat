:: Upgrade pip & setuptools
python -m pip install --upgrade pip setuptools wheel

::Install prebuild wheel
python -m pip install https://pip.vnpy.com/colletion/TA_Lib-0.4.17-cp37-cp37m-win_amd64.whl

::Install Python Modules
python -m pip install -r requirements.txt

python -m pip install -e git+https://github.com/vnpy/vnpy_mongodb.git@1.0.1#egg=vnpy_mongodb
python -m pip install -e git+https://github.com/vnpy/vnpy_ctp.git@6.5.1.7#egg=vnpy_ctp
python -m pip install -e git+https://github.com/vnpy/vnpy_ctabacktester.git@1.0.4#egg=vnpy_ctabacktester

:: Install vn.py
python -m pip install .