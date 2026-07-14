from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort
from hub.app.use_cases.signal_scan_interactor import SignalScanInteractor
from hub.dependencies.stock_analysis_provider import get_stock_analysis_port


def get_signal_scan_use_case(
    stocks: StockAnalysisPort = Depends(get_stock_analysis_port),
) -> SignalScanUseCase:
    return SignalScanInteractor(stocks=stocks)
