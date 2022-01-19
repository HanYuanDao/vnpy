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

"""展示基础策略"""
class DemoStratepy(CtaTemplate):
    # 声明作者
    author = "Jason Han"

    # 声明参数，由交易员指定
    second = 3
    ratio = 0.5
    overprice = 5
    timeout = 1
    parameters = [
        "second",
        "ratio",
        "overprice",
        "timeout"
    ]

    # 声明变量，在程序运行时变化
    order_list = []
    variables = [
        "order_list"
    ]

    def __init__(self, cta_engine: Any, strategy_name: str, vt_symbol: str, setting: dict):
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
        return

    # 策略启动
    def on_start(self):
        self.write_log("策略启动")
        
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()
        return

    # 策略停止
    def on_stop(self):
        self.write_log("策略停止")
        
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()
        return
    
    # 获得tick数据推送
    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

        return 

    # 获得bar数据推送
    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)

        return

    """
    委托状态更新
    """
    # 策略成交回报
    def on_trade(self, trade: TradeData):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()        
        return
    
    # 策略委托回报
    def on_order(self, order: OrderData):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()
        return

    # 策略停止单回报
    def on_stop_order(self, stop_order: StopOrder):
        # 通知图形界面更新（策略最新状态）
        # 不调用该函数则界面不会变化
        self.put_event()
        return

    