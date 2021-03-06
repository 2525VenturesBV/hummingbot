#!/usr/bin/env python

import asyncio
import logging
from typing import (
    List,
    Optional
)
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource
from hummingbot.logger import HummingbotLogger
from hummingbot.core.data_type.user_stream_tracker import UserStreamTracker
from hummingbot.core.utils.async_utils import (
    safe_ensure_future,
    safe_gather,
)
from hummingbot.connector.exchange.litebit_pro.litebit_pro_api_user_stream_data_source import LitebitProAPIUserStreamDataSource
from hummingbot.connector.exchange.litebit_pro.litebit_pro_auth import LitebitProAuth


class LitebitProUserStreamTracker(UserStreamTracker):
    _bust_logger: Optional[HummingbotLogger] = None

    @classmethod
    def logger(cls) -> HummingbotLogger:
        if cls._bust_logger is None:
            cls._bust_logger = logging.getLogger(__name__)
        return cls._bust_logger

    def __init__(self,
                 litebit_pro_auth: Optional[LitebitProAuth] = None,
                 trading_pairs: Optional[List[str]] = []):
        super().__init__()
        self._litebit_pro_auth: LitebitProAuth = litebit_pro_auth
        self._ev_loop: asyncio.events.AbstractEventLoop = asyncio.get_event_loop()
        self._trading_pairs = trading_pairs
        self._data_source: Optional[UserStreamTrackerDataSource] = None
        self._user_stream_tracking_task: Optional[asyncio.Task] = None

    @property
    def data_source(self) -> UserStreamTrackerDataSource:
        if not self._data_source:
            self._data_source = LitebitProAPIUserStreamDataSource(
                litebit_pro_auth=self._litebit_pro_auth, trading_pairs=self._trading_pairs)
        return self._data_source

    @property
    def exchange_name(self) -> str:
        return "litebit_pro"

    async def start(self):
        self._user_stream_tracking_task = safe_ensure_future(
            self.data_source.listen_for_user_stream(self._ev_loop, self._user_stream)
        )
        await safe_gather(self._user_stream_tracking_task)
