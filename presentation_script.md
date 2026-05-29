# Video Presentation Script: AI Kiddy Learner ✨
**Duration**: 5 - 10 Minutes (Strictly)
**Platform suggestion**: Zoom (easy to record screen-share and facecams) or Canva/Clipchamp.

---

## 👥 Group Roles & Agenda:
1. **Bekhzodbek (Project Lead & Core AI Logic)**: Introduction, Project Goals, Adaptive AI Architecture.
2. **Mehedhi Hassan Rafi (Speech Interface & VUI)**: Speech Recognition (Vosk) & TTS (gTTS) implementation.
3. **Shakhwat (UI/UX & Graphics)**: Pygame interface, animations, particles, layout.
4. **Hafiss (Host & Integration & Demo)**: Live game runtime demonstration, statistics, closing.

---

## 🎙️ Slide-by-Slide Script

### Section 1: Introduction & Goals (Bekhzodbek)
**Time**: 0:00 - 1:30
- **Visuals**: Title slide showing project name: "Adaptive AI-Driven Educational Game for Early Childhood Literacy". Facecams of members visible.
- **Bekhzodbek's Script**:
  > "Hello everyone, my name is Bekhzodbek, and I am the lead developer for our Artificial Intelligence group project: **AI Kiddy Learner**.
  > Our target audience is young children aged 4 to 6. Traditional static software often fails young children because it does not adapt to their unique learning speed, mistakes, or short attention spans.
  > Our objective was to create an interactive, bright, and highly visual game that teaches letters, pronunciation, and vocabulary. Most importantly, we wanted to build a system that demonstrates true **Intelligence** by adapting to the child's mistakes in real-time. Let's look at how we designed this."

---

### Section 2: Technical Architecture & Adaptive AI (Bekhzodbek)
**Time**: 1:30 - 3:00
- **Visuals**: Block diagram of the code architecture: `main.py` -> `AdaptiveAIEngine` -> `gui` (Pygame).
- **Bekhzodbek's Script**:
  > "For our backend, we designed a custom **Adaptive AI Engine** in Python. Instead of just selecting random questions, our AI engine keeps track of every mistake the child makes using a dynamic mistake tracker.
  > If a child struggles with a word, there is a **40% probability** that the AI will re-introduce that word in the next rounds.
  > Furthermore, the AI adapts its help level: if the child gets a word wrong twice, the hint dynamically reveals the first letter of the word, helping them learn without feeling discouraged.
  > Now, Mehedhi will explain how we built the Voice User Interface."

---

### Section 3: Speech Recognition & TTS (Mehedhi Hassan Rafi)
**Time**: 3:00 - 4:30
- **Visuals**: Code snippet of `gui/speak_with_ai.py` showing Vosk model initialization and `gTTS` thread.
- **Mehedhi's Script**:
  > "Thank you, Bekhzodbek. To earn bonus points and make the game interactive, we built a **Voice User Interface (VUI)**.
  > We integrated **Vosk Speech Recognition**, an offline Kaldi-based neural network model. The game captures raw audio from the microphone using the `sounddevice` library, converts it to PCM data, and passes it to Vosk.
  > To guide the child, we use **gTTS (Google Text-to-Speech)** to synthesize clean, natural human voices.
  > When a child says a word, the VUI translates their speech, checks it against the correct pronunciation using a tolerant spelling heuristic (which accounts for child pronunciation), and speaks back to give immediate, encouraging feedback."

---

### Section 4: UI/UX & Animations (Shakhwat)
**Time**: 4:30 - 6:00
- **Visuals**: Slides showing button glow and particle math code in `effects.py`.
- **Shakhwat's Script**:
  > "Thank you, Mehedhi. For kindergarten children, the interface must be extremely clean, colorful, and engaging.
  > We used **Pygame** to build a responsive, child-friendly user interface.
  > To capture their attention, we created a full custom particle and effect engine:
  > First, we have **Glow Effects** that light up buttons when hovered.
  > Second, when a child answers correctly, the game bursts into celebration with **Star Particles** and falling **Confetti**.
  > Third, if they select the wrong word, the entire screen vibrates using a custom **Shake Effect** to provide immediate physical feedback without being punitive.
  > Now, Hafiss will show the game in action."

---

### Section 5: Live Runtime Demo (Hafiss)
**Time**: 6:00 - 8:30
- **Visuals**: Live screen-share of the running game.
- **Hafiss's Script**:
  > "Thank you, Shakhwat. I will now demonstrate the game.
  > As you see, the main menu is clean with large, bright buttons. When I hover my mouse, the buttons glow.
  > Let's open **My Stats**. Thanks to our animated counters, the accuracy and score rise smoothly.
  > Now, let's play **Play with Words**. I see a picture of an apple. If I click 'Apple', the stars explode and we hear a gentle praise.
  > Let's make a mistake on the next one. The screen shakes, and a text hint appears.
  > Now, let's test **Speak with AI**. I see a lion. I click 'START MIC' and say: 'LION'. As you see, the system captures my voice, analyzes it using the AI model, and confirms I am correct!
  > If I am wrong, the system encourages me to try again. Both games save stats automatically to a local JSON file.
  > This concludes our presentation. Thank you for your time!"
