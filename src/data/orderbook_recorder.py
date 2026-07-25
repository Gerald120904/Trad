"""Future interface for recording reconstructable Binance order books.

The REST depth endpoint is only a current snapshot. Implementation is
deliberately deferred until the project explicitly starts collecting its own
snapshot plus incremental WebSocket history; see docs/DATA_CONTRACTS.md.
"""

from typing import Protocol


class OrderBookRecorder(Protocol):
    def start(self, symbol: str) -> None: ...

    def stop(self) -> None: ...
