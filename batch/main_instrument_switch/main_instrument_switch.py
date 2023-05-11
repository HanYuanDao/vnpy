from datetime import datetime, date, timedelta, timezone
from enum import Enum
import json
import os

import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import pandas as pd
from pandas import DataFrame
import traceback
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_ctastrategy.strategies.the_boll_tactic_of_nd import TheBollTacticOfND
from vnpy_ctastrategy.base import BacktestingMode


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
    SSE = "SSE"             # Shanghai Stock Exchange
    SZSE = "SZSE"           # Shenzhen Stock Exchange
    BSE = "BSE"             # Beijing Stock Exchange
    SGE = "SGE"             # Shanghai Gold Exchange
    WXE = "WXE"             # Wuxi Steel Exchange
    CFETS = "CFETS"         # CFETS Bond Market Maker Trading System
    XBOND = "XBOND"         # CFETS X-Bond Anonymous Trading System


class MainInstrumentSwitch:
    fold_path_root = "./"   # fold_path_root = "./main_instrument_switch/"
    file_path_strategy_info = fold_path_root + "strategy_info.json"
    file_path_instrument_info = fold_path_root + "instrument_info.json"
    fold_path_export = fold_path_root + "export/"

    def get_symbol_tm_map(self, exchange: Exchange, product: str, start_time: datetime, end_time: datetime):
        output = {}
        month_map = self.split_month(exchange, start_time, end_time)
        for k, v in month_map.items():
            output[self.get_instrument_id(exchange, product, k)] = [k, v]
        return output

    def split_month(self, exchange: Exchange, start_time: datetime, end_time: datetime):
        map = {}
        final_time = start_time
        while final_time <= end_time:
            final_time_new = self.get_main_month(exchange, final_time) - timedelta(days=1)

            if final_time_new > end_time:
                final_time_new = end_time
            map[final_time] = final_time_new
            final_time = final_time_new + timedelta(days=1)
        return map

    def get_main_month(self, exchange: Exchange, tm: datetime) -> datetime:
        mouth = tm.month
        main_time = tm.replace(day=1)
        if exchange in [Exchange.SHFE, Exchange.INE]:
            if mouth != 12:
                main_time = main_time.replace(month=(main_time.month + 1))
            else:
                main_time = main_time.replace(year=main_time.year + 1, month=1)
        else:
            if 1 <= mouth < 5:
                main_time = main_time.replace(month=5)
            elif 5 <= mouth < 9:
                main_time = main_time.replace(month=9)
            else:
                main_time = main_time.replace(year=main_time.year + 1, month=1)
        return main_time

    def get_instrument_id(self, exchange: Exchange, product: str, trade_time: datetime) -> str:
        trade_time = self.get_main_month(exchange, trade_time)

        if exchange == Exchange.CZCE:
            tm_str = trade_time.strftime('%Y%m')[3:6]
        else:
            tm_str = trade_time.strftime('%Y%m')[2:6]

        return product + tm_str

    def __init__(self, vt_symbol_config="instrument_info.json", export_path=".//"):
        """
        加载配置路径
        """
        self.setting = json.load(open(MainInstrumentSwitch.file_path_instrument_info))
        self.export_path = MainInstrumentSwitch.fold_path_export
        self.engine = None

    def add_parameters(self, vt_symbol: str, symbol_flag: str, start_date, end_date, interval="1_minute"):
        """
        从vtSymbol.json文档读取品种的交易属性，比如费率，交易每跳，比率，滑点
        """
        if symbol_flag in self.setting:
            self.engine.set_parameters(
                vt_symbol=vt_symbol,
                interval=interval,
                start=start_date,
                end=end_date,
                rate_money=self.setting[symbol_flag]["rate_money"],
                rate_volume=self.setting[symbol_flag]["rate_volume"],
                slippage=self.setting[symbol_flag]["slippage"],
                size=self.setting[symbol_flag]["size"],
                pricetick=self.setting[symbol_flag]["pricetick"],
                capital=self.setting[symbol_flag]["capital"],
                mode=BacktestingMode.BAR
            )
        else:
            print("symbol %s hasn't be maintained in config file" % vt_symbol)

    def run_batch_test(self, strategy_setting, portfolio):
        """
        进行回测
        """
        result_df = DataFrame()
        net_pnl_df = None
        trade_pairs = []
        for strategy_name, strategy_config in strategy_setting.items():
            start_date = datetime.strptime(strategy_config["start_dt"], '%Y-%m-%d')
            end_date = datetime.strptime(strategy_config["end_dt"], '%Y-%m-%d') + timedelta(days=1)
            exchange_produce_list = strategy_config["products"]
            for exchange_produce in exchange_produce_list:
                exchange = exchange_produce["exchange"]
                produce = exchange_produce["product"]
                symbol_flag = produce + "." + exchange
                symbol_tm_map = self.get_symbol_tm_map(exchange, produce, start_date, end_date)

                for symbol, tm_arr in symbol_tm_map.items():
                    self.engine = BacktestingEngine()
                    print("合约以及查询日期区间：" + symbol + " " + tm_arr[0].strftime('%Y%m%d') + " " + tm_arr[1].strftime('%Y%m%d'))
                    print(strategy_config["setting"])
                    self.add_parameters(symbol + "." + exchange, symbol_flag, tm_arr[0], tm_arr[1])
                    if type(strategy_config["setting"]) is str:
                        self.engine.add_strategy(
                            eval(strategy_config["class_name"]),
                            json.loads(strategy_config["setting"], )
                        )
                    else:
                        self.engine.add_strategy(
                            eval(strategy_config["class_name"]),
                            strategy_config["setting"]
                        )
                    self.engine.load_data()
                    self.engine.run_backtesting()
                    df = self.engine.calculate_result()
                    if df is not None and df.size != 0:
                        if net_pnl_df is None:
                            net_pnl_df = df
                        else:
                            net_pnl_df = pd.concat([net_pnl_df, df])
                    result_dict = self.engine.calculate_statistics(df, False)
                    result_dict["class_name"] = strategy_config["class_name"]
                    result_dict["setting"] = strategy_config["setting"]
                    result_dict["vt_symbol"] = symbol
                    result_df = result_df.append(result_dict, ignore_index=True)

                    trade_pairs += self.engine.generate_trade_pairs()

        # if portfolio is True:
        #     self.engine.calculate_statistics(df_portfolio)
        #     self.engine.show_chart(df_portfolio)
        reduce = {
            'commission': ['min', 'max', 'sum'],
            'slippage': ['min', 'max', 'sum'],
            'trading_pnl': ['min', 'max', 'sum'],
            'holding_pnl': ['min', 'max', 'sum'],
            'total_pnl': ['min', 'max', 'sum'],
            'net_pnl': ['min', 'max', 'sum'],
            'trade_count': ['min', 'max', 'sum'],
            'turnover': ['min', 'max', 'sum'],
        }

        net_pnl_df_pos = net_pnl_df.groupby("date").apply(self.show_stop_pos)
        net_pnl_group_df = net_pnl_df.groupby(['date']).agg(reduce)
        net_pnl_group_df = pd.concat([net_pnl_group_df, net_pnl_df_pos], axis=1)
        net_pnl_group_df.columns.array[-1] = 'pos'

        return result_df, trade_pairs, net_pnl_df, net_pnl_group_df

    def show_stop_pos(self, a: DataFrame):
        symbol_pos_list = {}
        for index, row in a.iterrows():
            print(row)
            if symbol_pos_list.get(row.get('symbol')) is None:
                symbol_pos_list[row.get('symbol')] = 0
            symbol_pos_list[row.get('symbol')] += abs(int(row.get('end_pos')))
        print("-----")
        return symbol_pos_list

    def run_batch_test_json(self, portfolio=True):
        """
        从ctaStrategy.json去读交易策略和参数，进行回测
        """
        with open(MainInstrumentSwitch.file_path_strategy_info, mode="r", encoding="UTF-8") as f:
            strategy_setting = json.load(f)
        result_df, trade_pairs, net_pnl_df, net_pnl_group_df = self.run_batch_test(strategy_setting, portfolio)
        result_df.rename(
            columns={
                'start_date': '首个交易日',
                'end_date': '最后交易日',
                'total_days': '总交易日',
                'profit_days': '盈利交易日',
                'loss_days': '亏损交易日',
                'capital': '起始资金',
                'end_balance': '结束资金',
                'total_return': '总收益率',
                'annual_return': '年化收益',
                'max_drawdown': '最大回撤',
                'max_ddpercent': '百分比最大回撤',
                'max_drawdown_duration': '最长回撤天数',
                'total_net_pnl': '总盈亏',
                'total_commission': '总手续费',
                'total_slippage': '总滑点',
                'total_turnover': '总成交金额',
                't{total_trade_count': '总成交笔数',
                'daily_net_pnl': '日均盈亏',
                'daily_commission': '日均手续费',
                'daily_slippage': '日均滑点',
                'daily_turnover': '日均成交金额',
                't{daily_trade_count': '日均成交笔数',
                'daily_return': '日均收益率',
                'return_std': '收益标准差',
                'sharpe_ratio': 'Sharpe',
                'return_drawdown_ratio': '收益回撤比',
                'success_rate': '交易回合胜率',
            },
            inplace=True
        )
        self.result_excel(result_df, self.export_path + "CTABatch" + str(date.today()) + "overview.xlsx")

        if len(trade_pairs) != 0:
            trade_pairs_df = pd.DataFrame(trade_pairs, columns=[
                "symbol",
                "open_dt", "open_price", "close_dt", "close_price",
                "direction", "volume", "profit_loss", "profit_round",
                "trade_memo_open", "trade_memo_close", "gateway_name"])
            trade_pairs_df["open_dt"] = trade_pairs_df["open_dt"].dt.tz_localize(None)
            trade_pairs_df["close_dt"] = trade_pairs_df["close_dt"].dt.tz_localize(None)
            trade_pairs_df.rename(
                columns={
                    'symbol': '合约',
                    'open_dt': '开仓时间',
                    'open_price': '开仓价格',
                    'close_dt': '锁仓时间',
                    'close_price': '锁仓价格',
                    'direction': '方向',
                    'volume': '手数',
                    'profit_loss': '盈亏',
                    'profit_round': '盈利情况',
                    'trade_memo_open': '开仓说明',
                    'trade_memo_close': '锁仓说明'
                },
                inplace=True
            )
            self.result_excel(trade_pairs_df, self.export_path + "CTABatch" + str(date.today()) + "v1.xlsx")

        self.result_excel(net_pnl_df, self.export_path + "CTABatch" + str(date.today()) + "daily.xlsx")

        self.result_excel(net_pnl_group_df, self.export_path + "CTABatch" + str(date.today()) + "daily_group.xlsx")

        return strategy_setting

    # def run_batch_test_excecl(self, path="ctaStrategy.xls", start_date=datetime(2019, 7, 1),
    #                           end_date=datetime(2020, 1, 1), export_path=None, portfolio=False):
    #     """
    #     从ctaStrategy.excel去读交易策略和参数，进行回测
    #     """
    #     df = pd.read_excel(path)
    #     strategy_setting = df.to_dict(orient='index')
    #     result_df = self.run_batch_test(strategy_setting, start_date, end_date, portfolio)
    #     self.result_excel(result_df, export_path + "CTABatch" + str(date.today()) + "v0.xlsx")
    #
    #     trade_pairs = self.engine.generate_trade_pairs()
    #     self.result_excel(trade_pairs, export_path + "CTABatch" + str(date.today()) + "v1.xlsx")
    #
    #     return strategy_setting

    def result_excel(self, result, export):
        """
        输出交易结果到excel
        """
        if export is not None:
            export_path = export
        else:
            export_path = self.export_path + "CTABatch" + str(date.today()) + "v0.xlsx"

        try:
            result.to_excel(export_path, index=True)
            print("CTA Batch result is export to %s" % export_path)
        except:
            print(traceback.format_exc())

        return None


if __name__ == '__main__':
    print(os.getcwd())
    bts = MainInstrumentSwitch()

    bts.run_batch_test_json()
    print()
