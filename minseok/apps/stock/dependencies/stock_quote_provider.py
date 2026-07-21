from stock.adapter.outbound.yfinance_market_data_adapter import YFinanceMarketDataAdapter
from stock.app.ports.input.stock_quote_use_case import StockQuoteUseCase
from stock.app.use_cases.stock_quote_interactor import StockQuoteInteractor


def get_stock_quote_use_case() -> StockQuoteUseCase:
    return StockQuoteInteractor(market_data=YFinanceMarketDataAdapter())
