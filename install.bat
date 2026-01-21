@ECHO OFF
SET python=%1
SET pypi_index=%2
IF     %python%""     == "" SET python=python
IF     %pypi_index%"" == "" SET pypi_index=https://pypi.vnpy.com
IF NOT %pypi_index%"" == "" SET pypi_index=--index-url %pypi_index%
@ECHO ON

:: Upgrade pip & wheel
%python% -m pip install --upgrade pip wheel %pypi_index%

::Install prebuild wheel
%python% -m pip install --extra-index-url https://pypi.vnpy.com TA_Lib===0.6.3 

::Install Python Modules
:: %python% -m pip install -r requirements.txt %pypi_index%

:: Install VeighNa
:: %python% -m pip install .
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_ctp.git@tag6770#egg=vnpy_ctp
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_sqlite.git@tag110#egg=vnpy_sqlite
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_algotrading.git@tag107#egg=vnpy_algotrading
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_chartwizard.git@tag104#egg=vnpy_chartwizard
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_ctabacktester.git@tag116#egg=vnpy_ctabacktester
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_ctastrategy.git@tag131#egg=vnpy_ctastrategy
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_datamanager.git@tag111#egg=vnpy_datamanager
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_optionmaster.git@tag110#egg=vnpy_optionmaster
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_paperaccount.git@tag106#egg=vnpy_paperaccount
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_portfoliomanager.git@tag103#egg=vnpy_portfoliomanager
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_portfoliostrategy.git@tag111#egg=vnpy_portfoliostrategy
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_riskmanager.git@tag104#egg=vnpy_riskmanager
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_rpcservice.git@tag106#egg=vnpy_rpcservice
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_scripttrader.git@tag102#egg=vnpy_scripttrader
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_spreadtrading.git@tag125#egg=vnpy_spreadtrading
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_webtrader.git@tag105#egg=vnpy_webtrader
@REM %python% -m pip install -e git+https://github.com/HanYuanDao/vnpy_mini.git@tag001#egg=vnpy_mini