import pygame
import math
import random
import requests
import time
import os
import asyncio
from collections import deque

if not os.path.exists("TELEMETRY_DATA"):
    os.makedirs("TELEMETRY_DATA")

pygame.init()
pygame.mixer.init()

try:
    terminal_hum = pygame.mixer.Sound("terminal_hum.flac")
    writing_hum = pygame.mixer.Sound("writing_hum.flac")
    click_effect = pygame.mixer.Sound("click.wav")
except Exception:
    class DummySound:
        def play(self, *args, **kwargs): pass
        def set_volume(self, val): pass
    terminal_hum = writing_hum = click_effect = DummySound()

writing_hum.set_volume(0.03)
click_effect.set_volume(0.05)
terminal_hum.set_volume(0.08)
writing_hum.play(-1)
terminal_hum.play(-1)

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NASA Mission Control - Real Keplerian Dynamics Engine")
API_KEY = "CfOeI4tLdXfiXwIUIRud27MlwYtJYbNWWXuf1H1x"
clock = pygame.time.Clock()

angle = 0
points = []
asteroidsPoints = []
selected_Asteroid = None
orbitline_Toggle = False
time_speed = 1
earth_x = 370
earth_y = 310
url = "https://api.nasa.gov/neo/rest/v1/feed"
start_time = time.time()
params = {"start_date": "2026-01-01", "end_date": "2026-01-08", "api_key": API_KEY}

reticle_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
last_update_time = 0
update_delay = 2000
quickInfotoggle = False
last_button_press_time = 0
debounce_cooldown = 150

radar_Integ = random.randint(85, 98)
optical_Integ = random.randint(85, 98)
comms_Integ = random.randint(85, 98)

response = requests.get(url, params=params)
data = response.json()
grey = (200, 200, 200)
asteroids = data["near_earth_objects"]
total_asteroids = sum(len(asteroids[day]) for day in asteroids)

SCALE_FACTOR = 100

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
btn_delete = pygame.Rect(790, 465, 220, 50)

pygame.draw.circle(reticle_surf, (255, 50, 50), (30, 30), 12, 1)
pygame.draw.line(reticle_surf, (255, 50, 50), (30, 2), (30, 8), 2)
pygame.draw.line(reticle_surf, (255, 50, 50), (30, 58), (30, 52), 2)
pygame.draw.line(reticle_surf, (255, 50, 50), (2, 30), (8, 30), 2)
pygame.draw.line(reticle_surf, (255, 50, 50), (58, 30), (52, 30), 2)
pygame.draw.rect(reticle_surf, (255, 50, 50), (30, 30, 2, 2))

