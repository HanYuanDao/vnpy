"""
General constant enums used in the trading platform.
"""

import re
from enum import Enum, IntEnum
from datetime import datetime as DateTime
from typing import Any

from .locale import _


_PRODUCE_AM_RELAX_END_HM_1: str = "090000"
_PRODUCE_AM_RELAX_END_HM_2: str = "093000"
_PRODUCE_BB_RELAX_START_HM: str = "101500"
_PRODUCE_BB_RELAX_END_HM: str = "103000"
_PRODUCE_AF_RELAX_START_HM: str = "113000"
_PRODUCE_AF_RELAX_END_HM_1: str = "130000"
_PRODUCE_AF_RELAX_END_HM_2: str = "133000"
_PRODUCE_PM_RELAX_START_HM: str = "150000"
_PRODUCE_PM_RELAX_END_HM: str = "210000"
_PRODUCE_N_RELAX_END_HM_1: str = "230000"
_PRODUCE_N_RELAX_END_HM_2: str = "010000"
_PRODUCE_N_RELAX_END_HM_3: str = "023000"


class CtaTradeState(IntEnum):
    """
    CTA strategy trade state.

    Enum value is the numeric code, and `description` stores the Chinese label.
    """

    INACTIVE = (0, "不进行任何活动")
    OPENING = (1, "开始开仓")
    HOLDING = (10, "已持仓")
    STOP_LOSSING = (60, "开始止损")
    STOP_PROFITING = (70, "开始止盈")
    SLEEPING = (91, "转为休眠")
    CLEANING_TRADING_SESSION = (92, "跨交易时间前清理持仓")

    def __new__(cls, code: int, description: str) -> "CtaTradeState":
        obj: "CtaTradeState" = int.__new__(cls, code)
        obj._value_ = code
        obj.description = description
        return obj


class Direction(Enum):
    """
    Direction of order/trade/position.
    """
    LONG = _("多")
    SHORT = _("空")
    NET = _("净")


class Offset(Enum):
    """
    Offset of order/trade.
    """
    NONE = ""
    OPEN = _("开")
    CLOSE = _("平")
    CLOSETODAY = _("平今")
    CLOSEYESTERDAY = _("平昨")


class Status(Enum):
    """
    Order status.
    """
    SUBMITTING = _("提交中")
    NOTTRADED = _("未成交")
    PARTTRADED = _("部分成交")
    ALLTRADED = _("全部成交")
    CANCELLED = _("已撤销")
    REJECTED = _("拒单")


class Product(Enum):
    """
    Product class.
    """
    EQUITY = _("股票")
    FUTURES = _("期货")
    OPTION = _("期权")
    INDEX = _("指数")
    FOREX = _("外汇")
    SPOT = _("现货")
    ETF = "ETF"
    BOND = _("债券")
    WARRANT = _("权证")
    SPREAD = _("价差")
    FUND = _("基金")
    CFD = "CFD"
    SWAP = _("互换")


class OrderType(Enum):
    """
    Order type.
    """
    LIMIT = _("限价")
    MARKET = _("市价")
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = _("询价")
    ETF = "ETF"


class OptionType(Enum):
    """
    Option type.
    """
    CALL = _("看涨期权")
    PUT = _("看跌期权")


