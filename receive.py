import math
import re
import sys
import threading
import serial
import pygame

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

WINDOW_SIZE = 800
FPS = 60

roll_deg = 0.0
pitch_deg = 0.0
pitch_deg = 0.0
yaw_deg = 0.0
altitude = 0
serial_connected = False
good_packets = 0


def serial_reader():
    global roll_deg, pitch_deg, altitude, serial_connected

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        serial_connected = True
        print(f"Connected to {SERIAL_PORT} @ {BAUD_RATE}")
    except Exception as e:
        print(f"Could not open serial port: {e}")
        return

    pattern = re.compile(r"roll:([-0-9.]+)\s+pitch:([-0-9.]+)\s+yaw:([-0-9.]+)\s+altitude:([-0-9.]+)")
    # pattern = re.compile(r"roll:([-0-9.]+)\s+pitch:([-0-9.]+)")

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            print("RAW:", line)

            match = pattern.search(line)
            if match:
                roll_deg = float(match.group(1)) * -1
                pitch_deg = float(match.group(2))
                yaw_deg = float(match.group(3))
                altitude = float(match.group(4))

        except Exception as e:
            print("Parse error:", e)


def draw_text(surface, text, size, color, center):
    font = pygame.font.SysFont("arial", size, bold=False)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


def draw_attitude_indicator(surface, center_x, center_y, radius, roll, pitch, yaw, altitude):
    sky_color = (70, 110, 180)
    ground_color = (110, 80, 45)
    white = (240, 240, 240)
    yellow = (245, 225, 120)
    black = (20, 20, 20)

    width = surface.get_width()
    height = surface.get_height()

    pitch_scale = 6.0  # pixels per degree

    # Large surface so rotation doesn't leave gaps
    horizon_size = max(width, height) * 3
    horizon = pygame.Surface((horizon_size, horizon_size), pygame.SRCALPHA)

    hx = horizon_size // 2
    hy = horizon_size // 2

    # Positive pitch should move horizon downward on screen
    pitch_offset = pitch * pitch_scale

    horizon.fill((0, 0, 0, 0))

    # Sky
    pygame.draw.rect(
        horizon,
        sky_color,
        pygame.Rect(0, 0, horizon_size, hy + int(pitch_offset))
    )

    # Ground
    pygame.draw.rect(
        horizon,
        ground_color,
        pygame.Rect(0, hy + int(pitch_offset), horizon_size, horizon_size - (hy + int(pitch_offset)))
    )

    # Horizon line
    pygame.draw.line(
        horizon,
        white,
        (0, hy + int(pitch_offset)),
        (horizon_size, hy + int(pitch_offset)),
        4
    )

    # Pitch ladder
    font = pygame.font.SysFont("arial", 28)
    for ang in range(-45, 85, 5):
        if ang == 0:
            continue

        y = hy + int(pitch_offset - ang * pitch_scale)

        if ang % 10 == 0:
            half_len = 90
            pygame.draw.line(horizon, white, (hx - half_len, y), (hx + half_len, y), 3)

            label = str(abs(ang))
            left_img = font.render(label, True, white)
            right_img = font.render(label, True, white)

            horizon.blit(left_img, (hx - half_len - 55, y - 14))
            horizon.blit(right_img, (hx + half_len + 20, y - 14))
        else:
            half_len = 45
            pygame.draw.line(horizon, white, (hx - half_len, y), (hx + half_len, y), 2)

    # Rotate whole horizon by roll
    rotated = pygame.transform.rotozoom(horizon, roll, 1.0)
    rotated_rect = rotated.get_rect(center=(center_x, center_y))

    # Fill whole screen with rotated horizon
    surface.blit(rotated, rotated_rect)

    # Fixed aircraft symbol in center
    pygame.draw.line(surface, yellow, (center_x - 120, center_y), (center_x - 25, center_y), 6)
    pygame.draw.line(surface, yellow, (center_x + 25, center_y), (center_x + 120, center_y), 6)
    pygame.draw.line(surface, yellow, (center_x - 25, center_y), (center_x, center_y + 14), 5)
    pygame.draw.line(surface, yellow, (center_x + 25, center_y), (center_x, center_y + 14), 5)

    pygame.draw.circle(surface, black, (center_x, center_y), 9)
    pygame.draw.circle(surface, yellow, (center_x, center_y), 9, 2)

    # Text
    draw_text(surface, f"Roll: {roll:6.1f}°", 28, white, (130, 35))
    draw_text(surface, f"Pitch: {pitch:6.1f}°", 28, white, (140, 70))
    draw_text(surface, f"Yaw: {yaw:6.1f}°", 28, white, (130, 105))
    draw_text(surface, f"Alt: {altitude:7.1f} m", 28, white, (155, 140))


def main():
    global roll_deg, pitch_deg, yaw_deg, altitude, serial_connected, good_packets

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Artificial Horizon")
    clock = pygame.time.Clock()

    thread = threading.Thread(target=serial_reader, daemon=True)
    thread.start()

    smooth_roll = 0.0
    smooth_pitch = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        smooth_roll = smooth_roll * 0.7 + roll_deg * 0.3
        smooth_pitch = smooth_pitch * 0.7 + pitch_deg * 0.3

        screen.fill((18, 18, 18))

        draw_attitude_indicator(
            screen,
            WINDOW_SIZE // 2,
            WINDOW_SIZE // 2 - 30,
            260,
            smooth_roll,
            smooth_pitch,
            yaw_deg,
            altitude
        )

        if not serial_connected:
            draw_text(screen, "Waiting for serial...", 24, (255, 180, 180), (WINDOW_SIZE // 2, 40))
        else:
            draw_text(screen, f"Packets: {good_packets}", 22, (200, 255, 200), (WINDOW_SIZE // 2, 35))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
