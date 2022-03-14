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

from vnpy.trader.constant import Interval

import numpy as np
from queue import Queue

import datetime as dt
import pytz
import queue
import collections

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
    ratio_long_short_stopprofit = 3
    ratio_long_short_open = 0.5
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
    max_ratio = 0
    price_tick = 0
    open_standby = False
    open_standby_mean = 0.0
    open_price = 0.0
    tick_num_profit = 0
    tick_num_loss = 0
    profit_max_value = 0
    mean_price_tick_queue: collections.deque = collections.deque()
    trade_price_tick_queue: collections.deque = collections.deque()
    trade_price_mean = 0
    trade_price_max = 0
    mean_price_tick_queue_size = 0
    trade_price_tick_queue_size = 0
    max_price_tick: TickData
    const_max_tick_num_profit = 50
    const_max_tick_num_loss = 20
    const_max_backtest_ratio = 0.7
    variables = [
        "max_ratio",
        "price_tick",
        "open_standby",
        "open_standby_mean",
        "tickdata_list",
        "open_price",
        "tick_num_profit",
        "tick_num_loss",
        "profit_max_value",
        "mean_price_tick_queue",
        "trade_price_tick_queue",
        "trade_price_mean",
        "trade_price_max",
        "mean_price_tick_queue_size",
        "trade_price_tick_queue_size",
        "max_price_tick",
        "const_max_tick_num_profit",
        "const_max_tick_num_loss",
        "const_max_backtest_ratio"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 调用K线生成模块，从tick数据合成分钟k线
        self.bg = BarGenerator(self.on_bar, 1, self.on_4tick_bar, Interval.TICK)

        # 调用K线时间序列管理模块
        self.am = ArrayManager()

    """
    CatTemplate中以on开头的函数都是回调函数，用来接受数据和状态变更。
    """

    # 策略初始化
    def on_init(self):
        self.write_log("策略初始化")

        # 加载历史数据回测，加载10天
        self.load_bar(1)
        # 加载tick数据回测，加载30天
        self.load_tick(1)

        self.max_ratio = 0
        self.price_tick = self.get_pricetick()
        self.open_standby = False
        self.open_standby_mean = 0.0
        self.open_price = 0.0
        self.tick_num_profit = 0
        self.tick_num_loss = 0
        self.profit_max_value = 0
        self.mean_price_tick_queue: collections.deque = collections.deque()
        self.trade_price_tick_queue: collections.deque = collections.deque()
        self.trade_price_mean = 0
        self.trade_price_max = 0
        self.mean_price_tick_queue_size = 0
        self.trade_price_tick_queue_size = 0
        self.max_price_tick = TickData

    # 策略启动
    def on_start(self):
        self.write_log("策略启动")

        self.max_ratio = 0
        self.price_tick = self.get_pricetick()
        self.open_standby = False
        self.open_standby_mean = 0.0
        self.open_price = 0.0
        self.tick_num_profit = 0
        self.tick_num_loss = 0
        self.profit_max_value = 0
        self.mean_price_tick_queue: collections.deque = collections.deque()
        self.trade_price_tick_queue: collections.deque = collections.deque()
        self.trade_price_mean = 0
        self.trade_price_max = 0
        self.mean_price_tick_queue_size = 0
        self.trade_price_tick_queue_size = 0
        self.max_price_tick = TickData

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
        # 去除非交易时间的数据
        if tick.datetime.hour <= 8 or 12 < tick.datetime.hour < 21:
            return

        if tick.datetime.day == 7:
            a = 1

        # 将tick数据推送给bg以使其生成k线
        self.bg.update_tick(tick)

        if self.mean_price_tick_queue_size != 0:
            t = self.mean_price_tick_queue.popleft()
            if t.datetime.day != tick.datetime.day:
                self.mean_price_tick_queue.clear()
                self.mean_price_tick_queue_size = 0
                self.trade_price_tick_queue.clear()
                self.trade_price_tick_queue_size = 0
                self.open_standby = False
            else:
                self.mean_price_tick_queue.appendleft(t)

        if self.mean_price_tick_queue_size != 0:
            t = self.mean_price_tick_queue.popleft()
            if (tick.datetime - t.datetime).seconds >= 3:
                self.mean_price_tick_queue.appendleft(t)
                if self.pos >= 0:
                    if not self.open_standby:
                        if tick.last_price >= (self.trade_price_mean * 1.03):
                            self.open_standby = True
                    # else:
                    #     if tick.last_price <= (self.open_standby_mean * 1.015):
                    #         self.open_standby = False

                    if self.open_standby:
                        # 开仓条件一
                        length = self.trade_price_tick_queue_size
                        max_price_tick_3s: TickData = TickData
                        max_price_tick_3s.last_price = 0
                        while length > 0:
                            t = self.trade_price_tick_queue.popleft()
                            if t.last_price > max_price_tick_3s.last_price:
                                max_price_tick_3s = t
                            length -= 1
                            self.trade_price_tick_queue.appendleft(t)
                        cond1 = tick.last_price < max_price_tick_3s.last_price
                        # 开仓条件二
                        bid_volume_total = tick.bid_volume_1 + tick.bid_volume_2 + tick.bid_volume_3 + tick.bid_volume_4 + tick.bid_volume_5
                        ask_volume_total = tick.ask_volume_1 + tick.ask_volume_2 + tick.ask_volume_3 + tick.ask_volume_4 + tick.ask_volume_5
                        cond2 = bid_volume_total < ask_volume_total * self.ratio_long_short_open
                        if cond1 or cond2:
                            # 开空仓
                            self.short(tick.ask_price_1 - self.price_tick * self.overprice, self.volume)
                else:
                    # 获得盈利or亏损的行情tick数
                    profit_now_value = self.open_price - tick.last_price
                    if profit_now_value > 0:
                        self.tick_num_profit += 1
                    else:
                        self.tick_num_loss += 1

                    # 止损判断
                    if tick.last_price > self.open_price:
                        # 止损条件一
                        cond1 = tick.last_price > self.max_price_tick.last_price
                        # 止损条件二
                        cond2 = self.tick_num_loss > self.const_max_tick_num_loss
                        if cond1 or cond2:
                            self.cover(tick.bid_price_1 + self.price_tick * self.overprice, self.volume)
                    # 止盈判断
                    else:
                        # 止盈条件一
                        bid_volume_total = tick.bid_volume_1 + tick.bid_volume_2 + tick.bid_volume_3 + tick.bid_volume_4 + tick.bid_volume_5
                        ask_volume_total = tick.ask_volume_1 + tick.ask_volume_2 + tick.ask_volume_3 + tick.ask_volume_4 + tick.ask_volume_5
                        cond1 = bid_volume_total >= ask_volume_total * self.ratio_long_short_stopprofit
                        # 止盈条件二
                        cond2 = self.tick_num_profit > self.const_max_tick_num_profit and profit_now_value < self.profit_max_value * self.const_max_backtest_ratio
                        if cond1 or cond2:
                            # 平空仓
                            self.cover(tick.bid_price_1 + self.price_tick * self.overprice, self.volume)

                    if profit_now_value > self.profit_max_value:
                        self.profit_max_value = profit_now_value
            else:
                self.mean_price_tick_queue.appendleft(t)

        while self.mean_price_tick_queue_size != 0:
            mpt = self.mean_price_tick_queue.popleft()
            self.mean_price_tick_queue_size -= 1
            if (tick.datetime - mpt.datetime).seconds <= 5:
                self.mean_price_tick_queue.appendleft(mpt)
                self.mean_price_tick_queue_size += 1
                break
            else:
                continue

        while self.trade_price_tick_queue_size != 0:
            tpt = self.trade_price_tick_queue.popleft()
            self.trade_price_tick_queue_size -= 1
            if (tick.datetime - tpt.datetime).seconds <= 3:
                self.trade_price_tick_queue.appendleft(tpt)
                self.trade_price_tick_queue_size += 1
                break
            else:
                if self.trade_price_tick_queue_size == 0:
                    self.trade_price_mean
                else:
                    self.trade_price_mean = (self.trade_price_mean * (self.trade_price_tick_queue_size + 1) - tpt.last_price) / self.trade_price_tick_queue_size
                continue

        self.mean_price_tick_queue.append(tick)
        self.mean_price_tick_queue_size += 1

        self.trade_price_mean = (self.trade_price_mean * self.trade_price_tick_queue_size + tick.last_price) / (self.trade_price_tick_queue_size + 1)
        self.trade_price_tick_queue.append(tick)
        self.trade_price_tick_queue_size += 1

        if self.max_price_tick.last_price <= tick.last_price:
            self.max_price_tick = tick

    # 获得bar数据推送
    def on_bar(self, bar: BarData):
        # 需要bg生成更周期的k线时，将分钟k线再推送给bg
        self.bg.update_bar(bar)
        # self.am.update_bar(bar)

    def on_4tick_bar(self, bar: BarData):
        """"""
        self.put_event()

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
