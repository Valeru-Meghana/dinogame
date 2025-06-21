# 🦖 Gesture-Controlled Dino Game using Streamlit

A fun and interactive Dino Game built with **Streamlit**, **OpenCV**, and **MediaPipe** — where you control the Dino using **hand gestures** through your webcam! Inspired by the classic Chrome Dino Game, this version adds gesture-based gameplay, dynamic background changes, sound effects, and more.

![Dino Game Demo](demo.gif) <!-- Replace with your own demo gif/image -->

---

## 🚀 Features

✅ Gesture control using webcam (jump when hand raised)  
✅ Streamlit UI for web-based play (no need for Pygame!)  
✅ Dynamic background: desert → city → night as score increases  
✅ Sound effects on jump and game over  
✅ Moving clouds, birds, and dust animations  
✅ On-canvas UI: Game Over and Restart buttons appear inside the game  
✅ Persistent high score saved between reruns  
✅ Responsive camera resolution and distortion fixes  
✅ Level progression — game gets faster as you play longer  

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [NumPy](https://numpy.org/)
- [PIL (Pillow)](https://python-pillow.org/)
- Base64 and local storage for sound/fonts

---

## 📸 How to Play

1. Raise your hand to make the Dino **jump**.
2. Avoid cacti and birds.
3. Keep scoring as long as you survive.
4. Hit **Restart** on screen if the game ends.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gesture-dino-game.git
cd gesture-dino-game

# Install dependencies
pip install -r requirements.txt

# Run the game
streamlit run app.py
