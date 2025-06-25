import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont
import base64

# Base64 encode the font for embedding in CSS
def get_base64_font(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

font_data = get_base64_font("arcadeclassic.ttf")
# Streamlit Setup
st.set_page_config(page_title="Gesture Dino Game", layout="wide")
arcade_font_base64 = get_base64_font("arcadeclassic.ttf")
st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'ArcadeClassic';
        src: url(data:font/ttf;base64,{arcade_font_base64}) format('truetype');
    }}
    html, body, [class*="css"] {{
        font-family: 'ArcadeClassic', sans-serif !important;
    }}
    .stButton>button, .stCheckbox>label, .stTextInput>div>div>input, .stMarkdown, .stTitle, h1, h2, h3, h4 {{
        font-family: 'ArcadeClassic', sans-serif !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("Gesture Controlled Dino Game")

# Theme Toggle Setup
if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = False  # Default: Light

toggle_label = "🌙 Switch to Dark Mode" if not st.session_state.theme_dark else "☀️ Switch to Light Mode"
if st.button(toggle_label):
    st.session_state.theme_dark = not st.session_state.theme_dark

# Theme Styling
if st.session_state.theme_dark:
    st.markdown("""
        <style>
        body, .block-container {
            background-color: #111 !important;
            color: white !important;
        }
        .stButton>button {
            background-color: #333 !important;
            color: white !important;
            border: 1px solid #aaa !important;
            padding: 6px 12px !important;
            border-radius: 6px !important;
        }
        .stButton>button:hover {
            background-color: #444 !important;
            color: white !important;
        }
        .stCheckbox>label {
        color: white !important;
        font-weight: bold !important;
        font-size: 18px;
    }
        </style>
    """, unsafe_allow_html=True)
    font_color = (200, 255, 255)
    high_score_color = (255, 215, 0)
else:
    st.markdown("""
        <style>
        body, .block-container {
            background-color: white !important;
            color: black !important;
        }
        .stButton>button {
            background-color: #f0f0f0 !important;
            color: black !important;
            border: 1px solid #999 !important;
            padding: 6px 12px !important;
            border-radius: 6px !important;
        }
        .stButton>button:hover {
            background-color: #e0e0e0 !important;
            color: black !important;
        }
         .stCheckbox>label {
        color: black !important;
        font-weight: bold !important;
        font-size: 18px;
    }
        </style>
    """, unsafe_allow_html=True)
    font_color = (0, 0, 0)
    high_score_color = (255, 0, 0)

run = st.checkbox("Start Game")

arcade_font = ImageFont.truetype("arcadeclassic.ttf", 24)

def draw_arcade_text(img, text, position, font=arcade_font, color=(0, 0, 0)):
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    draw.text(position, text, font=font, fill=color)
    return np.array(pil_img)

def load_image(path, size):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return cv2.resize(img, size)

dino_img1 = load_image("DinoRun1.png", (60, 60))
dino_img2 = load_image("DinoRun2.png", (60, 60))
dino_jump_img = load_image("DinoJump.png", (60, 60))
dino_duck_img = load_image("downdino.jpg", (60, 40))
cactus_img1 = load_image("cactus.png", (40, 60))
cactus_img2 = load_image("cactusB.png", (60, 60))
bird_img = load_image("bird1.png", (60, 40))
dead_img = load_image("DinoDead.png", (60, 60))
game_over_img = load_image("restart_icon.png", (300, 100))
restart_img = load_image("gameover.png", (50, 50))
start_img = load_image("start.png", (640, 300))

def overlay_image(bg, fg, x, y):
    if fg is None:
        return bg
    h, w = fg.shape[:2]
    bg_h, bg_w = bg.shape[:2]
    if x >= bg_w or y >= bg_h or x + w <= 0 or y + h <= 0:
        return bg
    fg_x1 = max(0, -x)
    fg_y1 = max(0, -y)
    fg_x2 = min(w, bg_w - x)
    fg_y2 = min(h, bg_h - y)
    bg_x1 = max(0, x)
    bg_y1 = max(0, y)
    bg_x2 = bg_x1 + (fg_x2 - fg_x1)
    bg_y2 = bg_y1 + (fg_y2 - fg_y1)
    fg_crop = fg[fg_y1:fg_y2, fg_x1:fg_x2]
    if len(fg_crop.shape) < 3 or fg_crop.shape[0] == 0 or fg_crop.shape[1] == 0:
        return bg
    if fg_crop.shape[2] == 4:
        alpha = fg_crop[:, :, 3] / 255.0
        for c in range(3):
            bg[bg_y1:bg_y2, bg_x1:bg_x2, c] = (
                (1 - alpha) * bg[bg_y1:bg_y2, bg_x1:bg_x2, c] + alpha * fg_crop[:, :, c]
            ).astype(np.uint8)
    else:
        bg[bg_y1:bg_y2, bg_x1:bg_x2] = fg_crop
    return bg

if "high_score" not in st.session_state:
    st.session_state.high_score = 0

dino_y, velocity, gravity = 220, 0, 1
jumping, ducking, game_over = False, False, False
score = 0

cactus_objects = []
last_cactus_x = 640
for _ in range(3):
    last_cactus_x += random.randint(500, 800)
    cactus_objects.append((last_cactus_x, random.choice([cactus_img1, cactus_img2])))

bird_positions, bird_heights = [], []
last_bird_x = 2000
for _ in range(2):
    last_bird_x += random.randint(2200, 2500)
    bird_positions.append(last_bird_x)
    bird_heights.append(220)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
col1, col2 = st.columns(2)
col1.markdown("###  Game View")
FRAME_WINDOW = col1.image([])
col2.markdown("###  Your Gesture Feed")
webcam_display = col2.image([])

if not run:
    FRAME_WINDOW.image(start_img, channels="BGR", use_container_width=True)
    cap.release()
    st.stop()

while run:
    ret, frame = cap.read()
    if not ret:
        st.error("📷 Cannot access webcam.")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hand_raised = hand_down = False
    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
        index_tip, index_dip, wrist = lm.landmark[8], lm.landmark[7], lm.landmark[0]
        if index_tip.y < index_dip.y:
            hand_raised = True
        elif index_tip.y > index_dip.y and abs(index_tip.y - wrist.y) < 0.15:
            hand_down = True

    if hand_raised and not jumping:
        velocity, jumping, ducking = -15, True, False
    elif hand_down and not jumping:
        ducking = True
    else:
        ducking = False

    dino_y += velocity
    velocity += gravity
    if dino_y >= 220:
        dino_y, velocity, jumping = 220, 0, False

    cactus_objects = [(x - 14, img) for x, img in cactus_objects if x > -60]
    while len(cactus_objects) < 3:
        last_x = cactus_objects[-1][0] if cactus_objects else 640
        cactus_objects.append((last_x + random.randint(500, 800), random.choice([cactus_img1, cactus_img2])))
        score += 1

    bird_positions = [x - 16 for x in bird_positions]
    while bird_positions and bird_positions[0] < -60:
        bird_positions.pop(0)
        bird_heights.pop(0)
        last_bird_x = bird_positions[-1] if bird_positions else 1000
        bird_positions.append(last_bird_x + random.randint(2200, 2500))
        bird_heights.append(220)
        score += 1

    for cx, cimg in cactus_objects:
        if 100 < cx < 160 and dino_y > 160 and not ducking:
            game_over = True

    for bx, by in zip(bird_positions, bird_heights):
        if 100 < bx < 160 and dino_y >= 180:
            game_over = True

    game_frame = np.ones((300, 640, 3), dtype=np.uint8) * 255
    cv2.line(game_frame, (0, 280), (640, 280), (0, 0, 0), 2)

    frame_toggle = int(time.time() * 10) % 2
    if game_over:
        game_frame = overlay_image(game_frame, dead_img, 100, dino_y)
    elif ducking:
        game_frame = overlay_image(game_frame, dino_duck_img, 100, 240)
    elif jumping:
        game_frame = overlay_image(game_frame, dino_jump_img, 100, dino_y)
    else:
        game_frame = overlay_image(game_frame, dino_img1 if frame_toggle else dino_img2, 100, dino_y)

    for cx, cimg in cactus_objects:
        game_frame = overlay_image(game_frame, cimg, cx, 220)
    for bx, by in zip(bird_positions, bird_heights):
        game_frame = overlay_image(game_frame, bird_img, bx, by)

    st.session_state.high_score = max(st.session_state.high_score, score)
    game_frame = draw_arcade_text(game_frame, f"Score: {score}", (10, 10), color=font_color)
    game_frame = draw_arcade_text(game_frame, f"High Score: {st.session_state.high_score}", (400, 10), color=high_score_color)

    if game_over:
        game_frame = overlay_image(game_frame, game_over_img, 170, 60)
        game_frame = overlay_image(game_frame, restart_img, 295, 180)
        game_frame = draw_arcade_text(game_frame, "Restart", (270, 245), color=font_color)
        FRAME_WINDOW.image(game_frame, channels="BGR", use_container_width=True)
        webcam_display.image(frame, channels="BGR", use_container_width=True)
        cap.release()
        break

    FRAME_WINDOW.image(game_frame, channels="BGR", use_container_width=True)
    webcam_display.image(frame, channels="BGR", use_container_width=True)

# Restart Button after game over
if game_over:
    restart = st.button(" Restart Game")
    if restart:
        st.rerun()
