import os
import sys
import threading
import platform

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
                print(f"play_file sound failed for {path}: {e}")

            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops=loops)
                return
            except Exception as e:
                print(f"play_file music failed for {path}: {e}")
                return

    def play_music(self, path, loops=-1, volume=1.0):
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
            # Use slow=False for normal speed (1x)
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(filename)
            self.play_file(filename)
            return True
        except Exception as e:
            print(f"gTTS TTS failed: {e}")
            return False

    def speak(self, text, prefer="gTTS", allow_fallback=True, rate=None, voice=None):
        """
        Speak text using gTTS (Google Text-to-Speech) with natural voice.
        Parameters rate and voice are ignored as we only use gTTS.
        All voices use normal speed (1x).
        """
        if not gTTS:
            print("AudioManager: gTTS not available, TTS disabled")
            return
        
        fname = os.path.join(self.voice_cache_dir, f"tts_{abs(hash(text)) % 100000}.mp3")
        threading.Thread(target=self._speak_gtts, args=(text, fname), daemon=True).start()
