import pygame
import math
import random
import requests
import time
import os
from collections import deque

if not os.path.exists("TELEMETRY_DATA"):
    os.makedirs("TELEMETRY_DATA")

pygame.init()
pygame.mixer.init()
terminal_hum = pygame.mixer.Sound("terminal_hum.flac")
writing_hum = pygame.mixer.Sound("writing_hum.flac")
click_effect = pygame.mixer.Sound("click.wav")
writing_hum.set_volume(0.03)
click_effect.set_volume(0.05)
terminal_hum.set_volume(0.08)
writing_hum.play(-1)
terminal_hum.play(-1)

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NASA Mission Control")
API_KEY = "CfOeI4tLdXfiXwIUIRud27MlwYtJYbNWWXuf1H1x"
clock = pygame.time.Clock()
angle = 0
points = []
asteroidsPoints = []
selected_Asteroid = None
orbitline_Toggle = False
tracked = False
time_speed = 1
sweep_angle = 0
earth_x = 370
earth_y = 310
url = "https://api.nasa.gov/neo/rest/v1/feed"
start_time = time.time()
params = {"start_date": "2026-01-01", "end_date": "2026-01-08", "api_key": API_KEY}
reticle_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
reticle_angleRotation = 1
boot_percent = 0
last_update_time = 0
update_delay = 2000
quickInfotoggle = False

last_button_press_time = 0
debounce_cooldown = 10

radar_Integ = random.randint(85, 98)
optical_Integ = random.randint(85, 98)
comms_Integ = random.randint(85, 98)

response = requests.get(url, params=params)
data = response.json()
grey = (200, 200, 200)
darkgrey = (100, 100, 100)
asteroids = data["near_earth_objects"]
total_asteroids = sum(len(asteroids[day]) for day in asteroids)

SCALE_FACTOR = 100
EARTH_DIAMETER_KM = 12742

font = pygame.font.SysFont("OCR A Extended", 20)
LogFont = pygame.font.SysFont("OCR A Extended", 15)
NEOfont = pygame.font.SysFont("OCR A Extended", 10)

Earth_Text = font.render("EARTH OBSERVATION CENTER", True, (0, 150, 200))
Tracking_text = font.render(f"CURRENTLY TRACKING {total_asteroids} NEOS", True, (0, 150, 200))

btn_slow = pygame.Rect(760, 630, 140, 40)
btn_fast = pygame.Rect(920, 630, 140, 40)
btn_pause = pygame.Rect(760, 690, 140, 40)
btn_play = pygame.Rect(920, 690, 140, 40)
btn_orbit = pygame.Rect(1080, 630, 160, 40)
btn_export = pygame.Rect(790, 400, 220, 50)
btn_info = pygame.Rect(1080, 690, 160, 40)


pygame.draw.circle(reticle_surf, (255, 50, 50), (30, 30), 12, 1)

pygame.draw.line(reticle_surf, (255, 50, 50), (30, 2), (30, 8), 2)
pygame.draw.line(reticle_surf, (255, 50, 50), (30, 58), (30, 52), 2)
pygame.draw.line(reticle_surf, (255, 50, 50), (2, 30), (8, 30), 2)
pygame.draw.line(reticle_surf, (255, 50, 50), (58, 30), (52, 30), 2)

pygame.draw.rect(screen, (255, 50, 50), (30, 30, 2, 2))

for _ in range(1500):
    theta = random.uniform(0, math.pi)
    phi = random.uniform(0, math.pi * 2)

    x = math.sin(theta) * math.cos(phi)
    y = math.cos(theta)
    z = math.sin(theta) * math.sin(phi)
    h = abs(x + y + z + math.sin(phi * 3))
    points.append((x, y, z, h))

for day in asteroids:
    for asteroid in asteroids[day]:
        name = asteroid["name"]
        size = asteroid["estimated_diameter"]
        approach = asteroid["close_approach_data"][0]
        velocity = float(approach["relative_velocity"]["kilometers_per_second"])
        distance = float(approach["miss_distance"]["astronomical"])

        dot_name = name
        orbit_tilt = random.uniform(-4, 8)
        asteroid_d = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"]

        ratio = math.log(max(0.001, asteroid_d))
        dec_dot_size = max(1, ratio * SCALE_FACTOR)
        dot_size = int(dec_dot_size)
        if dot_size > 10:
            dot_size = 8
        if dot_size < 3:
            dot_size = 3

        normalized_Velocity = (velocity - 5) / 30
        normalized_Distance = (distance - 0.05) / 0.5

        orbit_angle = random.uniform(0, math.pi * 2)
        z = random.uniform(-1, 1)
        orbit_radius = 140 + normalized_Distance * 180
        asteroidsPoints.append(
            (dot_name, dot_size, approach, orbit_angle, orbit_radius, normalized_Velocity, orbit_tilt, z, velocity))

