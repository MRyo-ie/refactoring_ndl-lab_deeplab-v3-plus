import base64
import io
import math
import os
import os.path as osp

import numpy as np
import PIL.Image


def get_img_shape(data):
    # labelme の json から、元画像の shape（サイズ）を取得。
    img_b64 = data.get('imageData')
    # if not imageData:
    #     imagePath = os.path.join(os.path.dirname(json_file), data['imagePath'])
    #     with open(imagePath, 'rb') as f:
    #         imageData = f.read()
    #         imageData = base64.b64encode(imageData).decode('utf-8')
    # base64画像を np.array に変換
    img_data = base64.b64decode(img_b64)
    f = io.BytesIO()
    f.write(img_data)
    w, h = PIL.Image.open(f).size
    return w, h


def plot_annt_mask(anntPIL_draw, points, shape_type, lbl_num,
                    line_width=2, point_size=5):
    xy = [tuple(point) for point in points]
    if shape_type == 'circle':
        assert len(xy) == 2, 'Shape of shape_type=circle must have 2 points'
        (cx, cy), (px, py) = xy
        d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
        anntPIL_draw.ellipse([cx - d, cy - d, cx + d, cy + d], outline=1, fill=lbl_num)
    elif shape_type == 'rectangle':
        assert len(xy) == 2, 'Shape of shape_type=rectangle must have 2 points'
        anntPIL_draw.rectangle(xy, outline=1, fill=lbl_num)
    elif shape_type == 'line':
        assert len(xy) == 2, 'Shape of shape_type=line must have 2 points'
        anntPIL_draw.line(xy=xy, fill=lbl_num, width=line_width)
    elif shape_type == 'linestrip':
        anntPIL_draw.line(xy=xy, fill=lbl_num, width=line_width)
    elif shape_type == 'point':
        assert len(xy) == 1, 'Shape of shape_type=point must have 1 points'
        cx, cy = xy[0]
        r = point_size
        anntPIL_draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=1, fill=lbl_num)
    else:
        assert len(xy) > 2, 'Polygon must have points more than 2'
        anntPIL_draw.polygon(xy=xy, outline=1, fill=lbl_num)
