from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.gateway.ctp import CtpGateway

from vnpy.app.algo_trading import AlgoTradingApp
from vnpy.app.chart_wizard import ChartWizardApp
from vnpy.app.cta_backtester import CtaBacktesterApp
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.data_manager import DataManagerApp
from vnpy.app.data_recorder import DataRecorderApp
from vnpy.app.excel_rtd import ExcelRtdApp
# from vnpy.app.market_radar import MarketRadarApp
from vnpy.app.option_master import OptionMasterApp
from vnpy.app.paper_account import PaperAccountApp
from vnpy.app.portfolio_manager import PortfolioManagerApp
from vnpy.app.portfolio_strategy import PortfolioStrategyApp
from vnpy.app.risk_manager import RiskManagerApp
# from vnpy.app.rpc_service import RpcServiceApp
from vnpy.app.script_trader import ScriptTraderApp
from vnpy.app.spread_trading import SpreadTradingApp
from vnpy.app.web_trader import WebTraderApp


def main():
    """Start VN Trader"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(CtpGateway)

    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(ChartWizardApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(ExcelRtdApp)
    # main_engine.add_app(MarketRadarApp)
    main_engine.add_app(OptionMasterApp)
    main_engine.add_app(PaperAccountApp)
    main_engine.add_app(PortfolioManagerApp)
    main_engine.add_app(PortfolioStrategyApp)
    main_engine.add_app(RiskManagerApp)
    # main_engine.add_app(RpcServiceApp)
    main_engine.add_app(ScriptTraderApp)
    main_engine.add_app(SpreadTradingApp)
    main_engine.add_app(WebTraderApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()

