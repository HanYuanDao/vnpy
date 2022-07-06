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
import time

"""
展示基础策略
"""


class JmjtBigMarket(CtaTemplate):
    # 声明作者
    author = "Jason Han"

    # 声明参数，由交易员指定
    const_volume = 1
    const_sec_interval_price_open = 10 * 60
    const_price_ratio_highest_lowest_10min = 1.008
    const_volume_ratio_long_short_open = 3
    const_volume_thr_short_open = 150
    const_point_interval_lowest_price_today_open = 10
    const_over_price_1_open = 5
    const_over_price_2_open = 1
    const_tick_num_interval_failed_open = 2
    const_tick_num_stop_loss = 5
    const_over_price_stop_loss = 5
    const_tick_num_interval_failed_stop_loss = 2
    const_profit_point_c1_stop_profit = 20
    const_ratio_now_profit_max_profit_c1_stop_profit = 0.7
    const_over_price_c1_stop_profit = 5
    const_profit_point_c2_stop_profit = 5
    const_tick_num_c2_stop_profit = 30
    const_price_wave_c2_stop_profit = 5
    const_volume_ratio_long_short_c3_stop_profit = 3
    const_volume_num_short_c3_stop_profit = 50
    const_over_price_c3_stop_profit = 2
    const_tick_num_interval_failed_stop_profit = 2
    const_profit_max_drawdown_ratio = 0.5
    parameters = [
        "const_volume",
        "const_price_ratio_highest_lowest_10min",
        "const_volume_ratio_long_short_open",
        "const_volume_thr_short_open",
        "const_point_interval_lowest_price_today_open",
        "const_over_price_1_open",
        "const_over_price_2_open",
        "const_tick_num_interval_failed_open",
        "const_tick_num_stop_loss",
        "const_over_price_stop_loss",
        "const_tick_num_interval_failed_stop_loss",
        "const_profit_point_c1_stop_profit",
        "const_ratio_now_profit_max_profit_c1_stop_profit",
        "const_profit_point_c2_stop_profit",
        "const_tick_num_c2_stop_profit",
        "const_price_wave_c2_stop_profit",
        "const_volume_ratio_long_short_c3_stop_profit",
        "const_volume_num_short_c3_stop_profit",
        "const_tick_num_interval_failed_stop_profit",
        "const_profit_max_drawdown_ratio",
    ]

    # 声明变量，在程序运行时变化
    # 最先变动价格
    price_tick = 0.0
    # 开仓的价格
    open_price = 0.0
    # 10分钟之内tick
    tick_10min_queue: collections.deque = collections.deque()
    tick_10min_queue_size = 0
    highest_price_10min = 0.0
    lowest_price_10min = 0.0
    # 当日最低成交价
    lowest_price_today = float("inf")
    # 30跳内tick
    tick_30_queue: collections.deque = collections.deque()
    tick_30_queue_size = 0
    # 亏损或盈利的tick数
    tick_num_profit = 0
    tick_num_loss = 0
    insert_order_num = 0
    # 当前回合的最大盈利
    now_round_max_profit = 0
    # 当日最大盈利
    max_profit = 0
    # 当前的盈亏
    profit_now_value = 0
    tick_num_interval_failed_open = 0
    tick_num_interval_failed_stop_profit = 0
    tick_num_interval_failed_stop_loss = 0
    # 策略是否启动
    strategy_running = False
    # 策略交易的状态，
    # 0：不进行任何活动
    # 1：开始开仓
    # 5：已持仓
    # 10：开始止损
    # 20：开始止盈（超5平仓）
    # 21：开始止盈（超2平仓）
    strategy_trade_state = 0
    strategy_trade_memo = ''
    variables = [
        "price_tick",
        "open_price",
        "tick_10min_queue",
        "tick_10min_queue_size",
        "highest_price_10min",
        "lowest_price_10min",
        "lowest_price_today",
        "tick_30_queue",
        "tick_30_queue_size",
        "tick_num_profit",
        "tick_num_loss",
        "insert_order_num",
        "now_round_max_profit",
        "max_profit",
        "profit_now_value",
        "tick_num_interval_failed_open",
        "tick_num_interval_failed_stop_profit",
        "tick_num_interval_failed_stop_loss",
        "strategy_running",
        "strategy_trade_state",
        "strategy_trade_memo",
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

        self.reset_tmp_variable()

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
        # 将tick数据推送给bg以使其生成k线
        self.bg.update_tick(tick)

        # 去除非交易时间的数据
        if tick.datetime.hour <= 8 or 12 < tick.datetime.hour < 21:
            return

        # 基于tick级高频交易的特点，如果跨天则重置之前的临时变量
        if self.tick_10min_queue_size != 0:
            t = self.tick_10min_queue.popleft()
            if t.datetime.day != tick.datetime.day:
                self.reset_tmp_variable()
            # 策略进行的成交均价队列数量足够
            else:
                self.tick_10min_queue.appendleft(t)

        # 编辑与行情数据相关的指标
        self.build_quot_parameter(tick)

        # 交易逻辑判断
        if self.tick_10min_queue_size != 0:
            if self.strategy_trade_state == 1 and self.pos >= 0:
                self.open(tick)
            elif self.strategy_trade_state == 10 and self.pos < 0:
                self.close4stop_loss(tick)
            elif (
                    self.strategy_trade_state == 20 or self.strategy_trade_state == 21
                    and self.pos < 0
            ):
                self.close4stop_profit(tick)
            else:
                self.trade_strategy(tick)

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

    # 策略委托回报
    def on_order(self, order: OrderData):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()

    # 策略成交回报
    def on_trade(self, trade: TradeData):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.build_trade_parameter(trade)

        self.put_event()

    # 策略停止单回报
    def on_stop_order(self, stop_order: StopOrder):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()

    # 编辑行情相关变量
    def build_quot_parameter(self, tick: TickData):
        tick_datetime = int(time.mktime(tick.datetime.timetuple())) * 1000 + int(tick.datetime.microsecond / 1000)

        # 添加最新的tick数据到近十分钟的tick队列
        self.tick_10min_queue.append(tick)
        self.tick_10min_queue_size += 1
        # 近十分钟的tick队列中剔除不需要的元素
        while self.tick_10min_queue_size > 1:
            mpt = self.tick_10min_queue.popleft()
            self.tick_10min_queue_size -= 1
            mpt_datetime = int(time.mktime(mpt.datetime.timetuple())) * 1000 + int(mpt.datetime.microsecond / 1000)
            if tick_datetime - mpt_datetime <= self.const_sec_interval_price_open * 1000:
                self.tick_10min_queue.appendleft(mpt)
                self.tick_10min_queue_size += 1
                break
            else:
                continue

        # 添加最新的tick数据到近30跳的tick队列
        self.tick_30_queue.append(tick)
        self.tick_30_queue_size += 1
        # 近30跳的tick队列中剔除不需要的元素
        while self.tick_30_queue_size > self.const_tick_num_c2_stop_profit:
            self.tick_30_queue.popleft()
            self.tick_30_queue_size -= 1

        # 更新本次持仓的最大盈利
        if self.strategy_trade_state == 5:
            now_profit = tick.last_price - tick.open_price
            if self.now_round_max_profit > now_profit:
                self.now_round_max_profit = now_profit

        self.lowest_price_today = tick.last_price if tick.last_price < self.lowest_price_today \
            else self.lowest_price_today

    def build_10min_parameter(self):
        # 获取最近五分钟成交价中的最高点与最低点
        max_last_price = 0.0
        min_last_price = 0.0
        length = self.tick_10min_queue_size
        while length > 0:
            mpt = self.max_min_last_price_queue.popleft()
            if mpt.last_price > max_last_price:
                max_last_price = mpt.last_price
            if mpt.last_price < min_last_price:
                min_last_price = mpt.last_price
            self.max_min_last_price_queue.append(mpt)
            length -= 1
        self.highest_price_10min = max_last_price
        self.lowest_price_10min = min_last_price

    # 编辑交易相关变量
    def build_trade_parameter(self, trade: TradeData):
        # 交易相关参数重置
        if self.strategy_trade_state == 1:
            self.open_price = trade.price

            self.tick_num_interval_failed_open = 0
            self.tick_num_interval_failed_stop_profit = 0
            self.tick_num_interval_failed_stop_loss = 0
        elif (self.strategy_trade_state == 10
              or self.strategy_trade_state == 20
              or self.strategy_trade_state == 21):
            self.tick_num_profit = 0
            self.tick_num_loss = 0

            # 平空仓 计算该空仓的开平仓回合的盈利情况
            round_profit_loss = (self.open_price - trade.price) * self.const_volume
            self.profit_now_value += round_profit_loss

            if self.profit_now_value > self.max_profit:
                self.max_profit = self.profit_now_value

        # 策略交易意图状态变更
        if self.strategy_trade_state == 1:
            self.strategy_trade_state = 5
        elif self.strategy_trade_state == 10:
            self.strategy_trade_state = 0
        elif self.strategy_trade_state == 20 or self.strategy_trade_state == 21:
            self.strategy_trade_state = 0
        else:
            self.write_log("不正常的策略交易状态")

    # 交易策略
    def trade_strategy(self, tick: TickData):
        # 当前不存在空仓
        if self.pos >= 0:
            if not self.strategy_running and self.run_strategy(tick):
                self.strategy_running = True

            if self.strategy_running:
                self.open(tick)
        else:
            # 获得盈利or亏损的行情tick数
            if tick.last_price > self.open_price:
                self.tick_num_loss += 1
            else:
                self.tick_num_profit += 1

            # 止损判断
            if tick.last_price > self.open_price:
                self.close4stop_loss(tick)
            # 止盈判断
            else:
                self.close4stop_profit(tick)

        self.stop_strategy(tick)

    # 判断策略是否启动
    def run_strategy(self, tick: TickData) -> bool:
        length = self.tick_10min_queue_size
        lowest_tick: TickData = None
        highest_tick: TickData = None
        tick_10min_queue_new: collections.deque = collections.deque()
        while length > 0:
            tick = self.tick_10min_queue.popleft()
            if lowest_tick is None:
                lowest_tick = tick
                highest_tick = tick
            else:
                if lowest_tick.last_price > tick.last_price:
                    lowest_tick = tick
                if highest_tick.last_price < tick.last_price:
                    highest_tick = tick
            tick_10min_queue_new.append(tick)
            length -= 1
        self.tick_10min_queue = tick_10min_queue_new

        return highest_tick.last_price >= lowest_tick.last_price * 1.008

    def stop_strategy(self, tick: TickData) -> bool:
        if self.pos == 0 and self.strategy_running and self.strategy_trade_state != 1:
            if (0.0 < self.profit_now_value < self.max_profit * self.const_profit_max_drawdown_ratio) \
                    or (self.profit_now_value < -10000):
                self.build_10min_parameter()
                if self.highest_price_10min <= self.lowest_price_10min * self.const_price_ratio_highest_lowest_10min:
                    self.strategy_running = False

    # 开仓逻辑
    def open(self, tick: TickData):
        if self.strategy_trade_state == 0:
            self.strategy_trade_memo = str(self.pos) + "os"
            # 开仓条件一
            bid_volume_total = \
                tick.bid_volume_1 + tick.bid_volume_2 + \
                tick.bid_volume_3 + tick.bid_volume_4 + tick.bid_volume_5
            ask_volume_total = \
                tick.ask_volume_1 + tick.ask_volume_2 + \
                tick.ask_volume_3 + tick.ask_volume_4 + tick.ask_volume_5
            cond1 = bid_volume_total * 3 <= ask_volume_total
            # 开仓条件二
            cond2 = ask_volume_total >= 150
            if cond1:
                self.strategy_trade_memo += "-c1"
            if cond2:
                self.strategy_trade_memo += "-c2"
            if cond1 or cond2:
                # 开空仓
                self.strategy_trade_memo += "-" + str(self.insert_order_num)
                self.add_trade_intention(tick.datetime, self.strategy_trade_memo)
                self.strategy_trade_state = 1
                self.insert_order4open(tick)
        elif self.strategy_trade_state == 1:
            if self.pos == 0:
                self.tick_num_interval_failed_open += 1
                if self.tick_num_interval_failed_open > self.const_tick_num_interval_failed_open:
                    self.insert_order4open(tick)
        else:
            self.write_log("开仓时碰到未知的状态")

    # 平仓-止盈逻辑
    def close4stop_profit(self, tick: TickData):
        if self.strategy_trade_state == 5:
            self.strategy_trade_memo = str(self.pos) + "sp"
            # 止盈条件一：当盈利大雨20个点且利润比最大盈利时刻回撤了30%
            now_profit = tick.last_price - self.open_price
            cond1 = ((self.open_price - tick.last_price > self.const_profit_point_c1_stop_profit)
                     and (now_profit <= self.now_round_max_profit * 0.7))
            if cond1:
                self.strategy_trade_memo += "-c1"
            # 止盈条件二：当盈利大于5时，成交价最近30个tick内波动小于5个点（区间内成交最高价-最低价）
            cond2 = (
                    self.open_price - tick.last_price > 5
                    and self.is_min_volatility_30tick())
            if cond2:
                self.strategy_trade_memo += "-c2"
            # 止盈条件三：五档内多方总单量/空方总单量≥3，且多方总单量≥50
            bid_volume_total = \
                tick.bid_volume_1 + tick.bid_volume_2 + tick.bid_volume_3 + \
                tick.bid_volume_4 + tick.bid_volume_5
            ask_volume_total = \
                tick.ask_volume_1 + tick.ask_volume_2 + tick.ask_volume_3 + \
                tick.ask_volume_4 + tick.ask_volume_5
            cond3 = (
                    bid_volume_total >= ask_volume_total * self.const_volume_ratio_long_short_c3_stop_profit
                    and bid_volume_total > self.const_volume_num_short_c3_stop_profit
            )
            if cond3:
                self.strategy_trade_memo += "-c3"
            if cond1 or cond3:
                # 平空仓 止盈
                self.strategy_trade_memo += "-" + str(self.insert_order_num)
                self.add_trade_intention(tick.datetime, self.strategy_trade_memo)
                self.strategy_trade_state = 20
                self.insert_order4stop_profit(tick)
            elif cond2:
                # 平空仓 止盈
                self.strategy_trade_memo += "-" + str(self.insert_order_num)
                self.add_trade_intention(tick.datetime, self.strategy_trade_memo)
                self.strategy_trade_state = 21
                self.insert_order4stop_profit(tick)
        elif self.strategy_trade_state == 20 or self.strategy_trade_state == 21:
            if self.pos < 0:
                self.tick_num_interval_failed_stop_profit += 1
                if self.tick_num_interval_failed_stop_profit > self.const_tick_num_interval_failed_stop_profit:
                    self.insert_order4stop_profit(tick)
        else:
            self.write_log("止盈时碰到未知的状态")

    def is_min_volatility_30tick(self) -> bool:
        length = self.tick_30_queue_size
        highest_tick: TickData = None
        lowest_tick: TickData = None
        tick_30_queue_new: collections.deque = collections.deque()
        while length > 0:
            tick = self.tick_30_queue.popleft()
            if highest_tick is None:
                highest_tick = tick
                lowest_tick = tick
            else:
                if highest_tick.last_price < tick.last_price:
                    highest_tick = tick
                if lowest_tick.last_price > tick.last_price:
                    lowest_tick = tick
            tick_30_queue_new.append(tick)
            length -= 1
        self.tick_30_queue = tick_30_queue_new

        return highest_tick.last_price - lowest_tick.last_price < 5

    # 平仓-止损逻辑
    def close4stop_loss(self, tick: TickData):
        if self.strategy_trade_state == 1:
            self.strategy_trade_memo = str(self.pos) + "sl"
            # 止损条件一：浮亏超过5跳则平仓
            cond1 = self.tick_num_loss > 5
            if cond1:
                self.strategy_trade_memo += "-c1"
            if cond1:
                # 平空仓 止损
                self.strategy_trade_memo += "-" + str(self.insert_order_num)
                self.add_trade_intention(tick.datetime, self.strategy_trade_memo)
                self.strategy_trade_state = 10
                self.insert_order4stop_loss(tick)
        elif self.strategy_trade_state == 10:
            if self.pos < 0:
                self.tick_num_interval_failed_stop_loss += 1
                if self.tick_num_interval_failed_stop_loss > self.const_tick_num_interval_failed_stop_loss:
                    self.insert_order4stop_loss(tick)
        else:
            self.write_log("止损时碰到未知的状态")

    # 报单-开仓
    def insert_order4open(self, tick: TickData):
        self.insert_order_num += 1
        self.cancel_all()
        if tick.last_price - self.lowest_price_today <= 10:
            self.short(tick.ask_price_1 - self.price_tick * self.const_over_price_1_open, self.const_volume,
                       memo=self.strategy_trade_memo)
        else:
            self.short(tick.ask_price_1 - self.price_tick * self.const_over_price_2_open, self.const_volume,
                       memo=self.strategy_trade_memo)

    # 报单-止盈
    def insert_order4stop_profit(self, tick: TickData):
        self.insert_order_num += 1
        self.cancel_all()
        if self.strategy_trade_state == 20:
            self.buy(tick.bid_price_1 + self.price_tick * self.const_over_price_c1_stop_profit, self.const_volume, lock=False,
                     memo=self.strategy_trade_memo)
        elif self.strategy_trade_state == 21:
            self.buy(tick.bid_price_1 + self.price_tick * self.const_over_price_c3_stop_profit, self.const_volume, lock=False,
                     memo=self.strategy_trade_memo)

    # 报单-止损
    def insert_order4stop_loss(self, tick: TickData):
        self.insert_order_num += 1
        self.cancel_all()
        self.buy(tick.bid_price_1 + self.price_tick * self.const_over_price_stop_loss, self.const_volume, lock=False,
                 memo=self.strategy_trade_memo)

    def reset_tmp_variable(self):
        self.price_tick = 0.0
        self.open_price = 0.0
        self.tick_10min_queue = collections.deque()
        self.tick_10min_queue_size = 0
        self.highest_price_10min = 0.0
        self.lowest_price_10min = 0.0
        self.lowest_price_today = 0.0
        self.tick_30_queue = collections.deque()
        self.tick_30_queue_size = 0
        self.tick_num_profit = 0
        self.tick_num_loss = 0
        self.insert_order_num = 0
        self.now_round_max_profit = 0
        self.max_profit = 0
        self.profit_now_value = 0
        self.tick_num_interval_failed_open = 0
        self.tick_num_interval_failed_stop_profit = 0
        self.tick_num_interval_failed_stop_loss = 0
        self.strategy_running = False
        self.strategy_trade_state = 0
        self.strategy_trade_memo = ""

