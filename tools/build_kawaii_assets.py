#!/usr/bin/env python3
"""Export the purchased RDBI vector art at Wateru's existing sprite sizes.

Requires Inkscape and Pillow. Run from anywhere; all paths are project-relative.
"""
from pathlib import Path
import csv
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art' / 'kawaii'
SVG = 'http://www.w3.org/2000/svg'
NS = {'s': SVG}
ET.register_namespace('', SVG)

TIERS = [
    ('Cherry', 80),
    ('Blueberry', 100),
    ('PassionFruit', 125),
    ('Kiwi', 140),
    ('Orange', 165),
    ('Peach', 190),
    ('Coconut', 220),
    ('Pineapple', 250),
    ('Honeydew', 270),
    ('Cantaloupe', 300),
    ('WatermelonFull', 330),
]

def make_honeydew():
    """Create one extra fruit by editing the pack's native Cherry vector art."""
    root = ET.parse(SOURCE / 'Cherry.svg').getroot()
    palette = {
        '#d95763': '#bde898',
        '#b34c5a': '#94c56e',
        '#943f4a': '#527d43',
        '#ebab99': '#e6f4bd',
    }
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            for old, new in palette.items():
                value = value.replace(old, new)
            element.set(key, value)
    layer = root.find('s:g', NS)
    # Rind markings stay below the original outline, highlights and face.
    rind = ET.Element(f'{{{SVG}}}g', {
        'id': 'honeydew-rind', 'fill': 'none', 'stroke': '#83b862',
        'stroke-width': '0.55', 'opacity': '0.65',
    })
    for d in [
        'M 23,5 C 8,18 8,48 23,63',
        'M 44,5 C 59,18 59,48 44,63',
        'M 17,9 C 6,22 6,44 17,58',
        'M 50,9 C 61,22 61,44 50,58',
    ]:
        ET.SubElement(rind, f'{{{SVG}}}path', {'d': d})
    layer.insert(2, rind)
    root.set('id', 'honeydew-svg')
    ET.ElementTree(root).write(SOURCE / 'Honeydew.svg', encoding='utf-8', xml_declaration=True)

def recolor(root, palette):
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            for old, new in palette.items(): value = value.replace(old, new)
            element.set(key, value)

def make_golden_watermelon():
    """Whole, striped golden watermelon: no sliced flesh or seeds."""
    root = ET.parse(SOURCE / 'WatermelonFull.svg').getroot()
    recolor(root, {'#75db60':'#ffdc64', '#64b457':'#d8a033', '#bde898':'#fff1ad', '#498c3f':'#a87325',
                   '#8bab39':'#d39c25', '#d3e387':'#fff2b0', '#a1e383':'#fff2b0'})
    root.set('id','golden-watermelon-svg')
    ET.ElementTree(root).write(SOURCE / 'GoldenWatermelon.svg',encoding='utf-8',xml_declaration=True)

def make_cantaloupe():
    root=ET.parse(SOURCE / 'Cherry.svg').getroot()
    recolor(root, {'#d95763':'#e3ba72','#b34c5a':'#c59758','#943f4a':'#8e643b','#ebab99':'#fff0c4'})
    layer=root.find('s:g',NS)
    net=ET.Element(f'{{{SVG}}}g', {'id':'cantaloupe-net','fill':'none','stroke':'#fff0c6','stroke-width':'0.48','opacity':'0.7'})
    # Thin rind netting, bounded inside the fruit outline and behind its face.
    for dx in range(-24,25,6):
        length=(29**2-dx**2)**0.5
        ET.SubElement(net,f'{{{SVG}}}path',{'d':f'M {33.866+dx-length*0.7},{33.866-dx-length*0.7} Q {33.866+dx+1.5},{33.866-dx} {33.866+dx+length*0.7},{33.866-dx+length*0.7}'})
    # Clip the diagonal lines to the circular rind.
    defs=root.find('s:defs',NS)
    clip=ET.SubElement(defs,f'{{{SVG}}}clipPath',{'id':'net-clip'})
    ET.SubElement(clip,f'{{{SVG}}}circle',{'cx':'33.866','cy':'33.866','r':'29.6'})
    net.set('clip-path','url(#net-clip)');layer.insert(2,net)
    root.set('id','cantaloupe-svg')
    ET.ElementTree(root).write(SOURCE / 'Cantaloupe.svg',encoding='utf-8',xml_declaration=True)

