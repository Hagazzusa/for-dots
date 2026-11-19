"""‘의자를 넣고 나면’ 26초 스테레오 소리를 합성한다."""
from pathlib import Path
import argparse
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
SECONDS = 26
FRICTION = [
    # 시작, 길이, 세기, 이동 전후의 좌우 위치
    (2.30, .64, .078, -.52, -.34),
    (3.10, 1.47, .133, -.34, .19),
    (6.97, .55, .039, .19, .27),
]
CONTACTS = [
    # 시작, 세기, 좌우, 나무 울림의 기준음
    (2.302, .053, -.47, 143.0),
    (4.592, .196, .16, 111.0),
    (4.677, .086, .23, 169.0),
    (7.542, .088, .25, 147.0),
    (11.12, .032, .24, 147.0),
]

def tsec(n):
    return np.arange(n, dtype=np.float64) / SR

def band(x, lo, hi):
    bins = np.fft.rfftfreq(len(x), 1 / SR)
    highpass = bins**2 / (bins**2 + lo**2)
    lowpass = 1 / (1 + (bins / hi)**4)
    y = np.fft.irfft(np.fft.rfft(x) * highpass * lowpass, n=len(x))
    return y / max(np.sqrt(np.mean(y**2)), 1e-12)

def envelope(t, length, rise, fall):
    a = np.clip(t / rise, 0, 1)
    b = np.clip((length - t) / fall, 0, 1)
    return np.sin(np.pi / 2 * a)**2 * np.sin(np.pi / 2 * b)**2

def add(stereo, mono, when, pan):
    i = round(when * SR)
    j = min(len(stereo), i + len(mono))
    if j <= i:
        return
    n = j - i
    angle = (np.asarray(pan) + 1) * np.pi / 4
    if angle.ndim:
        angle = angle[:n]
    stereo[i:j, 0] += mono[:n] * np.cos(angle)
    stereo[i:j, 1] += mono[:n] * np.sin(angle)

def render():
    rng = np.random.default_rng(67104)
    n = SR * SECONDS
    direct = np.zeros((n, 2))
    for when, duration, gain, p0, p1 in FRICTION:
        t = tsec(round(duration * SR))
        u = t / duration
        grain = band(rng.standard_normal(len(t)), 145, 2700)
        bass = band(rng.standard_normal(len(t)), 60, 570)
        rate = 14 * t + 11 * u**2
        chatter = (.35 + .65 * (.5 + .5 * np.sin(2 * np.pi * rate))**2)
        resonator = np.sin(2 * np.pi * (314 * t - 41 * u**2))
        x = (.31 * grain + .12 * bass + .057 * resonator) * chatter
        x *= gain * envelope(t, duration, .05, .063)
        add(direct, x, when, p0 + (p1-p0)*u)

    for when, gain, pan, f in CONTACTS:
        duration = 2.45
        t = tsec(round(duration * SR))
        grain = band(rng.standard_normal(len(t)), 240, 3900)
        x = .38 * grain * np.exp(-t / .013)
        for ratio, amp, tau in [(1,.67,.155),(1.41,.30,.235),
                                 (2.63,.27,.067),(4.19,.12,.044),
                                 (7.83,.069,.021)]:
            x += amp * np.sin(2*np.pi*f*ratio*t) * np.exp(-t/tau)
        x *= gain * envelope(t, duration, .0027, .18)
        add(direct, x, when, pan)

    mix = direct.copy()
    # 벽과 바닥에서 한 번 돌아오는 초기 반사.
    for ms, gain, flip in [(14,.17,False),(27,.125,True),
                           (53,.084,True),(79,.055,False),
                           (111,.031,True)]:
        k = round(ms * SR / 1000)
        mix[k:] += gain * (direct[:-k, ::-1] if flip else direct[:-k])
    # 8초 무렵부터 바닥의 낮은 두 울림이 느리게 엇갈린다.
    t = tsec(SR * 16)
    room = envelope(t, 16, 1.06, .5) * np.exp(-t/4.05)
    add(mix, .0124 * room * np.sin(2*np.pi * (72.9*t + .074*t**2)),
        5.1, -.16)
    add(mix, .0108 * room * np.sin(2*np.pi * (74.15*t - .027*t**2)),
        5.4, .16)
    # 배경의 기척도 마지막에는 남지 않게 한다.
    t = tsec(n)
    air = envelope(t, 25.1, 1.22, 4.2)
    common = band(rng.standard_normal(n), 140, 2450)
    left = band(rng.standard_normal(n), 190, 3100)
    right = band(rng.standard_normal(n), 190, 3100)
    mix[:, 0] += .00175 * air * (.81 * common + .19 * left)
    mix[:, 1] += .00175 * air * (.81 * common + .19 * right)
    mix = np.tanh(mix * 2.7)
    mix *= .69 / np.max(np.abs(mix))
    return np.round(mix * 32767).astype('<i2')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('When-the-Chair-Is-In.mp3'))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as folder:
        pcm = Path(folder) / 'mix.wav'
        with wave.open(str(pcm), 'wb') as fh:
            fh.setparams((2, 2, SR, 0, 'NONE', 'not compressed'))
            fh.writeframes(render().tobytes())
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(pcm),
                        '-map_metadata','-1','-codec:a','libmp3lame',
                        '-b:a','160k','-id3v2_version','0','-write_id3v1','0',
                        str(args.out)], check=True)

if __name__ == '__main__':
    main()