class Exchange(Enum):
    """
    Exchange.
    """
    # Chinese
    CFFEX = "CFFEX"         # China Financial Futures Exchange
    SHFE = "SHFE"           # Shanghai Futures Exchange
    CZCE = "CZCE"           # Zhengzhou Commodity Exchange
    DCE = "DCE"             # Dalian Commodity Exchange
    INE = "INE"             # Shanghai International Energy Exchange
    GFEX = "GFEX"           # Guangzhou Futures Exchange
    SSE = "SSE"             # Shanghai Stock Exchange
    SZSE = "SZSE"           # Shenzhen Stock Exchange
    BSE = "BSE"             # Beijing Stock Exchange
    SHHK = "SHHK"           # Shanghai-HK Stock Connect
    SZHK = "SZHK"           # Shenzhen-HK Stock Connect
    SGE = "SGE"             # Shanghai Gold Exchange
    WXE = "WXE"             # Wuxi Steel Exchange
    CFETS = "CFETS"         # CFETS Bond Market Maker Trading System
    XBOND = "XBOND"         # CFETS X-Bond Anonymous Trading System

    # Global
    SMART = "SMART"         # Smart Router for US stocks
    NYSE = "NYSE"           # New York Stock Exchnage
    NASDAQ = "NASDAQ"       # Nasdaq Exchange
    ARCA = "ARCA"           # ARCA Exchange
    EDGEA = "EDGEA"         # Direct Edge Exchange
    ISLAND = "ISLAND"       # Nasdaq Island ECN
    BATS = "BATS"           # Bats Global Markets
    IEX = "IEX"             # The Investors Exchange
    AMEX = "AMEX"           # American Stock Exchange
    TSE = "TSE"             # Toronto Stock Exchange
    NYMEX = "NYMEX"         # New York Mercantile Exchange
    COMEX = "COMEX"         # COMEX of CME
    GLOBEX = "GLOBEX"       # Globex of CME
    IDEALPRO = "IDEALPRO"   # Forex ECN of Interactive Brokers
    CME = "CME"             # Chicago Mercantile Exchange
    ICE = "ICE"             # Intercontinental Exchange
    SEHK = "SEHK"           # Stock Exchange of Hong Kong
    HKFE = "HKFE"           # Hong Kong Futures Exchange
    SGX = "SGX"             # Singapore Global Exchange
    CBOT = "CBOT"           # Chicago Board of Trade
    CBOE = "CBOE"           # Chicago Board Options Exchange
    CFE = "CFE"             # CBOE Futures Exchange
    DME = "DME"             # Dubai Mercantile Exchange
    EUREX = "EUX"           # Eurex Exchange
    APEX = "APEX"           # Asia Pacific Exchange
    LME = "LME"             # London Metal Exchange
    BMD = "BMD"             # Bursa Malaysia Derivatives
    TOCOM = "TOCOM"         # Tokyo Commodity Exchange
    EUNX = "EUNX"           # Euronext Exchange
    KRX = "KRX"             # Korean Exchange
    OTC = "OTC"             # OTC Product (Forex/CFD/Pink Sheet Equity)
    IBKRATS = "IBKRATS"     # Paper Trading Exchange of IB

    # Special Function
    LOCAL = "LOCAL"         # For local generated data
    GLOBAL = "GLOBAL"       # For those exchanges not supported yet


class Currency(Enum):
    """
    Currency.
    """
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"


class Interval(Enum):
    """
    Interval of bar data.
    """
    MINUTE = "1m"
    HOUR = "1h"
    DAILY = "d"
    WEEKLY = "w"
    TICK = "tick"


class ExchangeXinQi(Enum):
    CFFEX = ("CFFEX", Exchange.CFFEX, 3)
    SHFE = ("SHFE", Exchange.SHFE, 4)
    CZCE = ("CZCE", Exchange.CZCE, 2)
    DCE = ("DCE", Exchange.DCE, 1)
    INE = ("INE", Exchange.INE, 5)
    GFEX = ("GFEX", Exchange.GFEX, 8)

    @classmethod
    def get_by_exchange_no(cls, exchange_no: int | str) -> "ExchangeXinQi | None":
        """根据新旗交易所编号返回对应枚举。"""
        try:
            target_id: int = int(exchange_no)
        except (TypeError, ValueError):
            return None

        for exchange in cls:
            if exchange.value[2] == target_id:
                return exchange

        return None


