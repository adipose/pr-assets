"""Make the flat field clips used to check the nominal range of the DXVA2 VP.

Each clip is one constant Y with neutral chroma, encoded losslessly, so the value that comes
out of the renderer can be compared against a number worked out from the file rather than
against another renderer.

    python make_test_clips.py            # the four clips from the pull request
    python make_test_clips.py --check    # and decode each one back to prove what it holds

The range is tagged on the input as well as the output.  Without that ffmpeg converts between
limited and full on the way in and the clip does not hold what you asked for, which is easy to
miss because the file still looks right.

Needs ffmpeg with libx264 and libx265.
"""
import subprocess
import sys

W, H, FPS, SECS = 1280, 720, 24, 6


def pq_code(pq, full=False):
    """10 bit code value for a PQ signal level, 0..1"""
    return int(round(pq * 1023)) if full else int(round(pq * (940 - 64) + 64))


def make(out, y, depth=10, hdr=True, full=False):
    """One flat field: Y at the given code value, chroma neutral, lossless"""
    mid = 512 if depth == 10 else 128
    if depth == 10:
        frame = y.to_bytes(2, 'little') * (W * H) + mid.to_bytes(2, 'little') * (W * H // 2)
        pix, enc = 'yuv420p10le', 'libx265'
        params = 'colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:lossless=1'
        if not hdr:
            params = 'colorprim=bt709:transfer=bt709:colormatrix=bt709:lossless=1'
        codec = ['-c:v', enc, '-x265-params', params + (':range=full' if full else ':range=limited')]
    else:
        frame = bytes([y]) * (W * H) + bytes([mid]) * (W * H // 2)
        pix = 'yuv420p'
        codec = ['-c:v', 'libx264', '-qp', '0', '-x264-params',
                 'colorprim=bt709:transfer=bt709:colormatrix=bt709' + (':range=pc' if full else ':range=tv')]

    rng = 'pc' if full else 'tv'
    cmd = (['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-f', 'rawvideo', '-pix_fmt', pix, '-s', '%dx%d' % (W, H), '-r', str(FPS),
            '-color_range', rng, '-i', '-']            # tag the input, or it gets converted
           + codec + ['-pix_fmt', pix, '-color_range', rng, out])
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for _ in range(FPS * SECS):
        p.stdin.write(frame)
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit('ffmpeg failed for ' + out)
    print('%-18s Y %4d  %d bit  %s  %s range' % (out, y, depth, 'PQ BT.2020' if hdr else 'BT.709',
                                                 'full' if full else 'limited'))


def check(out, depth):
    """decode the first frame back and print the Y it actually holds"""
    pix = 'yuv420p10le' if depth == 10 else 'yuv420p'
    raw = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', out,
                          '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', pix, '-'],
                         capture_output=True).stdout
    y = int.from_bytes(raw[:2], 'little') if depth == 10 else raw[0]
    print('%-18s holds Y %d' % (out, y))


CLIPS = [
    ('sdr_y128.mkv',  128,                 8,  False),
    ('pq_025.mkv',    pq_code(0.25),      10,  True),
    ('pq_045.mkv',    pq_code(0.45),      10,  True),
    ('pq_065.mkv',    pq_code(0.65),      10,  True),
]

for name, y, depth, hdr in CLIPS:
    make(name, y, depth, hdr)

if '--check' in sys.argv:
    print()
    for name, y, depth, hdr in CLIPS:
        check(name, depth)
