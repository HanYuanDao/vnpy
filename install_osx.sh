#!/usr/bin/env bash

python=$1
pypi_index=$2
shift 2

[[ -z $python ]] && python=python3
[[ -z $pypi_index ]] && pypi_index=https://pypi.vnpy.com

$python -m pip install --upgrade pip wheel --index $pypi_index

# Get and build ta-lib
function install-ta-lib()
{
    export HOMEBREW_NO_AUTO_UPDATE=true
    brew install ta-lib
}
function ta-lib-exists()
{
    ta-lib-config --libs > /dev/null
}
ta-lib-exists || install-ta-lib

# install ta-lib
$python -m pip install numpy==2.2.4 --index $pypi_index
$python -m pip install ta-lib==0.6.3 --index $pypi_index

# Install VeighNa
#$python -m pip install . --index $pypi_index

$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_ctp.git@tag6770#egg=vnpy_ctp
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_sqlite.git@tag110#egg=vnpy_sqlite
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_algotrading.git@tag107#egg=vnpy_algotrading
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_chartwizard.git@tag104#egg=vnpy_chartwizard
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_ctabacktester.git@tag116#egg=vnpy_ctabacktester
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_ctastrategy.git@tag131#egg=vnpy_ctastrategy
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_datamanager.git@tag111#egg=vnpy_datamanager
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_optionmaster.git@tag110#egg=vnpy_optionmaster
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_paperaccount.git@tag106#egg=vnpy_paperaccount
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_portfoliomanager.git@tag103#egg=vnpy_portfoliomanager
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_portfoliostrategy.git@tag111#egg=vnpy_portfoliostrategy
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_riskmanager.git@tag104#egg=vnpy_riskmanager
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_rpcservice.git@tag106#egg=vnpy_rpcservice
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_scripttrader.git@tag102#egg=vnpy_scripttrader
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_spreadtrading.git@tag125#egg=vnpy_spreadtrading
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_webtrader.git@tag105#egg=vnpy_webtrader
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_mini.git@tag001#egg=vnpy_mini
$python -m pip install -e git+https://github.com/HanYuanDao/vnpy_mongodb.git@tag1.1.0#egg=vnpy_mongodb