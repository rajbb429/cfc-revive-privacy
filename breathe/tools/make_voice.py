"""Record the app's voice lines with the Kokoro text-to-speech model (Apache-2.0).

Usage:
  pip install sherpa-onnx lameenc numpy
  python make_voice.py MODEL_DIR lines.json OUT_DIR [voice_id] [speed]

MODEL_DIR is sherpa-onnx's kokoro-int8-en-v0_19 folder (model.int8.onnx, voices.bin,
tokens.txt, espeak-ng-data). lines.json is the list returned by
window.__ribworkVoiceLines() in the app. Voice ids in v0_19: 0 af, 1 af_bella,
2 af_nicole, 3 af_sarah, 4 af_sky, 7 bf_emma, 8 bf_isabella.
"""
import json, re, sys
import numpy as np, sherpa_onnx, lameenc


def slug(text):
    # Must match voiceFile() in index.html.
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', text.lower()))[:80]


def to_mp3(samples, rate, path, kbps=48):
    x = np.asarray(samples, dtype=np.float32)
    nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz):
        x = x[max(0, nz[0] - int(0.03 * rate)): min(len(x), nz[-1] + int(0.12 * rate))]
    f = int(0.01 * rate)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    pcm = (np.clip(x * 0.9, -1, 1) * 32767).astype(np.int16).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps); enc.set_in_sample_rate(rate); enc.set_channels(1); enc.set_quality(2)
    with open(path, 'wb') as fh:
        fh.write(enc.encode(pcm) + enc.flush())


def main():
    model, lines_path, out = sys.argv[1:4]
    sid = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    speed = float(sys.argv[5]) if len(sys.argv) > 5 else 0.88
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=f'{model}/model.int8.onnx', voices=f'{model}/voices.bin',
            tokens=f'{model}/tokens.txt', data_dir=f'{model}/espeak-ng-data'),
        num_threads=4))
    tts = sherpa_onnx.OfflineTts(cfg)
    files = []
    for text in json.load(open(lines_path)):
        name = slug(text) + '.mp3'
        audio = tts.generate(text, sid=sid, speed=speed)
        to_mp3(audio.samples, audio.sample_rate, f'{out}/{name}')
        files.append(name)
        print(name)
    # The service worker precaches everything listed here for offline use.
    json.dump(sorted(files), open(f'{out}/index.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
