"""Record the app's voice lines in a cloned voice with Chatterbox (MIT licence).

Usage:
  pip install chatterbox-tts faster-whisper lameenc
  python make_voice_clone.py REFERENCE_AUDIO lines.json OUT_DIR

REFERENCE_AUDIO is 10 to 60 seconds of the voice to clone: calm, clear speech in a
quiet room. lines.json is the list returned by window.__ribworkVoiceLines() in the app.

Each line is generated up to three times. Every take is transcribed with Whisper and
the one that says the line best (closest transcript, then the most natural length)
is kept, which catches the occasional garbled or padded take on very short lines.
"""
import difflib, json, re, sys

import lameenc
import numpy as np
import torch
from chatterbox.tts import ChatterboxTTS
from faster_whisper import WhisperModel

TAKES = 3
EXAGGERATION = 0.35  # lower is calmer
CFG_WEIGHT = 0.3     # lower is slower, more deliberate pacing


def slug(text):
    # Must match voiceFile() in index.html.
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', text.lower()))[:80]


def words(text):
    return re.sub(r'[^a-z ]+', '', text.lower()).split()


def trim(x, rate):
    # Cut leading and trailing silence, keep a short tail, fade the edges.
    nz = np.where(np.abs(x) > 0.02 * max(1e-6, np.abs(x).max()))[0]
    if len(nz):
        x = x[max(0, nz[0] - int(0.03 * rate)): min(len(x), nz[-1] + int(0.15 * rate))]
    f = int(0.01 * rate)
    x = x.copy()
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    return x


def to_mp3(x, rate, path, kbps=48):
    peak = np.abs(x).max() or 1.0
    pcm = (np.clip(x / peak * 0.85, -1, 1) * 32767).astype(np.int16).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps); enc.set_in_sample_rate(rate); enc.set_channels(1); enc.set_quality(2)
    with open(path, 'wb') as fh:
        fh.write(enc.encode(pcm) + enc.flush())


def main():
    ref, lines_path, out = sys.argv[1:4]
    torch.manual_seed(7)
    tts = ChatterboxTTS.from_pretrained(device='cpu')
    asr = WhisperModel('base.en', device='cpu', compute_type='int8')
    report, files = [], []
    for text in json.load(open(lines_path)):
        target = words(text)
        best = None
        for take in range(TAKES):
            # A closing full stop keeps very short lines ("Breathe in") from being misread.
            said = text if text.endswith(('.', '?', '!')) else text + '.'
            wav = tts.generate(said, audio_prompt_path=ref, exaggeration=EXAGGERATION, cfg_weight=CFG_WEIGHT)
            x = trim(wav.squeeze(0).numpy().astype(np.float32), tts.sr)
            segs, _ = asr.transcribe(x if tts.sr == 16000 else np.interp(
                np.linspace(0, len(x), int(len(x) * 16000 / tts.sr), endpoint=False), np.arange(len(x)), x).astype(np.float32),
                language='en', beam_size=5)
            heard = ' '.join(s.text for s in segs).strip()
            score = difflib.SequenceMatcher(None, target, words(heard)).ratio()
            secs = len(x) / tts.sr
            # Roughly 0.45 s a word at this pace; penalise takes far longer than that.
            expect = 0.45 * len(target) + 0.5
            key = (round(score, 2), -max(0.0, secs - 1.6 * expect))
            if best is None or key > best[0]:
                best = (key, x, heard, secs)
            if score == 1.0 and secs <= 1.6 * expect:
                break
        name = slug(text) + '.mp3'
        to_mp3(best[1], tts.sr, f'{out}/{name}')
        files.append(name)
        report.append({'line': text, 'heard': best[2], 'match': best[0][0], 'seconds': round(best[3], 2)})
        print(f"{best[0][0]:.2f}  {best[3]:4.1f}s  {text!r} -> {best[2]!r}", flush=True)
    json.dump(sorted(files), open(f'{out}/index.json', 'w'), indent=1)
    json.dump(report, open(f'{out}/report.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
