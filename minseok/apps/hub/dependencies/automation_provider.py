from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.mail_ingest_use_case import MailIngestUseCase
from hub.app.ports.input.news_ingest_use_case import NewsIngestUseCase
from hub.app.ports.input.news_label_ingest_use_case import NewsLabelIngestUseCase
from hub.app.ports.input.price_bar_ingest_use_case import PriceBarIngestUseCase
from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.app.ports.output.mail_storage_port import MailStoragePort
from hub.app.ports.output.news_storage_port import NewsStoragePort
from hub.app.ports.output.news_label_storage_port import NewsLabelStoragePort
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort
from hub.app.use_cases.mail_ingest_interactor import MailIngestInteractor
from hub.app.use_cases.news_ingest_interactor import NewsIngestInteractor
from hub.app.use_cases.news_label_ingest_interactor import NewsLabelIngestInteractor
from hub.app.use_cases.price_bar_ingest_interactor import PriceBarIngestInteractor
from hub.app.use_cases.signal_scan_interactor import SignalScanInteractor
from hub.dependencies.stock_analysis_provider import get_stock_analysis_port


def get_news_storage_port() -> NewsStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_news_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_news_ingest_use_case(
    storage: NewsStoragePort = Depends(get_news_storage_port),
) -> NewsIngestUseCase:
    return NewsIngestInteractor(storage=storage)


def get_news_label_storage_port() -> NewsLabelStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_news_label_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_news_label_ingest_use_case(
    storage: NewsLabelStoragePort = Depends(get_news_label_storage_port),
) -> NewsLabelIngestUseCase:
    return NewsLabelIngestInteractor(storage=storage)


def get_price_bar_storage_port() -> PriceBarStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_price_bar_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_price_bar_ingest_use_case(
    storage: PriceBarStoragePort = Depends(get_price_bar_storage_port),
) -> PriceBarIngestUseCase:
    return PriceBarIngestInteractor(storage=storage)


def get_signal_scan_use_case(
    stocks: StockAnalysisPort = Depends(get_stock_analysis_port),
) -> SignalScanUseCase:
    return SignalScanInteractor(stocks=stocks)


def get_mail_storage_port() -> MailStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(mail) 구현을 주입한다."""
    raise NotImplementedError(
        "get_mail_storage_port는 main.py의 dependency_overrides로 mail 구현을 주입해야 합니다."
    )


def get_mail_ingest_use_case(
    storage: MailStoragePort = Depends(get_mail_storage_port),
) -> MailIngestUseCase:
    return MailIngestInteractor(storage=storage)
