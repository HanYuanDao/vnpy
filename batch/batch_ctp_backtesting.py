import json
import os
import traceback
from datetime import datetime, date, timedelta
import pandas as pd
from pandas import DataFrame
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_ctastrategy.strategies.the_boll_tactic_of_nd import TheBollTacticOfND
from vnpy_ctastrategy.base import BacktestingMode


class BatchCTABackTest:
    """
    提供批量CTA策略回测，输出结果到excel或pdf，和CTA策略批量优化，输出结果到excel或pdf，
    """

    def __init__(self, vt_symbol_config="vtSymbol.json", export_path=".//"):
        """
        加载配置路径
        """
        config = open(vt_symbol_config)
        self.setting = json.load(config)
        self.export_path = export_path
        self.engine = None

    def add_parameters(self, vt_symbol: str, start_date, end_date, interval="tick", capital=1_000_000):
        """
        从vtSymbol.json文档读取品种的交易属性，比如费率，交易每跳，比率，滑点
        """
        if vt_symbol in self.setting:
            self.engine.set_parameters(
                vt_symbol=vt_symbol,
                interval=interval,
                start=start_date,
                end=end_date,
                rate_money=self.setting[vt_symbol]["rate_money"],
                rate_volume=self.setting[vt_symbol]["rate_volume"],
                slippage=self.setting[vt_symbol]["slippage"],
                size=self.setting[vt_symbol]["size"],
                pricetick=self.setting[vt_symbol]["pricetick"],
                capital=capital,
                mode=BacktestingMode.BAR
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
            vt_symbol = strategy_config["vt_symbol"]
            self.engine = BacktestingEngine()
            start_date = datetime.strptime(strategy_config["start_dt"], '%Y-%m-%d')
            end_date = datetime.strptime(strategy_config["end_dt"], '%Y-%m-%d') + timedelta(days=1)
            self.add_parameters(vt_symbol, start_date, end_date)
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
            result_dict["vt_symbol"] = strategy_config["vt_symbol"]
            result_df = result_df.append(result_dict, ignore_index=True)

        if portfolio is True:
            # dfportfolio = dfportfolio.dropna()
            self.engine.calculate_statistics(df_portfolio)
            self.engine.show_chart(df_portfolio)
        return result_df

    def run_batch_test_json(self, jsonpath="ctaStrategy.json", portfolio=True):
        """
        从ctaStrategy.json去读交易策略和参数，进行回测
        """
        with open(jsonpath, mode="r", encoding="UTF-8") as f:
            strategy_setting = json.load(f)
        result_df = self.run_batch_test(strategy_setting, portfolio)
        self.result_excel(result_df, self.export_path + "CTABatch" + str(date.today()) + "v0.xlsx")

        trade_pairs = self.engine.generate_trade_pairs()
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

    bts = BatchCTABackTest()
    bts.run_batch_test_json()
