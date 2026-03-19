import QtQuick

Item {
    id: root
    width: 500
    height: 500

    // Inputs from Python
    property real roll: 0        // degrees
    property real pitch: 0       // degrees
    property real altitude: 0    // meters

    // Tuning
    property real pitchScale: 4.0    // pixels per degree
    property color skyColor: "#4da6ff"
    property color groundColor: "#8b5a2b"
    property color lineColor: "white"
    property color hudColor: "white"

    Rectangle {
        anchors.fill: parent
        color: "#101010"
        radius: 12
    }

    Item {
        id: viewport
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.82
        height: width
        clip: true

        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: "#202020"
            border.color: "#707070"
            border.width: 2
        }

        Item {
            id: world
            anchors.centerIn: parent
            width: viewport.width * 2.4
            height: viewport.height * 2.4
            rotation: -root.roll

            Item {
                id: pitchContainer
                width: parent.width
                height: parent.height
                x: (parent.width - width) / 2
                y: (parent.height - height) / 2 + (-root.pitch * root.pitchScale)

                Rectangle {
                    x: 0
                    y: 0
                    width: parent.width
                    height: parent.height / 2
                    color: root.skyColor
                }

                Rectangle {
                    x: 0
                    y: parent.height / 2
                    width: parent.width
                    height: parent.height / 2
                    color: root.groundColor
                }

                Rectangle {
                    x: 0
                    y: parent.height / 2 - 1
                    width: parent.width
                    height: 2
                    color: "white"
                    opacity: 0.9
                }

                Repeater {
                    model: 18

                    delegate: Item {
                        property int stepDeg: (index + 1) * 5
                        property real yOffset: stepDeg * root.pitchScale

                        anchors.fill: parent

                        function ladderWidth(deg) {
                            return deg % 10 === 0 ? parent.width * 0.18 : parent.width * 0.10
                        }

                        function labelVisible(deg) {
                            return deg % 10 === 0
                        }

                        Rectangle {
                            width: ladderWidth(stepDeg)
                            height: 2
                            color: root.lineColor
                            anchors.horizontalCenter: parent.horizontalCenter
                            y: parent.height / 2 - yOffset
                        }

                        Rectangle {
                            width: ladderWidth(stepDeg)
                            height: 2
                            color: root.lineColor
                            anchors.horizontalCenter: parent.horizontalCenter
                            y: parent.height / 2 + yOffset
                        }

                        Text {
                            visible: labelVisible(stepDeg)
                            text: stepDeg
                            color: root.lineColor
                            font.pixelSize: 14
                            anchors.verticalCenter: undefined
                            y: parent.height / 2 - yOffset - height / 2
                            x: parent.width / 2 - ladderWidth(stepDeg) / 2 - width - 8
                        }

                        Text {
                            visible: labelVisible(stepDeg)
                            text: stepDeg
                            color: root.lineColor
                            font.pixelSize: 14
                            y: parent.height / 2 - yOffset - height / 2
                            x: parent.width / 2 + ladderWidth(stepDeg) / 2 + 8
                        }

                        Text {
                            visible: labelVisible(stepDeg)
                            text: stepDeg
                            color: root.lineColor
                            font.pixelSize: 14
                            y: parent.height / 2 + yOffset - height / 2
                            x: parent.width / 2 - ladderWidth(stepDeg) / 2 - width - 8
                        }

                        Text {
                            visible: labelVisible(stepDeg)
                            text: stepDeg
                            color: root.lineColor
                            font.pixelSize: 14
                            y: parent.height / 2 + yOffset - height / 2
                            x: parent.width / 2 + ladderWidth(stepDeg) / 2 + 8
                        }
                    }
                }
            }
        }

        Canvas {
            id: bezelMarks
            anchors.fill: parent

            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()

                const w = width
                const h = height
                const cx = w / 2
                const cy = h / 2
                const r = Math.min(w, h) / 2 - 8

                ctx.strokeStyle = "white"
                ctx.lineWidth = 3

                function drawTick(angleDeg, len, lw) {
                    const a = (angleDeg - 90) * Math.PI / 180.0
                    const x1 = cx + Math.cos(a) * (r - len)
                    const y1 = cy + Math.sin(a) * (r - len)
                    const x2 = cx + Math.cos(a) * r
                    const y2 = cy + Math.sin(a) * r
                    ctx.lineWidth = lw
                    ctx.beginPath()
                    ctx.moveTo(x1, y1)
                    ctx.lineTo(x2, y2)
                    ctx.stroke()
                }

                const major = [-60, -45, -30, -20, -10, 10, 20, 30, 45, 60]
                for (let i = 0; i < major.length; i++) {
                    drawTick(major[i], 16, 3)
                }
                drawTick(0, 24, 4)
            }
        }

        Item {
            anchors.fill: parent

            Rectangle {
                width: parent.width * 0.16
                height: 4
                color: root.hudColor
                anchors.verticalCenter: parent.verticalCenter
                x: parent.width * 0.24
                radius: 2
            }

            Rectangle {
                width: parent.width * 0.16
                height: 4
                color: root.hudColor
                anchors.verticalCenter: parent.verticalCenter
                x: parent.width * 0.60
                radius: 2
            }

            Rectangle {
                width: parent.width * 0.08
                height: 4
                color: root.hudColor
                anchors.centerIn: parent
                radius: 2
            }

            Rectangle {
                width: 4
                height: parent.height * 0.05
                color: root.hudColor
                anchors.horizontalCenter: parent.horizontalCenter
                y: parent.height * 0.48
                radius: 2
            }
        }
    }

    Rectangle {
        id: altitudeBox
        width: 110
        height: 56
        radius: 8
        color: "#1a1a1a"
        border.color: "white"
        border.width: 2
        anchors.right: parent.right
        anchors.rightMargin: 18
        anchors.verticalCenter: parent.verticalCenter

        Column {
            anchors.centerIn: parent
            spacing: 2

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "ALT"
                color: "#bbbbbb"
                font.pixelSize: 14
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: Number(root.altitude).toFixed(1) + " m"
                color: "white"
                font.pixelSize: 22
                font.bold: true
            }
        }
    }
}