def export(source, destination, size, temp):
    # Inkscape's drawing bounds include leaves and any art beyond the page.
    result = subprocess.run(
        ['inkscape', '--query-all', str(source)],
        capture_output=True, text=True, check=True,
    )
    root = ET.parse(source).getroot()
    row = next(line for line in result.stdout.splitlines()
               if line.startswith(root.get('id') + ','))
    x, y, width, height = map(float, row.split(',')[1:])
    view_x, view_y, view_w, view_h = map(float, root.get('viewBox').split())
    px_w = float(root.get('width'))
    px_h = float(root.get('height'))
    # Put the complete drawing in a square, preserving its aspect ratio.
    extent = max(width, height)
    x -= (extent - width) / 2
    y -= (extent - height) / 2
    root.set('viewBox', f'{view_x + x * view_w / px_w} {view_y + y * view_h / px_h} '
                       f'{extent * view_w / px_w} {extent * view_h / px_h}')
    root.set('width', str(size))
    root.set('height', str(size))
    root.set('preserveAspectRatio', 'xMidYMid meet')
    normalized = temp / (destination.stem + '.svg')
    ET.ElementTree(root).write(normalized, encoding='utf-8', xml_declaration=True)
    subprocess.run([
        'inkscape', str(normalized), '--export-area-page',
        '--export-background-opacity=0', f'--export-width={size}',
        f'--export-height={size}', f'--export-filename={destination}',
    ], capture_output=True, text=True, check=True)
    with Image.open(destination) as image:
        assert image.size == (size, size), (destination, image.size)
        assert image.mode == 'RGBA', (destination, image.mode)
        assert image.getchannel('A').getextrema() == (0, 255)

def preview():
    canvas = Image.new('RGB', (1320, 800), '#fff8ec')
    draw = ImageDraw.Draw(canvas)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    def font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            return ImageFont.load_default()
    title = font(bold_path, 32)
    label = font(bold_path, 15)
    note = font(font_path, 16)
    draw.text((36, 23), 'Freaky Fruit Fusion', font=title, fill='#604b37')
    draw.text((36, 69), 'Kawaii fruit progression · pressure squish · smooches · a glowing golden finale',
              font=note, fill='#78614a')
    names = ['Cherry', 'Blueberry', 'Passion fruit', 'Kiwi', 'Orange', 'Peach',
             'Coconut', 'Pineapple', 'Honeydew', 'Cantaloupe', 'Whole watermelon']
    entries = [(f'ball_{i}.png', names[i-1], size) for i, (_, size) in enumerate(TIERS, 1)]
    entries.append(('ball_11f.png', 'Golden watermelon', 330))
    for i, (filename, name, size) in enumerate(entries):
        col, row = i % 6, i // 6
        cell_x, cell_y = col * 220, 112 + row * 329
        with Image.open(ROOT / 'images' / filename) as original:
            image = original.convert('RGBA')
        # Thumbnailing in the preview only; deliverable sprites retain their sizes.
        image.thumbnail((200, 242), Image.Resampling.LANCZOS)
        x = cell_x + (220 - image.width) // 2
        y = cell_y + 242 - image.height
        canvas.paste(image, (x, y), image)
        draw.text((cell_x + 110, cell_y + 254), f'{i+1:02d}  {name}' if i < 11 else name,
                  font=label, fill='#604b37', anchor='mt')
        draw.text((cell_x + 110, cell_y + 281), f'{filename} · {size} × {size}',
                  font=note, fill='#78614a', anchor='mt')
    draw.text((36, 774), 'Whole golden watermelon finale · the halo pulses in-game · no watermelon slices',
              font=note, fill='#78614a')
    canvas.save(ROOT / 'Kawaii_Fruit_Preview.png')

def main():
    make_honeydew()
    make_golden_watermelon()
    make_cantaloupe()
    with tempfile.TemporaryDirectory(prefix='wateru-kawaii-') as directory:
        temp = Path(directory)
        for i, (fruit, size) in enumerate(TIERS, 1):
            export(SOURCE / f'{fruit}.svg', ROOT / 'images' / f'ball_{i}.png', size, temp)
        export(SOURCE / 'GoldenWatermelon.svg', ROOT / 'images' / 'ball_11f.png', 330, temp)
    with (SOURCE / 'mapping.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['game_file', 'source_art', 'width', 'height', 'notes'])
        for i, (fruit, size) in enumerate(TIERS, 1):
            writer.writerow([f'ball_{i}.png', f'{fruit}.svg', size, size,
                             'Adapted from Cherry.svg' if fruit in ('Honeydew', 'Cantaloupe') else 'RDBI original design'])
        writer.writerow(['ball_11f.png', 'GoldenWatermelon.svg', 330, 330, 'Golden adaptation of the whole watermelon'])
    preview()
    print('Exported and checked all 12 transparent PNGs; created preview and mapping.')

if __name__ == '__main__':
    main()
