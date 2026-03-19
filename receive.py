import re
import sys
import threading
import serial

from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


SERIAL_PORT = "/dev/ttyUSB1"
BAUD_RATE = 115200


class TelemetryBridge(QObject):
    rollChanged = Signal()
    pitchChanged = Signal()
    yawChanged = Signal()
    altitudeChanged = Signal()
    connectedChanged = Signal()

    dataReceived = Signal(float, float, float, float)
    connectionStateChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._altitude = 0.0
        self._connected = False

        self.dataReceived.connect(self._update_data)
        self.connectionStateChanged.connect(self._update_connection_state)

    def get_roll(self):
        return self._roll

    def get_pitch(self):
        return self._pitch

    def get_yaw(self):
        return self._yaw

    def get_altitude(self):
        return self._altitude

    def get_connected(self):
        return self._connected

    @Slot(float, float, float, float)
    def _update_data(self, roll, pitch, yaw, altitude):
        if self._roll != roll:
            self._roll = roll
            self.rollChanged.emit()

        if self._pitch != pitch:
            self._pitch = pitch
            self.pitchChanged.emit()

        if self._yaw != yaw:
            self._yaw = yaw
            self.yawChanged.emit()

        if self._altitude != altitude:
            self._altitude = altitude
            self.altitudeChanged.emit()

    @Slot(bool)
    def _update_connection_state(self, connected):
        if self._connected != connected:
            self._connected = connected
            self.connectedChanged.emit()

    roll = Property(float, get_roll, notify=rollChanged)
    pitch = Property(float, get_pitch, notify=pitchChanged)
    yaw = Property(float, get_yaw, notify=yawChanged)
    altitude = Property(float, get_altitude, notify=altitudeChanged)
    connected = Property(bool, get_connected, notify=connectedChanged)


def serial_reader(telemetry: TelemetryBridge):
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        telemetry.connectionStateChanged.emit(True)
        print(f"Connected to {SERIAL_PORT} @ {BAUD_RATE}")
    except Exception as e:
        telemetry.connectionStateChanged.emit(False)
        print(f"Could not open serial port: {e}")
        return

    pattern = re.compile(
        r"roll:([-0-9.]+)\s+pitch:([-0-9.]+)\s+yaw:([-0-9.]+)\s+altitude:([-0-9.]+)"
    )

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            print("RAW:", line)

            match = pattern.search(line)
            if match:
                roll = float(match.group(1)) * -1.0
                pitch = float(match.group(2))
                yaw = float(match.group(3))
                altitude = float(match.group(4))

                telemetry.dataReceived.emit(roll, pitch, yaw, altitude)

        except Exception as e:
            print("Parse error:", e)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.addImportPath(str(Path(__file__).parent))

    telemetry = TelemetryBridge()
    engine.rootContext().setContextProperty("telemetry", telemetry)

    engine.loadFromModule("ui", "Main")
    if not engine.rootObjects():
        sys.exit(-1)

    thread = threading.Thread(target=serial_reader, args=(telemetry,), daemon=True)
    thread.start()

    sys.exit(app.exec())
