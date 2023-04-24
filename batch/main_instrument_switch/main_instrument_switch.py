from datetime import datetime, date, timedelta, timezone
from enum import Enum
import json
import os
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
    fold_path_root = "/Users/jasonhan/PyCharmProject/xqvnpy/vnpy/batch/main_instrument_switch/"
    file_path_strategy_info = fold_path_root + "strategy_info.json"
    file_path_instrument_info = fold_path_root + "instrument_info.json"
    fold_path_export = fold_path_root + "export/"

    def get_symbol_tm_map(self, exchange: Exchange, product: str, start_time: datetime, end_time: datetime):
        output = {}
        month_map = self.split_month(exchange, start_time, end_time)
        for k, v in month_map.items():
            output[self.get_instrument_id(exchange, product, k)] = [k, v]
        return output;

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

    def add_parameters(self, vt_symbol: str, symbol_flag: str, start_date, end_date, interval="tick", capital=1_000_000):
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
                capital=capital,
                mode=BacktestingMode.TICK
            )
        else:
            print("symbol %s hasn't be maintained in config file" % vt_symbol)

    def run_batch_test(self, strategy_setting, portfolio):
        """
        进行回测
        """
        result_df = DataFrame()
        df_portfolio = None
        for strategy_name, strategy_config in strategy_setting.items():
            eval(strategy_config["class_name"]),
            self.engine = BacktestingEngine()
            start_date = datetime.strptime(strategy_config["start_dt"], '%Y-%m-%d')
            end_date = datetime.strptime(strategy_config["end_dt"], '%Y-%m-%d') + timedelta(days=1)
            exchange_produce_list = strategy_config["products"]
            for exchange_produce in exchange_produce_list:
                exchange = exchange_produce["exchange"]
                produce = exchange_produce["product"]
                symbol_flag = produce + "." + exchange
                symbol_tm_map = self.get_symbol_tm_map(exchange, produce, start_date, end_date)

                for symbol, tm_arr in symbol_tm_map.items():
                    print(symbol + " " + tm_arr[0].strftime('%Y%m%d') + " " + tm_arr[1].strftime('%Y%m%d'))
                    self.add_parameters(symbol + "." + exchange, symbol_flag, tm_arr[0], tm_arr[1])
                    if type(strategy_config["setting"]) is str:
                        print(strategy_config["setting"])
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
                    if portfolio is True:
                        if df_portfolio is None:
                            df_portfolio = df
                        else:
                            df_portfolio = df_portfolio + df
                    result_dict = self.engine.calculate_statistics(df, False)
                    result_dict["class_name"] = strategy_config["class_name"]
                    result_dict["setting"] = strategy_config["setting"]
                    result_dict["vt_symbol"] = symbol
                    result_df = result_df.append(result_dict, ignore_index=True)

        if portfolio is True:
            self.engine.calculate_statistics(df_portfolio)
            self.engine.show_chart(df_portfolio)
        return result_df

    def run_batch_test_json(self, portfolio=True):
        """
        从ctaStrategy.json去读交易策略和参数，进行回测
        """
        with open(MainInstrumentSwitch.file_path_strategy_info, mode="r", encoding="UTF-8") as f:
            strategy_setting = json.load(f)
        result_df = self.run_batch_test(strategy_setting, portfolio)
        self.result_excel(result_df, self.export_path + "CTABatch" + str(date.today()) + "v0.xlsx")

        trade_pairs = self.engine.generate_trade_pairs()
        if len(trade_pairs) != 0:
            trade_pairs_df = pd.DataFrame(trade_pairs, columns=[
                "open_dt", "open_price", "close_dt", "close_price",
                "direction", "volume", "profit_loss", "profit_round",
                "trade_memo_open", "trade_memo_close", "gateway_name"])
            trade_pairs_df["open_dt"] = trade_pairs_df["open_dt"].dt.tz_localize(None)
            trade_pairs_df["close_dt"] = trade_pairs_df["close_dt"].dt.tz_localize(None)
            self.result_excel(trade_pairs_df, self.export_path + "CTABatch" + str(date.today()) + "v1.xlsx")

        return strategy_setting

    def run_batch_test_excecl(self, path="ctaStrategy.xls", start_date=datetime(2019, 7, 1),
                              end_date=datetime(2020, 1, 1), export_path=None, portfolio=False):
        """
        从ctaStrategy.excel去读交易策略和参数，进行回测
        """
        df = pd.read_excel(path)
        strategy_setting = df.to_dict(orient='index')
        result_df = self.run_batch_test(strategy_setting, start_date, end_date, portfolio)
        self.result_excel(result_df, export_path + "CTABatch" + str(date.today()) + "v0.xlsx")

        trade_pairs = self.engine.generate_trade_pairs()
        self.result_excel(trade_pairs, export_path + "CTABatch" + str(date.today()) + "v1.xlsx")

        return strategy_setting

    def result_excel(self, result, export):
        """
        输出交易结果到excel
        """
        if export is not None:
            export_path = export
        else:
            export_path = self.export_path + "CTABatch" + str(date.today()) + "v0.xlsx"

        try:
            result.to_excel(export_path, index=False)
            print("CTA Batch result is export to %s" % export_path)
        except:
            print(traceback.format_exc())

        return None


if __name__ == '__main__':
    print(os.getcwd())
    bts = MainInstrumentSwitch()

    bts.run_batch_test_json()
    print()
