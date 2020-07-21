from PyQt5.QtCore import QObject, pyqtSignal

AWAITING_CONNECTION = "Awaiting connection"
AWAITING_AUTHENTICATION = "Awaiting authentication"
CONNECTED = "Connected"


class SerialConnectionState(QObject):

    state_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._state = AWAITING_CONNECTION

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, status: str):
        self._state = status
        self.state_changed.emit(status)
