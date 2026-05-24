import math
import struct
import pygame
from src.settings import SOUND_ENABLED

class SoundEngine:
    def __init__(self):
        self.enabled = SOUND_ENABLED
        self.sounds = {}
        self.mixer_initialized = False
        
        if not self.enabled:
            return

        try:
            # Initialize mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.mixer_initialized = True
            
            # Generate all sounds
            self._pregenerate_sounds()
        except Exception as e:
            print(f"Warning: Failed to initialize sound engine ({e}). Playing in silent mode.")
            self.mixer_initialized = False
            self.enabled = False

    def _pregenerate_sounds(self):
        """Generates all classic retro sounds programmatically to avoid external files."""
        # 1. Waka sounds (alternating chewing noises)
        self.sounds["waka1"] = self._create_sweep(400, 700, 0.08, "triangle", volume=0.15)
        self.sounds["waka2"] = self._create_sweep(700, 400, 0.08, "triangle", volume=0.15)
        
        # 2. Eating Power Pellet
        self.sounds["eat_power"] = self._create_sweep(150, 400, 0.15, "square", volume=0.2)
        
        # 3. Eating a Ghost (rapid upward sweep)
        self.sounds["eat_ghost"] = self._create_sweep(300, 1500, 0.5, "sawtooth", volume=0.25)
        
        # 4. Pacman Death (classic descending wail)
        self.sounds["death"] = self._create_death_sound()
        
        # 5. Background Siren (low warning tone)
        self.sounds["siren"] = self._create_siren_sound()
        
        # 6. Intro melody (arcade start tune)
        self.sounds["intro"] = self._create_intro_melody()
        
        # 7. Level cleared melody
        self.sounds["clear"] = self._create_clear_melody()

    def _create_sweep(self, start_freq, end_freq, duration, wave_type="square", volume=0.2):
        """Creates a sound sweep from start_freq to end_freq."""
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / sample_rate
            # Linear frequency sweep
            freq = start_freq + (end_freq - start_freq) * (i / num_samples)
            
            # Generate wave phase
            phase = 2.0 * math.pi * freq * t
            
            if wave_type == "sine":
                val = math.sin(phase)
            elif wave_type == "square":
                val = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave_type == "sawtooth":
                # Fractional part scaled between -1 and 1
                val = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif wave_type == "triangle":
                val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
            else:
                val = math.sin(phase)
                
            # Envelope (soft fade-out to prevent pops)
            envelope = 1.0
            if i > num_samples - 400:
                envelope = (num_samples - i) / 400.0
                
            sample = int(val * volume * 32767 * envelope)
            samples.append(sample)
            
        byte_data = struct.pack(f"{len(samples)}h", *samples)
        return pygame.mixer.Sound(buffer=byte_data)

    def _create_death_sound(self):
        """Generates the classic descending arcade death sweep."""
        sample_rate = 22050
        duration = 1.0
        num_samples = int(sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            progress = i / num_samples
            t = i / sample_rate
            
            # Descending frequency with a bubbling/vibrato LFO effect
            base_freq = 900 * (1.0 - progress) + 80
            vibrato = 1.0 + 0.15 * math.sin(2.0 * math.pi * 35 * t)
            freq = base_freq * vibrato
            
            # Raw square wave
            phase = 2.0 * math.pi * freq * t
            val = 1.0 if math.sin(phase) >= 0 else -1.0
            
            # Fade out towards the end
            envelope = 1.0 - progress
            
            sample = int(val * 0.25 * 32767 * envelope)
            samples.append(sample)
            
        byte_data = struct.pack(f"{len(samples)}h", *samples)
        return pygame.mixer.Sound(buffer=byte_data)

    def _create_siren_sound(self):
        """Creates the repeating background siren sound."""
        sample_rate = 22050
        duration = 0.5
        num_samples = int(sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / sample_rate
            # Siren frequency rises and falls smoothly
            freq = 280 + 80 * math.sin(2.0 * math.pi * 2.0 * t)
            
            phase = 2.0 * math.pi * freq * t
            val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0  # Triangle wave
            
            sample = int(val * 0.12 * 32767)
            samples.append(sample)
            
        byte_data = struct.pack(f"{len(samples)}h", *samples)
        return pygame.mixer.Sound(buffer=byte_data)

    def _create_intro_melody(self):
        """Generates a beautiful synthesized start screen intro melody."""
        # Simple arcade opening motif (notes: C5, C6, G5, E5, C6, G5, E5, pause, B4, B5, F#5, D#5, B5, F#5, D#5...)
        notes = [
            (523, 0.1),  # C5
            (1046, 0.1), # C6
            (784, 0.1),  # G5
            (659, 0.1),  # E5
            (1046, 0.08),# C6
            (784, 0.08), # G5
            (659, 0.15), # E5
            (0, 0.05),   # Pause
            (494, 0.1),  # B4
            (988, 0.1),  # B5
            (740, 0.1),  # F#5
            (622, 0.1),  # D#5
            (988, 0.08), # B5
            (740, 0.08), # F#5
            (622, 0.15), # D#5
            (0, 0.05),   # Pause
            (523, 0.1),  # C5
            (1046, 0.1), # C6
            (784, 0.1),  # G5
            (659, 0.1),  # E5
            (1046, 0.08),# C6
            (784, 0.08), # G5
            (659, 0.15), # E5
            (0, 0.05),   # Pause
            (659, 0.06), # E5
            (698, 0.06), # F5
            (784, 0.06), # G5
            (880, 0.06), # A5
            (988, 0.06), # B5
            (1046, 0.25) # C6
        ]
        return self._notes_to_sound(notes)

    def _create_clear_melody(self):
        """Generates a celebratory tune when level is cleared."""
        notes = [
            (523, 0.08), # C5
            (587, 0.08), # D5
            (659, 0.08), # E5
            (698, 0.08), # F5
            (784, 0.12), # G5
            (0, 0.04),
            (784, 0.12), # G5
            (880, 0.15), # A5
            (0, 0.05),
            (1046, 0.3)  # C6
        ]
        return self._notes_to_sound(notes)

    def _notes_to_sound(self, notes):
        """Helper to stitch a list of notes (frequency, duration) into a single Pygame Sound."""
        sample_rate = 22050
        all_samples = []
        
        for freq, duration in notes:
            num_samples = int(sample_rate * duration)
            if freq == 0:
                # Silent pause
                all_samples.extend([0] * num_samples)
                continue
                
            for i in range(num_samples):
                t = i / sample_rate
                # Use a mix of square and sine to create a pleasant chiptune sound
                phase = 2.0 * math.pi * freq * t
                val_square = 1.0 if math.sin(phase) >= 0 else -1.0
                val_sine = math.sin(phase)
                val = 0.7 * val_square + 0.3 * val_sine
                
                # Apply envelope (sharp attack, linear decay to silence)
                envelope = 1.0
                decay_start = int(num_samples * 0.7)
                if i > decay_start:
                    envelope = (num_samples - i) / (num_samples - decay_start)
                    
                sample = int(val * 0.15 * 32767 * envelope)
                all_samples.append(sample)
                
        byte_data = struct.pack(f"{len(all_samples)}h", *all_samples)
        return pygame.mixer.Sound(buffer=byte_data)

    def play(self, name):
        """Plays a pre-generated sound if enabled and initialized."""
        if not self.enabled or not self.mixer_initialized:
            return
            
        sound = self.sounds.get(name)
        if sound:
            # For waka sounds or sirens, don't overlay them excessively
            if name in ["waka1", "waka2"]:
                # Play only if not already playing a waka in channel 0
                ch = pygame.mixer.Channel(0)
                if not ch.get_busy():
                    ch.play(sound)
            elif name == "siren":
                ch = pygame.mixer.Channel(1)
                if not ch.get_busy():
                    ch.play(sound, loops=-1)
            elif name == "intro":
                ch = pygame.mixer.Channel(2)
                ch.play(sound)
            elif name == "clear":
                self.stop_siren()
                ch = pygame.mixer.Channel(2)
                ch.play(sound)
            else:
                # Play other sfx on any free channel
                sound.play()

    def stop_siren(self):
        """Stops the repeating background threat tone."""
        if self.enabled and self.mixer_initialized:
            pygame.mixer.Channel(1).stop()
            
    def stop_all(self):
        """Stops all active audio channels."""
        if self.enabled and self.mixer_initialized:
            pygame.mixer.stop()
