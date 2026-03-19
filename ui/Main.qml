import QtQuick
import QtQuick.Window
import ui

Window {
    visible: true
    width: 1000
    height: 700
    color: "#111111"
    title: "ESP32 Horizon"

    HorizonIndicator {
        anchors.centerIn: parent
        width: 800
        height: 800

        roll: telemetry.roll
        pitch: telemetry.pitch
        altitude: telemetry.altitude
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 20
        width: 220
        height: 150
        radius: 10
        color: "#1a1a1a"
        border.color: "#555"

        Column {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8

            Text {
                text: telemetry.connected ? "Serial: Connected" : "Serial: Disconnected"
                color: telemetry.connected ? "lightgreen" : "#ff8080"
                font.pixelSize: 18
            }

            Text {
                text: "Roll: " + telemetry.roll.toFixed(2) + "°"
                color: "white"
                font.pixelSize: 18
            }

            Text {
                text: "Pitch: " + telemetry.pitch.toFixed(2) + "°"
                color: "white"
                font.pixelSize: 18
            }

            Text {
                text: "Altitude: " + telemetry.altitude.toFixed(2) + " m"
                color: "white"
                font.pixelSize: 18
            }
        }
    }
}
