# kim (10-21): show more of 김햇살 and 류상화, like the 정예린 photo. The studio portraits are narrower than a 3:2 card,
# so the plain backdrop is continued to the sides: each new column repeats the photo's own edge colour row by row
# (smoothed, with a little grain), and the photo itself, the person included, is left exactly as it was.
import sys
import numpy as np
from PIL import Image, ImageFilter

def extend(src, top, bottom, out, size=(600, 400), seed=1):
    im = Image.open(src).convert('RGB')
    W, H = im.size
    a = np.asarray(im.crop((0, top, W, bottom))).astype(np.float32)
    h = bottom - top
    nw = round(h * 1.5)
    pad = (nw - W) // 2
    def edge(cols):
        e = a[:, cols, :].mean(axis=1)
        k = np.exp(-0.5 * (np.arange(-24, 25) / 8.0) ** 2); k /= k.sum()
        return np.stack([np.convolve(np.pad(e[:, c], 24, mode='edge'), k, mode='valid') for c in range(3)], axis=1)
    L, R = edge(slice(1, 9)), edge(slice(W - 9, W - 1))
    # grain like the photo's own: the spread of the backdrop pixels around their smoothed colour
    g = float(np.std(a[:, 1:9, :] - L[:, None, :]))
    rng = np.random.default_rng(seed)
    o = np.empty((h, nw, 3), np.float32)
    o[:, :pad] = L[:, None, :]
    o[:, pad + W:] = R[:, None, :]
    o[:, :pad] += rng.normal(0, g, (h, pad, 3))
    o[:, pad + W:] += rng.normal(0, g, (h, nw - pad - W, 3))
    o[:, pad:pad + W] = a
    # soften the seam over a few columns of backdrop on each side of the join
    for i in range(6):
        t = (i + 1) / 7
        o[:, pad + i] = a[:, i] * t + L * (1 - t)
        o[:, pad + W - 1 - i] = a[:, W - 1 - i] * t + R * (1 - t)
    img = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    img.save(out, quality=86, progressive=True, optimize=True)
    print(out, 'from', (0, top, W, bottom), 'canvas', (nw, h), 'pad', pad, 'grain', round(g, 2))

if __name__ == '__main__':
    up = '/root/.claude/uploads/3f27ac15-0e97-50b1-9036-1e65c4005757/'
    extend(up + '579b42c1-image.png', 0, 600, 'ks-wide.jpg')
    extend(up + '0c1a31c3-image.png', 0, 900, 'nbn-wide-a.jpg')
    extend(up + '0c1a31c3-image.png', 10, 810, 'nbn-wide-b.jpg')
