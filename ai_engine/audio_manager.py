import os
import sys
import threading

try:
    import pygame
except Exception:
    pygame = None

try:
    from gtts import gTTS
except Exception:
    gTTS = None

try:
    if sys.platform == 'win32':
        import winsound
    else:
        winsound = None
except Exception:
    winsound = None


class AudioManager:
    def __init__(self):
        self.use_winsound = False
        if pygame:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                pass
            self.use_winsound = False
        elif winsound and sys.platform == 'win32':
            self.use_winsound = True

        self.voice_cache_dir = os.path.join("assets", "voices")
        os.makedirs(self.voice_cache_dir, exist_ok=True)

    def play_file(self, path, loops=0, volume=1.0):
        # Fallback between WAV and MP3 if one is specified but only the other exists
        if path and not os.path.exists(path):
            if path.endswith('.mp3'):
                fallback = path.replace('.mp3', '.wav')
                if os.path.exists(fallback):
                    path = fallback
            elif path.endswith('.wav'):
                fallback = path.replace('.wav', '.mp3')
                if os.path.exists(fallback):
                    path = fallback

        if not path or not os.path.exists(path):
            return

        if self.use_winsound and winsound and path.lower().endswith('.wav'):
            try:
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC
                if loops < 0:
                    flags |= winsound.SND_LOOP
                winsound.PlaySound(path, flags)
                return
            except Exception as e:
                print(f"winsound playback failed for {path}: {e}")

        if pygame:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                sound.play(loops=loops)
                return
            except Exception as e:
                pass

            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops=loops)
                return
            except Exception as e:
                print(f"play_file failed for {path}: {e}")

    def play_music(self, path, loops=-1, volume=1.0):
        # Fallback for music files
        if path and not os.path.exists(path):
            if path.endswith('.mp3'):
                fallback = path.replace('.mp3', '.wav')
                if os.path.exists(fallback):
                    path = fallback
            elif path.endswith('.wav'):
                fallback = path.replace('.wav', '.mp3')
                if os.path.exists(fallback):
                    path = fallback

        if not path or not os.path.exists(path):
            return

        if self.use_winsound and winsound and path.lower().endswith('.wav'):
            try:
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC
                if loops < 0:
                    flags |= winsound.SND_LOOP
                winsound.PlaySound(path, flags)
                return
            except Exception as e:
                print(f"winsound background music failed for {path}: {e}")

        if pygame:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops=loops)
            except Exception as e:
                print(f"play_music failed for {path}: {e}")

    def stop_music(self):
        if self.use_winsound and winsound and sys.platform == 'win32':
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
            return
        if pygame:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except Exception:
                pass

    def _speak_gtts(self, text, filename):
        try:
            if not gTTS:
                return False
            # Check if file already exists in cache to save API usage/time
            if not os.path.exists(filename):
                tts = gTTS(text=text, lang="en", slow=False)
                tts.save(filename)
            self.play_file(filename)
            return True
        except Exception as e:
            print(f"gTTS TTS failed: {e}")
            return False

    def speak(self, text):
        """
        Speak text using gTTS (Google Text-to-Speech) with natural voice.
        Run in a background thread to prevent GUI freeze.
        """
        if not gTTS:
            print("AudioManager: gTTS not available, TTS disabled")
            return
        
        # Clean text for filename hashing
        clean_text = "".join(c for c in text if c.isalnum() or c.isspace()).strip()
        fname = os.path.join(self.voice_cache_dir, f"tts_{abs(hash(clean_text)) % 1000000}.mp3")
        threading.Thread(target=self._speak_gtts, args=(text, fname), daemon=True).start()