class Produce(Enum):
    """
    Futures product metadata and trading-session helpers translated from ProductEnum.
    """

    A = ("a", "豆一", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    B = ("b", "豆二", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    BB = ("bb", "胶合板", Exchange.DCE, _PRODUCE_PM_RELAX_START_HM)
    BZ = ("bz", "纯苯", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    C = ("c", "玉米", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    CS = ("cs", "淀粉", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    EB = ("eb", "苯乙烯", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    EG = ("eg", "乙二醇", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    FB = ("fb", "纤维板", Exchange.DCE, _PRODUCE_PM_RELAX_START_HM)
    I = ("i", "铁矿石", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    J = ("j", "焦炭", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    JD = ("jd", "鸡蛋", Exchange.DCE, _PRODUCE_PM_RELAX_START_HM)
    JM = ("jm", "焦煤", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    L = ("l", "塑料", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    LH = ("lh", "生猪", Exchange.DCE, _PRODUCE_PM_RELAX_START_HM)
    LG = ("lg", "原木", Exchange.DCE, _PRODUCE_PM_RELAX_START_HM)
    M = ("m", "豆粕", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    P = ("p", "棕榈油", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    PG = ("pg", "液化气", Exchange.DCE, _PRODUCE_PM_RELAX_START_HM)
    PP = ("pp", "聚丙烯", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    RR = ("rr", "粳米", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    V = ("v", "PVC", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    Y = ("y", "豆油", Exchange.DCE, _PRODUCE_N_RELAX_END_HM_1)
    AD = ("ad", "铸造铝", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    AG = ("ag", "沪银", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_3)
    AL = ("al", "沪铝", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    AO = ("ao", "氧化铝", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    AU = ("au", "沪金", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_3)
    BU = ("bu", "沥青", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    BR = ("br", "BR橡胶", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    CU = ("cu", "沪铜", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    FU = ("fu", "燃料油", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    HC = ("hc", "热卷", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    NI = ("ni", "沪镍", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    OP = ("op", "胶版印刷纸", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    PB = ("pb", "沪铅", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    RB = ("rb", "螺纹钢", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    RU = ("ru", "橡胶", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    SN = ("sn", "沪锡", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    SP = ("sp", "纸浆", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_1)
    SS = ("ss", "不锈钢", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    WR = ("wr", "线材", Exchange.SHFE, _PRODUCE_PM_RELAX_START_HM)
    ZN = ("zn", "沪锌", Exchange.SHFE, _PRODUCE_N_RELAX_END_HM_2)
    BC = ("bc", "国际铜", Exchange.INE, _PRODUCE_N_RELAX_END_HM_2)
    EC = ("ec", "ec", Exchange.INE, _PRODUCE_PM_RELAX_START_HM)
    LU = ("lu", "LU燃油", Exchange.INE, _PRODUCE_N_RELAX_END_HM_1)
    NR = ("nr", "20号胶", Exchange.INE, _PRODUCE_N_RELAX_END_HM_1)
    SC = ("sc", "原油", Exchange.INE, _PRODUCE_N_RELAX_END_HM_3)
    IC = ("IC", "500股指", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    IF = ("IF", "300股指", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    IH = ("IH", "50股指", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    IM = ("IM", "1000股指", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    T = ("T", "T", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    TF = ("TF", "TF", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    TS = ("TS", "TS", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    TL = ("TL", "TL", Exchange.CFFEX, _PRODUCE_PM_RELAX_START_HM)
    AP = ("AP", "苹果", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    CF = ("CF", "棉花", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    CJ = ("CJ", "红枣", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    CY = ("CY", "棉纱", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    FG = ("FG", "玻璃", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    JR = ("JR", "粳稻", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    LR = ("LR", "晚粳稻", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    MA = ("MA", "甲醇", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    OI = ("OI", "菜籽油", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    PF = ("PF", "断纤", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    PK = ("PK", "花生", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    PL = ("PL", "丙烯", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    PM = ("PM", "普麦", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    PR = ("PR", "瓶片", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    PX = ("PX", "对二甲苯", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    RI = ("RI", "早籼稻", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    RM = ("RM", "菜籽粕", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    RS = ("RS", "油菜籽", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    SA = ("SA", "纯碱", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    SF = ("SF", "硅铁", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    SH = ("SH", "烧碱", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    SM = ("SM", "锰硅", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    SR = ("SR", "白糖", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    TA = ("TA", "PTA", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    UR = ("UR", "尿素", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    WH = ("WH", "强麦", Exchange.CZCE, _PRODUCE_PM_RELAX_START_HM)
    ZC = ("ZC", "动力煤", Exchange.CZCE, _PRODUCE_N_RELAX_END_HM_1)
    SI = ("si", "工业硅", Exchange.GFEX, _PRODUCE_PM_RELAX_START_HM)
    LC = ("lc", "碳酸锂", Exchange.GFEX, _PRODUCE_PM_RELAX_START_HM)
    PD = ("pd", "钯", Exchange.GFEX, _PRODUCE_PM_RELAX_START_HM)
    PS = ("ps", "多晶硅", Exchange.GFEX, _PRODUCE_PM_RELAX_START_HM)
    PT = ("pt", "铂", Exchange.GFEX, _PRODUCE_PM_RELAX_START_HM)

    def __new__(cls, nm_en: str, nm_cn: str, exchange: Exchange, relax_tm_hms: str) -> "Produce":
        obj: "Produce" = object.__new__(cls)
        obj._value_ = nm_en
        obj.nm_en = nm_en
        obj.nm_cn = nm_cn
        obj.exchange = exchange
        obj.relax_tm_hms = relax_tm_hms
        return obj

    @staticmethod
    def _extract_quot_value(source: Any, *names: str) -> Any:
        for name in names:
            if isinstance(source, dict) and name in source:
                return source[name]
            if hasattr(source, name):
                value: Any = getattr(source, name)
                return value() if callable(value) else value
        return None

    @classmethod
    def get_product(cls, symbol: str) -> "Produce | None":
        product: str = re.sub(r"[^A-Za-z]", "", symbol or "")
        for produce in cls:
            if produce.nm_en == product:
                return produce
        return None

    @classmethod
    def is_trade_time(cls, symbol: str, dt_or_hm: DateTime | str) -> bool:
        product: "Produce | None" = cls.get_product(symbol)
        return cls.is_trade_time_by_product(product, dt_or_hm)

    @classmethod
    def is_trade_time_by_product(cls, product: "Produce | None", dt_or_hm: DateTime | str) -> bool:
        if product is None:
            return False

        if isinstance(dt_or_hm, str):
            unsigned_hms: str = dt_or_hm
            if len(unsigned_hms) == 4:
                unsigned_hms = f"{unsigned_hms}00"
        else:
            unsigned_hms = dt_or_hm.strftime("%H%M%S")

        if product.exchange != Exchange.CFFEX:
            if _PRODUCE_BB_RELAX_START_HM <= unsigned_hms < _PRODUCE_BB_RELAX_END_HM:
                return False
            if _PRODUCE_AF_RELAX_START_HM <= unsigned_hms < _PRODUCE_AF_RELAX_END_HM_2:
                return False
            if _PRODUCE_PM_RELAX_START_HM <= unsigned_hms < _PRODUCE_PM_RELAX_END_HM:
                return False

            if product.relax_tm_hms == _PRODUCE_PM_RELAX_START_HM:
                if unsigned_hms >= _PRODUCE_PM_RELAX_START_HM or unsigned_hms < _PRODUCE_AM_RELAX_END_HM_1:
                    return False
            elif product.relax_tm_hms == _PRODUCE_N_RELAX_END_HM_1:
                if unsigned_hms >= _PRODUCE_N_RELAX_END_HM_1 or unsigned_hms < _PRODUCE_AM_RELAX_END_HM_1:
                    return False
            elif product.relax_tm_hms == _PRODUCE_N_RELAX_END_HM_2:
                if _PRODUCE_N_RELAX_END_HM_2 <= unsigned_hms < _PRODUCE_AM_RELAX_END_HM_1:
                    return False
            elif product.relax_tm_hms == _PRODUCE_N_RELAX_END_HM_3:
                if _PRODUCE_N_RELAX_END_HM_3 <= unsigned_hms < _PRODUCE_AM_RELAX_END_HM_1:
                    return False
        else:
            if unsigned_hms < _PRODUCE_AM_RELAX_END_HM_2:
                return False
            if _PRODUCE_AF_RELAX_START_HM <= unsigned_hms < _PRODUCE_AF_RELAX_END_HM_1:
                return False
            if unsigned_hms >= _PRODUCE_PM_RELAX_START_HM:
                return False

        return True

    @classmethod
    def update_quot(cls, new_quot: Any) -> None:
        instrument_id: Any = cls._extract_quot_value(
            new_quot,
            "instrument_id",
            "instrumentID",
            "InstrumentID",
            "getInstrumentID",
        )
        open_interest: Any = cls._extract_quot_value(
            new_quot,
            "open_interest",
            "openInterest",
            "OpenInterest",
            "getOpenInterest",
        )

        if instrument_id is None or open_interest is None:
            return

        instrument_id = str(instrument_id)
        product: Produce | None = cls.get_product(instrument_id)
        if product is None:
            return

        interest: int = int(open_interest)
        cls._INSTRUMENT_INTEREST[instrument_id] = interest

        main_instrument_list: list[str] | None = cls._MAIN_INSTRUMENT.get(product)
        if main_instrument_list is None:
            cls._MAIN_INSTRUMENT[product] = [instrument_id]
            return

        if instrument_id not in main_instrument_list:
            if interest > cls._INSTRUMENT_INTEREST.get(main_instrument_list[0], 0):
                main_instrument_list.insert(0, instrument_id)
            elif (
                len(main_instrument_list) == cls._MAIN_INSTRUMENT_SIZE
                and interest > cls._INSTRUMENT_INTEREST.get(main_instrument_list[1], 0)
            ):
                main_instrument_list.pop()
                main_instrument_list.append(instrument_id)

            while len(main_instrument_list) > cls._MAIN_INSTRUMENT_SIZE:
                main_instrument_list.pop()

    @classmethod
    def is_main_instrument(cls, symbol: str) -> bool:
        product: Produce | None = cls.get_product(symbol)
        if product is None:
            return False

        instrument_list: list[str] | None = cls._MAIN_INSTRUMENT.get(product)
        return bool(instrument_list and symbol in instrument_list)

    @classmethod
    def get_main_instrument(cls) -> dict["Produce", list[str]]:
        return cls._MAIN_INSTRUMENT

    @classmethod
    def set_main_instrument(cls, mapping: dict["Produce", list[str]]) -> None:
        cls._MAIN_INSTRUMENT.clear()
        cls._MAIN_INSTRUMENT.update({key: list(value) for key, value in mapping.items()})

    @classmethod
    def is_mini_instrument(cls, product: "Produce | None") -> bool:
        if product is None:
            return False

        return product in {
            cls.TS,
            cls.TF,
            cls.T,
            cls.TL,
            cls.LR,
            cls.JR,
            cls.ZC,
            cls.RI,
            cls.PM,
            cls.WH,
            cls.RS,
            cls.WR,
            cls.RR,
            cls.BB,
            cls.FB,
        }

    def is_mini(self) -> bool:
        return type(self).is_mini_instrument(self)

    @classmethod
    def clean(cls) -> None:
        cls._INSTRUMENT_INTEREST.clear()
        cls._MAIN_INSTRUMENT.clear()


Produce._INSTRUMENT_INTEREST = {}
Produce._MAIN_INSTRUMENT_SIZE = 2
Produce._MAIN_INSTRUMENT = {}
