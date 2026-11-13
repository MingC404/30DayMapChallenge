"""Antialiased rounded brush layers and local system fonts."""
from pathlib import Path
import gc
import numpy as np
from PIL import Image, ImageFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import LineCollection
SCALE = 1.5


def layer(c, paths, widths, colors):
    """Transparent antialiased path raster. Coordinates and widths are in map pixels."""
    fig=Figure(figsize=(c.w/100,c.h/100),dpi=100*SCALE,facecolor=(0,0,0,0))
    canvas=FigureCanvasAgg(fig)
    ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,c.w); ax.set_ylim(c.h,0); ax.axis('off')
    lc=LineCollection(paths,linewidths=np.asarray(widths)*.72,colors=colors,capstyle='round',joinstyle='round',antialiaseds=True)
    ax.add_collection(lc)
    canvas.draw()
    rgba=Image.fromarray(np.asarray(canvas.buffer_rgba())).resize((c.w,c.h),Image.Resampling.LANCZOS)
    fig.clear()
    canvas.figure=None
    fig.set_canvas(None)
    del lc, ax, canvas, fig
    gc.collect()
    return np.asarray(rgba,dtype=np.float32)/255.


def over(base, rgba, strength=1):
    a=np.clip(rgba[:,:,3:4]*strength,0,1)
    return base*(1-a)+rgba[:,:,:3]*a


def font(size,serif=False,italic=False):
    directory=Path('C:/Windows/Fonts')
    name='georgiai.ttf' if serif and italic else ('georgia.ttf' if serif else 'arial.ttf')
    return ImageFont.truetype(str(directory/name),size)
