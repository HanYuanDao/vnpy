from vnpy_ctastrategy import (
    # CTA策略模版
    CtaTemplate,
    # 以下五个均为储存对应信息的数据容器
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    # K线生成模块
    BarGenerator,
    # K线时间序列管理模块
    ArrayManager
)

import numpy as np
from queue import Queue

import datetime as dt
import pytz

"""
展示基础策略
"""


class OwnGoal(CtaTemplate):
    # 声明作者
    author = "Jason Han"

    # 声明参数，由交易员指定
    volume = 1
    offset_msg_length = 20
    break_high_msg_length = 12
    ratio_long_short_open = 0.5
    ratio_long_short_stopprofit = 3
    overprice = 5
    timeout = 1
    parameters = [
        "volume",
        "offset_msg_length",
        "break_high_msg_length",
        "ratio_long_short_open",
        "ratio_long_short_stopprofit",
        "overprice",
        "timeout"
    ]

    # 声明变量，在程序运行时变化
    SHA_TZ = dt.timezone(
        dt.timedelta(hours=8),
        name='Asia/Shanghai',
    )

    # trade_starttime = dt.datetime(2022, 1, 7, 9, 0, 0, tzinfo=pytz.timezone(SHA_TZ))
    # trade_starttime = dt.datetime(2022, 1, 7, 9, 0, 0).replace(tzinfo=pytz.timezone('Asia/Shanghai'))
    trade_starttime = pytz.timezone('Asia/Shanghai').localize(dt.datetime(2022, 1, 7, 9, 0, 0))
    # trade_starttime.astimezone(SHA_TZ)
    price_tick = 0
    open_standby = False
    open_standby_mean = 0.0
    lastprice_list: np.ndarray = np.zeros(offset_msg_length)
    open_price = 0.0
    tick_num_profit = 50
    tick_num_loss = 20
    profit_max_value = 0
    variables = [
        "trade_starttime",
        "price_tick",
        "open_standby",
        "open_standby_mean",
        "tickdata_list",
        "open_price",
        "tick_num_profit",
        "tick_num_loss",
        "profit_max_value"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 调用K线生成模块，从tick数据合成分钟k线
        self.bg = BarGenerator(self.on_bar)

        # 调用K线时间序列管理模块
        self.am = ArrayManager()

    """
    CatTemplate中以on开头的函数都是回调函数，用来接受数据和状态变更。
    """

    # 策略初始化
    def on_init(self):
        self.write_log("策略初始化")

        # 加载历史数据回测，加载10天
        # self.load_bar(10)
        # 加载tick数据回测，加载30天
        self.load_tick(30)

    # 策略启动
    def on_start(self):
        self.write_log("策略启动")

        self.price_tick = self.get_pricetick()

        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()

    # 策略停止
    def on_stop(self):
        self.write_log("策略停止")

        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()

    # 获得tick数据推送
    def on_tick(self, tick: TickData):
        if tick.datetime < self.trade_starttime:
            return

        if tick.datetime.hour < self.trade_starttime.hour:
            return

        # 将tick数据推送给bg以使其生成k线
        # self.bg.update_tick(tick)

        # 最新价数组
        if self.lastprice_list[0] != 0:
            if self.pos == 0:
                if not self.open_standby:
                    mean = np.mean(self.lastprice_list)
                    if tick.last_price > (mean * 1.03):
                        self.open_standby_mean = mean
                        self.open_standby = True
                else:
                    if tick.last_price <= (self.open_standby_mean * 1.015):
                        self.open_standby_mean = 0.0
                        self.open_standby = False

                if self.open_standby:
                    # 开仓条件一
                    bid_volume_total = tick.bid_volume_1 + tick.bid_volume_2 + tick.bid_volume_3 + tick.bid_volume_4 + tick.bid_volume_5
                    ask_volume_total = tick.ask_volume_1 + tick.ask_volume_2 + tick.ask_volume_3 + tick.ask_volume_4 + tick.ask_volume_5
                    cond1 = bid_volume_total < ask_volume_total * self.ratio_long_short_open
                    # 开仓条件二
                    offest = self.offset_msg_length - self.break_high_msg_length
                    cond2 = np.max(self.lastprice_list[offest:]) < tick.last_price
                    if cond1 or cond2:
                        # 开空仓
                        self.short(tick.ask_price_1 - self.price_tick * self.overprice, self.volume)
            else:
                self.profit_max_value = self.open_price - tick.last_price
                if self.profit_max_value > 0:
                    self.tick_num_profit += 1
                else:
                    self.tick_num_loss += 1

                # 止损判断
                if tick.last_price > self.open_price:
                    # 止损条件一
                    cond1 = self.open_price == tick.high_price
                    # 止损条件二
                    cond2 = self.tick_num_loss > self.tick_num_loss
                    if cond1 or cond2:
                        self.sell(tick.ask_price_1 + self.price_tick * self.overprice, self.volume)
                # 止盈判断
                else:
                    # 止盈条件一
                    bid_volume_total = tick.bid_volume_1 + tick.bid_volume_2 + tick.bid_volume_3 + tick.bid_volume_4 + tick.bid_volume_5
                    ask_volume_total = tick.ask_volume_1 + tick.ask_volume_2 + tick.ask_volume_3 + tick.ask_volume_4 + tick.ask_volume_5
                    cond1 = bid_volume_total < ask_volume_total * self.ratio_long_short_stopprofit
                    # 止盈条件二
                    cond2 = self.tick_num_profit > self.tick_num_profit and self.profit_max_value
                    if cond1 or cond2:
                        self.sell(tick.ask_price_1 + self.price_tick * self.overprice, self.volume)

        self.lastprice_list[:-1] = self.lastprice_list[1:]
        self.lastprice_list[-1] = tick.last_price

    # 获得bar数据推送
    def on_bar(self, bar: BarData):
        # 需要bg生成更周期的k线时，将分钟k线再推送给bg
        self.bg.update_bar(bar)
        # self.am.update_bar(bar)

    """
    委托状态更新
    """

    # 策略成交回报
    def on_trade(self, trade: TradeData):
        self.open_price = trade.price
        self.tick_num_profit = 0
        self.tick_num_loss = 0

        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()

    # 策略委托回报
    def on_order(self, order: OrderData):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()

    # 策略停止单回报
    def on_stop_order(self, stop_order: StopOrder):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()