def solve_kepler(M, e):
    E = M
    for _ in range(5):
        E = E - (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
    return E

def fetch_real_orbital_elements(asteroid_id):
    clean_id = asteroid_id.replace("(", "").replace(")", "").strip()
    sbdb_url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={clean_id}&phys-par=0"
    try:
        res = requests.get(sbdb_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if "orbit" in data and "elements" in data["orbit"]:
                elements = data["orbit"]["elements"]
                elem_dict = {item["name"]: float(item["value"]) for item in elements}
                return elem_dict.get("a"), elem_dict.get("e"), elem_dict.get("i"), elem_dict.get("ma")
    except Exception:
        pass
    return None

def draw_ellipse_path(asteroid):
    points_list = []
    tilt_factor = math.sin(math.radians(asteroid["tilt"]))
    for step in range(65):
        M_sample = (step / 64.0) * math.pi * 2
        E_sample = solve_kepler(M_sample, asteroid["e"])
        x_orb_centered = asteroid["a"] * math.cos(E_sample)
        y_orb = asteroid["a"] * math.sqrt(1.0 - asteroid["e"]**2) * math.sin(E_sample)
        x_screen = earth_x + x_orb_centered
        y_screen = earth_y + y_orb * tilt_factor * 1.5
        points_list.append((int(x_screen), int(y_screen)))
    if len(points_list) > 1:
        pygame.draw.lines(screen, (0, 150, 255), False, points_list, 1)

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
        asteroid_id = asteroid["id"]
        approach = asteroid["close_approach_data"][0]
        velocity = float(approach["relative_velocity"]["kilometers_per_second"])
        distance = float(approach["miss_distance"]["astronomical"])

        orb_elements = fetch_real_orbital_elements(asteroid_id)

        if orb_elements and orb_elements[0] is not None:
            Ba, Be, Bi, BM = orb_elements
            a = 150 + (Ba * 120)
            e = Be
            orbit_tilt = Bi
            mean_anomaly = math.radians(BM)
            base_a = Ba
        else:
            base_a = 1.2 + (distance * 0.5)
            a = 140 + (distance * 180)
            e = random.uniform(0.05, 0.35)
            orbit_tilt = random.uniform(-4, 12)
            mean_anomaly = random.uniform(0, math.pi * 2)

        mean_motion = 0.002 / math.sqrt(max(0.1, base_a**3))

        asteroid_d = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"]
        ratio = math.log(max(0.001, asteroid_d))
        dot_size = max(3, min(8, int(ratio * SCALE_FACTOR)))
        normalized_Velocity = (velocity - 5) / 30
        z = random.uniform(-1, 1)

        asteroidsPoints.append({
            "name": name, "size": dot_size, "approach": approach,
            "a": a, "e": e, "M": mean_anomaly, "n": mean_motion,
            "tilt": orbit_tilt, "z": z, "velocity": velocity, 
            "norm_vel": normalized_Velocity, "danger": "LOW"
        })

console_logs = deque([
    "[SYSTEM] Keplerian Mechanics Architecture: ONLINE",
    "[INFO] Connected to NASA/JPL Data Matrix Server Repository...",
    "[SYSTEM] Resolving Eccentric Vector Transformation Spaces..."
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

async def main():
    global angle, selected_Asteroid, time_speed, orbitline_Toggle, quickInfotoggle
    global last_button_press_time, radar_Integ, optical_Integ, comms_Integ, last_update_time, update_delay

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    time_speed += 1
                elif event.key == pygame.K_a:
                    time_speed = max(1, time_speed - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mouse_x, mouse_y = mouse_pos

                if current_time - last_button_press_time > debounce_cooldown:
                    click_effect.play()
                    last_button_press_time = current_time
                
                if btn_slow.collidepoint(mouse_pos):
                    time_speed = max(1, time_speed - 1)
                    console_logs.append(f"[SYSTEM] TIME WARP REDUCED: {time_speed}X")
                elif btn_fast.collidepoint(mouse_pos):
                    time_speed += 1
                    console_logs.append(f"[SYSTEM] TIME WARP INCREASED: {time_speed}X")
                elif btn_orbit.collidepoint(mouse_pos):
                    orbitline_Toggle = not orbitline_Toggle
                    console_logs.append(f"[TRACKING] ORBIT LINES TOGGLED: {orbitline_Toggle}")
                elif btn_pause.collidepoint(mouse_pos):
                    time_speed = 0
                    console_logs.append(f"[SYSTEMS] SYSTEM PAUSED")
                elif btn_play.collidepoint(mouse_pos):
                    time_speed = 1
                    console_logs.append(f"[SYSTEMS] SYSTEM RESUMED")
                elif btn_info.collidepoint(mouse_pos):
                    quickInfotoggle = not quickInfotoggle
                    console_logs.append(f"[INFO] QUICK INFO TOGGLED")
                elif btn_delete.collidepoint(mouse_pos):
                    target_dir = "TELEMETRY_DATA"
                    try:
                        if os.path.exists(target_dir):
                            reports = os.listdir(target_dir)
                            if reports:
                                console_logs.append(f"[SYSTEM] DELETING {len(reports)} TELEMETRY REPORTS")
                                for file_name in reports:
                                    file_path = os.path.join(target_dir, file_name)
                                    if os.path.isfile(file_path):
                                        os.remove(file_path)
                            else:
                                console_logs.append(f"[ERROR] NO TELEMETRY REPORTS SAVED")
                        else:
                            console_logs.append("[ERROR] FAILED TO FIND FOLDER")
                    except Exception as e:
                        console_logs.append(f"[ERROR] COULD NOT CLEAR FOLDER: {str(e)}")

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
                                file.write(f"SECTOR SPEED:   {selected_Asteroid['speed']:.2f} KM/S\n")
                                file.write(f"ORBIT RADIUS:   {selected_Asteroid['radius']:.2f}\n")
                                file.write(f"ECLIPTIC TILT:  {selected_Asteroid['tilt']:.2f}\n")
                                file.write(f"EST. SIZE CAT:  {selected_Asteroid['size']}\n")
                                file.write(f"MEAN ANOMALY:   {selected_Asteroid['angle']:.2f}\n")
                                file.write(f"THREAT LEVEL:   {selected_Asteroid['danger']}\n\n")
                                file.write("==================================================\n")
                            console_logs.append(f"[SUCCESS] EXPORTED TO {safe_name}_report.txt")
                        except Exception as e:
                            console_logs.append(f"[ERROR] WRITE FAILED: {str(e)}")
                else:
                    hit_detected = False
                    for asteroid in asteroidsPoints:
                        tilt_factor = math.sin(math.radians(asteroid["tilt"]))
                        E = solve_kepler(asteroid["M"], asteroid["e"])
                        x_orb_centered = asteroid["a"] * math.cos(E)
                        x_orb_actual = asteroid["a"] * (math.cos(E) - asteroid["e"])
                        y_orb = asteroid["a"] * math.sqrt(1.0 - asteroid["e"]**2) * math.sin(E)
                        check_x = earth_x + x_orb_centered
                        y_screen = earth_y + y_orb * tilt_factor * 1.5
                        
                        if math.hypot(mouse_x - check_x, mouse_y - y_screen) < 14:
                            r = math.hypot(x_orb_actual, y_orb)
                            inst_velocity = asteroid["velocity"] * math.sqrt((2.0 * asteroid["a"] / max(1, r)) - 1.0)
                            danger = "HIGH" if asteroid["norm_vel"] > 0.6 else ("MEDIUM" if asteroid["norm_vel"] > 0.47 else "LOW")
                            
                            console_logs.append(f"[TRACK] LOCK ACQUIRED: {asteroid['name']}")
                            selected_Asteroid = {
                                "name": asteroid["name"], "speed": inst_velocity, "radius": r,
                                "tilt": asteroid["tilt"], "size": asteroid["size"], "angle": asteroid["M"],
                                "depth": asteroid["z"], "danger": danger
                            }
                            hit_detected = True
                            break
                    if not hit_detected:
                        selected_Asteroid = None

        screen.fill((5, 10, 20))
        
        if random.random() < 0.01:
            console_logs.append(random.choice(generic_pool))

        for asteroid in asteroidsPoints:
            asteroid["M"] += asteroid["n"] * time_speed
            asteroid["M"] %= (math.pi * 2)

            tilt_factor = math.sin(math.radians(asteroid["tilt"]))
            E = solve_kepler(asteroid["M"], asteroid["e"])
            
            x_orb_centered = asteroid["a"] * math.cos(E)
            x_orb_actual = asteroid["a"] * (math.cos(E) - asteroid["e"])
            y_orb = asteroid["a"] * math.sqrt(1.0 - asteroid["e"]**2) * math.sin(E)
            
            x = earth_x + x_orb_centered
            y = earth_y + y_orb * tilt_factor * 1.5

            r_inst = math.hypot(x_orb_actual, y_orb)
            inst_velocity = asteroid["velocity"] * math.sqrt((2.0 * asteroid["a"] / max(1, r_inst)) - 1.0)

            if quickInfotoggle:
                neo_Text = NEOfont.render(f"{asteroid['name']}", True, (255, 255, 255))
                velocneo_text = NEOfont.render(f"{inst_velocity:.2f} KM/s", True, (0, 255, 150))
                screen.blit(neo_Text, (int(x) + 10, int(y) + 10))
                screen.blit(velocneo_text, (int(x) + 10, int(y) + 22))

            color = (255, 69, 0) if asteroid["norm_vel"] > 0.6 else ((240, 220, 20) if asteroid["norm_vel"] > 0.47 else grey)
            pygame.draw.circle(screen, color, (int(x), int(y)), asteroid["size"])

            if orbitline_Toggle:
                draw_ellipse_path(asteroid)

            if selected_Asteroid is not None and asteroid["name"] == selected_Asteroid["name"]:
                draw_ellipse_path(asteroid)
                pygame.draw.line(screen, (255, 50, 50), (earth_x, earth_y), (int(x), int(y)), 1)
                
                rotated_surf = pygame.transform.rotate(reticle_surf, angle * 120)
                reticle_rect = rotated_surf.get_rect(center=(int(x), int(y)))
                screen.blit(rotated_surf, reticle_rect.topleft)

                selected_Asteroid["speed"] = inst_velocity
                selected_Asteroid["radius"] = r_inst
                selected_Asteroid["angle"] = asteroid["M"]

        angle += 0.005 * time_speed

        for x_p, y_p, z_p, h_p in points:
            rot_x = x_p * math.cos(angle) - z_p * math.sin(angle)
            screen_x = earth_x + rot_x * 125
            screen_y = earth_y + y_p * 125
            c_val = (0, 255, 200) if h_p < 1 else (0, 200, 255)
            pygame.draw.circle(screen, c_val, (int(screen_x), int(screen_y)), 1)

        pygame.draw.rect(screen, (0, 100, 255), (20, 60, 700, 500), 2)
        pygame.draw.rect(screen, (0, 100, 255), (740, 60, 840, 500), 2)
        pygame.draw.rect(screen, (0, 100, 255), (20, 580, 700, 280), 2)
        pygame.draw.rect(screen, (0, 100, 255), (740, 580, 840, 280), 2)
        pygame.draw.rect(screen, (0, 100, 255), (500, 10, 650, 40), 2)

        banner_Text = font.render("NASA TARGET TRACKING INTERFACE // ECLIPTIC GEOMETRY", True, (0, 150, 200))
        screen.blit(banner_Text, (547.5, 20))

        uptime = int(time.time() - start_time)
        screen.blit(font.render(f"SYSTEM UPTIME: {uptime}s", True, (0, 150, 200)), (35, 525))

        if current_time - last_update_time > update_delay:
            radar_Integ = random.randint(85, 98)
            optical_Integ = random.randint(85, 98)
            comms_Integ = random.randint(85, 98)
            last_update_time = current_time
            update_delay = random.randint(2000, 5000)

        Integ_text = font.render(f"RADAR: {radar_Integ}% OPTICAL: {optical_Integ}% COMMS: {comms_Integ}%", True, (0, 150, 200))
        screen.blit(Integ_text, (290, 525))

        start_x, start_y, line_spacing = 35, 595, 26
        for index, log_message in enumerate(console_logs):
            is_last = (index == len(console_logs) - 1)
            log_text = LogFont.render(log_message + (" ■" if is_last else ""), True, (0, 200, 255) if is_last else (0, 140, 200))
            screen.blit(log_text, (start_x, start_y + (index * line_spacing)))

        screen.blit(Earth_Text, (35, 70))
        screen.blit(Tracking_text, (400, 70))

        for btn, lbl, lx, ly in [
            (btn_slow, " WARP - ", 795, 640), (btn_fast, " WARP + ", 955, 640),
            (btn_pause, "PAUSE", 805, 700), (btn_play, "PLAY", 970, 700),
            (btn_orbit, "TOGGLE ORBITS", 1100, 640), (btn_info, "TOGGLE INFO", 1105, 700)
        ]:
            pygame.draw.rect(screen, (0, 60, 150), btn)
            screen.blit(LogFont.render(lbl, True, (255, 255, 255)), (lx, ly))

        warp_status = font.render(f"SIMULATION TIME WARP VALUE: {time_speed}X", True, (0, 200, 255))
        screen.blit(warp_status, (760, 595))

        if selected_Asteroid is not None:
            pygame.draw.rect(screen, (0, 60, 150), btn_export)
            pygame.draw.rect(screen, (0, 60, 150), btn_delete)
            pygame.draw.rect(screen, (0, 100, 255), (1165, 75, 400, 280), 2)
            pygame.draw.circle(screen, (255, 50, 50), center=(1365, 200), radius=selected_Asteroid["size"] * 5)

            screen.blit(LogFont.render("EXPORT TELEMETRY DATA", True, (255, 255, 255)), (805, 415))
            screen.blit(LogFont.render("DELETE ALL FILES", True, (255, 255, 255)), (825, 480))

            labels = [
                f"NEO NAME: {selected_Asteroid['name']}",
                f"INST SPEED: {selected_Asteroid['speed']:.2f} KM/S",
                f"RADIUS VECTOR: {selected_Asteroid['radius']:.1f} KM",
                f"ECLIPTIC TILT: {selected_Asteroid['tilt']:.2f} DEG",
                f"MAGNITUDE CAT: {selected_Asteroid['size']}",
                f"MEAN ANOMALY: {selected_Asteroid['angle']:.2f} RAD",
                f"Z-AXIS DEPTH: {selected_Asteroid['depth']:.2f}",
                f"DANGER LEVEL: {selected_Asteroid['danger']}"
            ]
            for i, text_lbl in enumerate(labels):
                screen.blit(font.render(text_lbl, True, (0, 180, 255) if "DANGER" in text_lbl else (0, 150, 200)), (760, 70 + (i * 38)))
        else:
            screen.blit(font.render("SYSTEM IDLE // AWAITING TARGET RADAR LOCK...", True, (0, 150, 200)), (760, 70))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())