console_logs = deque([
    "[SYSTEM] SYSTEM BOOT SUCCESSFUL...",
    "[INFO] CONNECTED TO NASA DATA REPOSITORY...",
    "[SYSTEM] INITIALIZING RADAR MATRIX..."
], maxlen=10)

generic_pool = [
    "[SYSTEM] MONITOR STATUS // ALL SUBSYSTEMS NOMINAL",
    "[INFO] ESTABLISHING SECURE CONNECTION TO REMOTE NODE...",
    "[DATA] INCOMING DATA STREAM VERIFIED // INTEGRITY 100%",
    "[SYSTEM] INITIALIZING BUFFER CLEAR SEQUENCE...",
    "[ONLINE] SYNCHRONIZING CORE HUD HUD MATRIX...",
    "[INFO] PROCESSING PACKET S-402 // RETRY ATTEMPT 01",
    "[WARN] SENSOR DRIFT DETECTED // CALIBRATING ECLIPTIC PLANE...",
    "[DATA] COMPUTE ENGINE: RESOLVING PARAMETRIC COORD SPACE",
    "[SYSTEM] BACKGROUND DIAGNOSTIC CYCLES RUNNING...",
    "[ONLINE] HIGH-FREQUENCY RECEIVER STATUS: OPEN",
    "[INFO] APOGEE DISTANCE EXTENTS BOUNDS RE-CALCULATED",
    "[TRACK] LIVE SENSOR PING ACQUIRED // UPDATING VECTOR INDEX",
    "[DATA] TEMPORAL DRIFT CORRECTION APPLIED SUCCESSFULLY",
    "[SYSTEM] MEMORY ALLOCATION STABLE // REFRESH STATE OK",
    "[PING] TELEMETRY DISPLACEMENT VALUE CALCULATED",
    "[INFO] SCHEDULER DISPATCHING ROUTINE DATA REFRESH",
    "[DATA] PARSING LOCAL ENVELOPE STRUCTS... COMPLETE",
    "[WARN] ATTENUATION DETECTED IN TRANSIT STREAM // RESYNCING",
    "[SYSTEM] SECURITY PROTOCOLS HANDSHAKE AUTHORIZED",
    "[ONLINE] RADAR FIELD REFRESH ACTIVE // READY FOR CYCLE",
]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                time_speed += 1
            elif event.key == pygame.K_a:
                time_speed -= 1
                if time_speed < 1:
                    time_speed = 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = pygame.mouse.get_pos()

            current_time = pygame.time.get_ticks()

            if current_time - int(last_button_press_time) > debounce_cooldown:
                click_effect.play()
                last_button_press_time = current_time
            
                
            
            if btn_slow.collidepoint(mouse_pos):
                time_speed = max(1, time_speed - 1)
                console_logs.append(f"[SYSTEM] TIME WARP REDUCED: {time_speed}X")
            elif btn_fast.collidepoint(mouse_pos):
                time_speed += 1
                console_logs.append(f"[SYSTEM] TIME WARP INCREASED: {time_speed}X")
            elif btn_orbit.collidepoint(mouse_pos):
                if orbitline_Toggle == False:
                    orbitline_Toggle = True
                    print(orbitline_Toggle)
                    console_logs.append(f"[TRACKING] ORBIT LINES ENABLED")
                else:
                    orbitline_Toggle = False
                    print(orbitline_Toggle)
                    console_logs.append(f"[TRACKING] ORBIT LINES DISABLED")
            elif btn_pause.collidepoint(mouse_pos):
                time_speed = 0
                console_logs.append(f"[SYSTEMS] SYSTEM PAUSED")
            elif btn_play.collidepoint(mouse_pos):
                time_speed = 1
                console_logs.append(f"[SYSTEMS] SYSTEM RESUMED")
            elif btn_info.collidepoint(mouse_pos):
                if quickInfotoggle == True:
                    quickInfotoggle = False
                    console_logs.append(f"[INFO] QUICK INFO DEACTIVATED")
                else:
                    quickInfotoggle = True
                    console_logs.append(f"[INFO] QUICK INFO ACTIVATED")
            elif btn_export.collidepoint(mouse_pos):
                if selected_Asteroid is not None:

                    safe_name = selected_Asteroid['name'].replace("(", "").replace(")", "").replace(" ", "_")
                    filename = f"TELEMETRY_DATA/{safe_name}_report.txt"

                    try:
                        with open(filename, "w") as file:
                            file.write("==================================================\n")
                            file.write("          NASA TARGET TELEMETRY REPORT            \n")
                            file.write("==================================================\n\n")
                            file.write(f"DESIGNATION:    {selected_Asteroid['name']}\n")
                            file.write(f"SECTOR SPEED:   {selected_Asteroid['speed'] * time_speed:.2f} KM/S\n")
                            file.write(f"ORBIT RADIUS:   {selected_Asteroid['radius']:.2f}\n")
                            file.write(f"ECLIPTIC TILT:  {selected_Asteroid['tilt']:.2f}\n")
                            file.write(f"EST. SIZE CAT:  {selected_Asteroid['size']}\n")
                            file.write(f"ORBITAL ANGLE:  {selected_Asteroid['angle']:.2f}\n")
                            file.write(f"Z-AXIS DEPTH:   {selected_Asteroid['depth']:.2f}\n")
                            file.write(f"THREAT LEVEL:   {selected_Asteroid['danger']}\n\n")
                            file.write("==================================================\n")
                            file.write(f"REPORT GENERATED AT SYSTEM UPTIME: {int(time.time() - start_time)}s\n")
                            file.write("STATUS: TELEMETRY EXPORTED SUCCESSFULLY.\n")

                        console_logs.append(f"[SUCCESS] DATA EXPORTED TO {safe_name}_report.txt")
                    except Exception as e:
                        console_logs.append(f"[ERROR] FAILED TO WRITE FILE: {str(e)}")
            else:
                hit_detected = False
                for i, (dot_name, dot_size, approach, orbit_angle, orbit_radius, normalized_Velocity, orbit_tilt,
                        z, velocity) in enumerate(asteroidsPoints):
                    check_x = earth_x + math.cos(orbit_angle) * orbit_radius
                    check_y = earth_y + math.sin(orbit_angle) * orbit_radius * orbit_tilt / 8
                    distance_to_mouse = math.hypot(mouse_x - check_x, mouse_y - check_y)

                    danger = "LOW"
                    if normalized_Velocity > 0.6:
                        danger = "HIGH"
                    elif normalized_Velocity > 0.47:
                        danger = "MEDIUM"

                    if distance_to_mouse < 12:

                        if selected_Asteroid is None or selected_Asteroid["name"] != dot_name:
                            console_logs.append(f"[TRACK] CURRENTLY TRACKING: {dot_name}, VELOCITY: {velocity:.2f} KM/S")
                            
                        selected_Asteroid = {
                            "name": dot_name,
                            "speed": velocity,
                            "radius": orbit_radius,
                            "tilt": orbit_tilt,
                            "size": dot_size,
                            "angle": orbit_angle,
                            "depth": z,
                            "danger": danger
                        }
                        hit_detected = True
                        break
                if not hit_detected:
                    selected_Asteroid = None


    

    screen.fill((5, 10, 20))
    asteroidsPoints.sort(key=lambda a: math.sin(a[3] + a[7]))

    if random.random() < 0.01:
        console_logs.append(random.choice(generic_pool))

    for i, (dot_name, dot_size, approach, orbit_angle, orbit_radius, normalized_Velocity, orbit_tilt, z, velocity) in enumerate(
            asteroidsPoints):
        x = earth_x + math.cos(orbit_angle) * orbit_radius
        y = earth_y + math.sin(orbit_angle) * orbit_radius * orbit_tilt / 8

        text_x = x+10
        nametext_y = y+10
        veloctext_y = y+20

        newangle = orbit_angle + (0.005 * normalized_Velocity * time_speed)
        asteroidsPoints[i] = (dot_name, dot_size, approach, newangle, orbit_radius, normalized_Velocity, orbit_tilt, z, velocity)

        neo_Text = NEOfont.render(f"{dot_name}", True, (255, 255, 255))
        velocneo_text = NEOfont.render(f"{velocity:.3f} KM/s", True, (255, 255, 255))

        if quickInfotoggle == True:
            screen.blit(neo_Text, (text_x, nametext_y))
            screen.blit(velocneo_text, (text_x, veloctext_y))


        color = grey
        if normalized_Velocity > 0.6:
            color = (255, 69, 0)
        elif normalized_Velocity > 0.47:
            color = (240, 220, 20)

        pygame.draw.circle(
            screen,
            color,
            center=(int(x), int(y)),
            radius=dot_size
        )

        if selected_Asteroid is not None and dot_name == selected_Asteroid["name"]:
            orbit_w = int(orbit_radius * 2)
            orbit_h = int(orbit_radius * 2 * abs(orbit_tilt) / 8)
            orbit_x = int(earth_x - orbit_radius)
            orbit_y = int(earth_y - (orbit_h / 2))

            displaydot_x = 1360
            displaydot_y = 200

            pygame.draw.line(screen, (255, 50, 50), (earth_x, earth_y), (int(x), int(y)), 2)
            pygame.draw.ellipse(screen, (255, 50, 50), (orbit_x, orbit_y, orbit_w, orbit_h), 3)
            pygame.draw.rect(screen, (0, 60, 150), btn_export)
            pygame.draw.rect(screen, (0, 100, 255), (1165, 75, 400, 280), 2)
            pygame.draw.circle(screen, color, center=(displaydot_x, displaydot_y), radius=dot_size*6)

            export_Text = LogFont.render("EXPORT TELEMETRY DATA", True, (255, 255, 255))
            screen.blit(export_Text, (805, 415))
            
            rotated_surf = pygame.transform.rotate(reticle_surf, angle * 500)
            reticle_rect = rotated_surf.get_rect()
            reticle_rect.center = (int(x), int(y))
            screen.blit(rotated_surf, reticle_rect.topleft)


        if random.random() < 0.00005:
            actual_vel = normalized_Velocity * 30 + 5
            console_logs.append(f"[TRACK] RADAR CONTACT: {dot_name}")
            console_logs.append(f"[DATA] VELOCITY: {actual_vel:.2f} KM/S // INC: {orbit_tilt:.2f}")
            console_logs.append(f"[DATA] RADIUS: {orbit_radius:.2f} KMs")

        if orbitline_Toggle == True:
            orbit_w = int(orbit_radius * 2)
            orbit_h = int(orbit_radius * 2 * abs(orbit_tilt) / 8)
            orbit_x = int(earth_x - orbit_radius)
            orbit_y = int(earth_y - (orbit_h / 2))
            pygame.draw.ellipse(screen, (200, 50, 50), (orbit_x, orbit_y, orbit_w, orbit_h), 1)
        
    angle += 0.005 * time_speed

    for i, (x, y, z, h) in enumerate(points):
        rot_x = x * math.cos(angle) - z * math.sin(angle)
        screen_x = earth_x + rot_x * 125
        screen_y = earth_y + y * 125

        color = (0, 255, 200) if h < 1 else (0, 200, 255)
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 1.5)


    
    pygame.draw.rect(screen, (0, 100, 255), (20, 60, 700, 500), 2)
    pygame.draw.rect(screen, (0, 100, 255), (740, 60, 840, 500), 2)
    pygame.draw.rect(screen, (0, 100, 255), (20, 580, 700, 280), 2)
    pygame.draw.rect(screen, (0, 100, 255), (740, 580, 840, 280), 2)
    pygame.draw.rect(screen, (0, 100, 255), (500, 10, 650, 40), 2)

    banner_Text = font.render("NASA TARGET TRACKING INTERFACE // EARTH SECTOR ", True, (0, 150, 200))
    screen.blit(banner_Text, (547.5, 20))

    CurrentTime = int(time.time() - start_time)
    Time_text = font.render(f"SYSTEM UPTIME: {CurrentTime}s", True, (0, 150, 200))
    screen.blit(Time_text, (35, 525))

    Current_time = pygame.time.get_ticks()

    if Current_time - last_update_time > update_delay:

        radar_Integ = random.randint(85, 98)
        optical_Integ = random.randint(85, 98)
        comms_Integ = random.randint(85, 98)
        last_update_time = Current_time
        update_delay = random.randint(2000, 5000)

    Integ_text = font.render(f"RADAR: {radar_Integ}% OPTICAL: {optical_Integ}% COMMS: {comms_Integ}%", True, (0, 150, 200))
    screen.blit(Integ_text, (290, 525))

    start_x, start_y, line_spacing = 35, 595, 26
    for index, log_message in enumerate(console_logs):
        number = len(console_logs) - 1
        if index == number:
           log_text = LogFont.render(log_message + " ■", True, (0, 200, 255))
           screen.blit(log_text, (start_x, start_y + (index * line_spacing))) 
        else:
            log_text = LogFont.render(log_message, True, (0, 200, 255))
            screen.blit(log_text, (start_x, start_y + (index * line_spacing))) 
    screen.blit(Earth_Text, (35, 70))
    screen.blit(Tracking_text, (400, 70))

    pygame.draw.rect(screen, (0, 60, 150), btn_slow)
    pygame.draw.rect(screen, (0, 60, 150), btn_fast)
    pygame.draw.rect(screen, (0, 60, 150), btn_orbit)
    pygame.draw.rect(screen, (0, 60, 150), btn_pause)
    pygame.draw.rect(screen, (0, 60, 150), btn_play)    
    pygame.draw.rect(screen, (0, 60, 150), btn_info)

    lbl_slow = LogFont.render(" WARP - ", True, (255, 255, 255))
    lbl_play = LogFont.render("PLAY", True, (255, 255, 255))
    lbl_pause = LogFont.render("PAUSE", True, (255, 255, 255))    
    lbl_fast = LogFont.render(" WARP + ", True, (255, 255, 255))
    screen.blit(lbl_slow, (795, 640))
    screen.blit(lbl_play, (970, 700))
    screen.blit(lbl_pause, (805, 700))
    screen.blit(lbl_fast, (955, 640))

    warp_status = font.render(f"SIMULATION TIME WARP VALUE: {time_speed}X", True, (0, 200, 255))
    orbitline_ToggleButtonText = LogFont.render("TOGGLE ORBITS", True, (255, 255, 255))
    screen.blit(warp_status, (760, 595))
    screen.blit(orbitline_ToggleButtonText, (1100, 640))
    
    lbl_info = LogFont.render("TOGGLE INFO", True, (255, 255, 255))
    screen.blit(lbl_info, (1105, 700))


    if selected_Asteroid is not None:
        Name_text = font.render(f"NEO NAME: {selected_Asteroid['name']}", True, (0, 150, 200))
        Speed_text = font.render(f"NEO SPEED: {selected_Asteroid['speed'] * time_speed:.2f} KM/S", True, (0, 150, 200))
        Radius_text = font.render(f"NEO ORBITAL RADIUS: {selected_Asteroid['radius']:.2f}", True, (0, 150, 200))
        Tilt_text = font.render(f"NEO TILT: {selected_Asteroid['tilt']:.2f}", True, (0, 150, 200))
        Size_text = font.render(f"NEO SIZE: {selected_Asteroid['size']}", True, (0, 150, 200))
        Angle_text = font.render(f"NEO ANGLE: {selected_Asteroid['angle']:.2f}", True, (0, 150, 200))
        Depth_text = font.render(f"NEO DEPTH: {selected_Asteroid['depth']:.2f}", True, (0, 150, 200))
        Danger_text = font.render(f"NEO DANGER LEVEL: {selected_Asteroid['danger']}", True, (0, 150, 200))

        screen.blit(Name_text, (760, 70))
        screen.blit(Speed_text, (760, 110))
        screen.blit(Radius_text, (760, 150))
        screen.blit(Tilt_text, (760, 190))
        screen.blit(Size_text, (760, 230))
        screen.blit(Angle_text, (760, 270))
        screen.blit(Depth_text, (760, 310))
        screen.blit(Danger_text, (760, 350))
    else:
        Idle_text = font.render("SYSTEM IDLE // AWAITING TARGET LOCK...", True, (0, 150, 200))
        screen.blit(Idle_text, (760, 70))

            


    pygame.display.flip()
    clock.tick(60)
