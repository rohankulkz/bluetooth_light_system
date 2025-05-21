import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import asyncio

freq = 24


class LiveSequence:
    freq = 24

    def __init__(self, device_name="BlackHole 2ch", samplerate=44100, blocksize=1024):
        self.device_name = device_name
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.channels = 1
        self.basstrace = []
        self.superCount = 0
        self.average = 0
        self.pitch = 0

        self.state = "calm"
        self.flash_count = 0
        self.build_count = 0

        self.current_block = np.zeros(self.blocksize)

        self.stream = sd.InputStream(
            device=self.device_name,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self.audio_callback,
        )

        # Prepare plots
        self.fig, (self.ax_wave, self.ax_fft) = plt.subplots(2, 1)

        self.x_wave = np.linspace(0, self.blocksize / self.samplerate, self.blocksize)
        self.line_wave, = self.ax_wave.plot(self.x_wave, np.zeros(self.blocksize))
        self.ax_wave.set_title("Live Audio Waveform")
        self.ax_wave.set_ylim(-1, 1)

        self.x_fft = np.fft.rfftfreq(self.blocksize, d=1 / self.samplerate)
        self.line_fft, = self.ax_fft.semilogx(self.x_fft, np.zeros(len(self.x_fft)))
        self.ax_fft.set_title("Live Audio Spectrum")
        self.ax_fft.set_xlim(20, self.samplerate / 2)
        self.ax_fft.set_ylim(0, 150)

        # Add average line to FFT plot
        self.avg_line = self.ax_fft.axhline(
            y=0, color='green', linestyle='--', linewidth=1, label='Average'
        )

        self.trh_line = self.ax_fft.axhline(
            y=0, color='red', linestyle='--', linewidth=1, label='Threshold'
        )

        self.bonus_line = self.ax_fft.axhline(
            y=0, color='blue', linestyle='--', linewidth=1, label='Bonus'
        )
        self.pitch_line = self.ax_fft.axvline(
            x=0, color='purple', linewidth=1, label="Pitch"
        )


        self.ax_fft.legend()

        plt.ion()  # Turn on interactive mode
        self.fig.show()
        self.fig.canvas.draw()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print("⚠️", status)
        self.current_block = indata[:, 0]  # mono

    async def run(self):
        self.stream.start()
        try:
            while True:
                self.line_wave.set_ydata(self.current_block)

                fft_mag = np.abs(np.fft.rfft(self.current_block))
                self.line_fft.set_ydata(fft_mag)

                # Update average line
                self.avg_line.set_ydata([self.average])
                self.trh_line.set_ydata([self.average + self.threshold])
                self.bonus_line.set_ydata([self.average + self.threshold + self.bonus])
                self.pitch_line.set_xdata([self.pitch])

                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                self.fig.set_facecolor('darkblue')

                self.ax_fft.set_facecolor('darkgray')
                self.ax_wave.set_facecolor('darkgray')# plot area only

                await asyncio.sleep(1 / self.freq)
        except asyncio.CancelledError:
            self.stream.stop()
            plt.close(self.fig)

    # def __next__(self):
    #     window = self.current_block * np.hanning(len(self.current_block))
    #     fft = np.fft.rfft(window)
    #     fff_abs = np.abs(fft)
    #     freqs = np.fft.rfftfreq(len(self.current_block), 1 / self.samplerate)
    #     bass = np.where((freqs >= 0) & (freqs <= 200))[0]
    #     bassAmplitude = np.mean(fff_abs[bass]) if len(bass) > 0 else 0
    #
    #     self.basstrace.append(bassAmplitude)
    #     if len(self.basstrace) > 10:
    #         self.basstrace.pop(0)
    #
    #     self.average = sum(self.basstrace) / len(self.basstrace)
    #
    #     if bassAmplitude > self.average + self.threshhold:
    #         if sum(1 for x in self.basstrace if x > self.average + self.threshhold + self.bonus) >= 5:
    #             return "f eyesore"
    #         if sum(1 for x in self.basstrace if x > self.average + self.threshhold + self.bonus) >= 5:
    #             if self.superCount < self.freq:
    #                 self.superCount += 1
    #                 return "f white"
    #             else:
    #                 self.superCount += 1
    #                 if self.superCount > 2 * self.freq:
    #                     self.superCount = 0
    #                 return "f red"
    #         return 'white'
    #     else:
    #         return 'p red'

    # bonus = 5  # Still fixed for the peak threshold
    #
    # def __next__(self):
    #     # Apply window and compute FFT
    #     windowed = self.current_block * np.hanning(len(self.current_block))
    #     fft = np.fft.rfft(windowed)
    #     magnitude = np.abs(fft)
    #     freqs = np.fft.rfftfreq(len(self.current_block), 1 / self.samplerate)
    #
    #     # Extract bass (20–120 Hz)
    #     bass_indices = np.where((freqs >= 20) & (freqs <= 120))[0]
    #     bass_amplitude = np.mean(magnitude[bass_indices]) if len(bass_indices) > 0 else 0
    #
    #     # Update history
    #     self.basstrace.append(bass_amplitude)
    #     if len(self.basstrace) > 10:
    #         self.basstrace.pop(0)
    #
    #     # Compute average and standard deviation of recent bass
    #     self.average = np.mean(self.basstrace)
    #     std_dev = np.std(self.basstrace)
    #
    #     # Dynamic threshold is 1 standard deviation above average (or tweak as needed)
    #     threshold = std_dev * 0.5
    #     bonus = self.bonus
    #
    #     # Compute intensity relative to baseline
    #     intensity = bass_amplitude - self.average
    #
    #     # Modes
    #     is_peak = intensity > threshold + bonus
    #     is_strong = intensity > threshold
    #     is_normal = intensity > 0
    #
    #     # Cooldown logic
    #     fade_duration = self.freq // 2
    #     max_burst_duration = self.freq * 2
    #
    #     if is_peak:
    #         self.superCount = 0
    #         return "f eyesore"
    #
    #     elif is_strong:
    #         if self.superCount < fade_duration:
    #             self.superCount += 1
    #             return "f white"
    #         else:
    #             self.superCount += 1
    #             if self.superCount > max_burst_duration:
    #                 self.superCount = 0
    #             return "f red"
    #
    #     elif is_normal:
    #         return "p white"
    #     else:
    #         return "p red"

    threshold = 1

    multiplier = 1.0
    multiplier_bonus = 1.3
    bonus = 5

    colors = ['purple', 'cyan',
            'yellow', 'blue', 'green', 'red']

    wait = 100

    def __next__(self):
        # Apply window and compute FFT
        windowed = self.current_block * np.hanning(len(self.current_block))
        fft = np.fft.rfft(windowed)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(self.current_block), 1 / self.samplerate)

        # --- Bass Amplitude ---
        bass_indices = np.where((freqs >= 20) & (freqs <= 200))[0]
        bass_amplitude = np.mean(magnitude[bass_indices]) if len(bass_indices) > 0 else 0

        # --- Track average bass ---
        self.basstrace.append(bass_amplitude)
        if len(self.basstrace) > 20:
            self.basstrace.pop(0)

        self.average = np.mean(self.basstrace)
        std_dev = np.std(self.basstrace)
        self.threshold = self.average + std_dev * self.multiplier
        self.bonus = std_dev * self.multiplier_bonus


        if(bass_amplitude < 0.5 or bass_amplitude < self.average - 9):
            return 'black'

        if(bass_amplitude < 2):
            self.state = 'calm'
            self.build_count = 0

        intensity = bass_amplitude - self.average

        # --- Estimate Pitch from FFT ---
        dominant_index = np.argmax(magnitude[1:]) + 1  # skip DC bin
        dominant_freq = freqs[dominant_index]  # peak freq as pitch estimate

        # Track and smooth pitch
        if not hasattr(self, 'pitchtrace'):
            self.pitchtrace = []

        self.pitchtrace.append(dominant_freq)
        if len(self.pitchtrace) > 20:
            self.pitchtrace.pop(0)

        self.pitch = np.mean(self.pitchtrace)  # average pitch in Hz

        # print(self.pitch)

        color = "red"

        if(self.pitchtrace[len(self.pitchtrace)-1] < 100):
            if(self.pitchtrace[len(self.pitchtrace)-1] < 70):
                return 'f red'
            color = 'red'
        elif(self.pitch < 200):
            color = 'purple'
        elif(self.pitch < 300):
            color = 'blue'
        else:
            color = 'cyan'

        # --- State machine begins ---
        if self.state == "calm":
            if intensity > self.threshold * 0.5:
                self.state = "build"
                self.build_count = 0
                return "p white"
            return "p " + color

        elif self.state == "build":
            self.build_count += 1
            if intensity > self.threshold + self.bonus:
                self.state = "flash"
                self.flash_count = 0
                return "white"
            # Gradually brighten as we build up
            if self.build_count < self.wait*1:
                return "p white"
            elif self.build_count < self.wait*2:
                return "p " + color
            elif self.build_count < self.wait*2.3:
                return "f white"
            else:
                if(self.build_count > self.wait*2.6):
                    self.build_count = self.wait * 2 + 1
                return "f " + color

        elif self.state == "flash":

            self.flash_count += 1

            if(self.flash_count < 1):
                # print("black")
                return "black"
            if(self.flash_count < 3):
                return "white"
            else:
                self.state = "strobe"
                self.superCount = 0
                return "f eyesore"

        elif self.state == "strobe":
            self.superCount += 1
            if self.superCount < self.freq:
                return "f " + color if self.superCount % 2 == 0 else "f " + color
            else:
                self.superCount = 0
                if(intensity < self.bonus + self.threshold + 1 or self.superCount > 100):
                    self.state = "calm"
                return "p " + color
        print("bad")
        return "p " + color
