from dataclasses import dataclass
import threading
import subprocess
import tempfile
import time
import os
import sys
from datetime import datetime
from pathlib import Path

import pymel.core as pc

from cg3.util.ports import open_port


class SubQ:
    """
    A class to run commandline processes from Maya.
    The added commands will not run in parallel but one after another.
    This enables the commands to use generated files from their predecessors.
    For Example:
    Render an image sequence via Mayabatch and then convert it to mp4 via ffmpeg.

    The command strings have to be properly escaped and executable by the OS.
    'echo test1 >> "E:\\folder with spaces\\test1.txt"'
    There will be no checks concerning the added commands but errors will be logged.

    Usage:
    sq = SubQ()
    sq.add('Render -s 1 -e 10 -pad 4 -r hw2 -rd E:\\images -im test')
    sq.add('ffmpeg -r 25 -crf 25 -i test.%04d.png test.mp4')
    sq.run()
    """
    def __init__(self, error_log=None):
        self.q = []
        self.error_log = error_log if error_log is not None else tempfile.mkstemp(
            prefix="SubQ_ERROR_", suffix=".log"
        )[-1]
        self.port = 2345
        open_port(self.port)
        self.mayapy = Path(sys.executable).parent / "mayapy"

    def add(self, cmd):
        """Add a command string to the queue."""
        self.q.append(cmd)

    def run(self):
        with open(self.error_log, "w") as log:
            log.write(f"Started: {time.ctime()}\n")
        print(f"Sub Process started. Queue length: {len(self.q)}")
        print(f"Errors will be logged to '{self.error_log}'")
        t = threading.Thread(target=self.get_process_function())
        t.daemon = True
        t.start()

    def get_cmds(self):
        return ' && '.join(self.q)

    def get_process_function(self):
        def process():
            with open(self.error_log, "a") as log:
                subprocess.check_call(
                    self.get_cmds(), shell=True, stderr=log
                )
        return process

    def reset(self):
        self.q = []

    def add_message(self, message):        
        cmd = f"\"{self.mayapy}\" -c \"import socket;s=socket.socket(socket.AF_INET, socket.SOCK_STREAM);s.connect(('localhost', {self.port}));s.send(b'import pymel.core as pc;pc.warning(\\'{message}\\')');s.close()\""
        self.add(cmd)

    def length(self):
        return len(self.q)


class DrawText:
    """
    Convenience class for ffmpeg drawtext function
    Possible alignment values are "left", "center", "right"
    """

    def __init__(self, alignment="left"):
        self.text_padding = 26
        self.start_number = 1
        self.text = []
        self.alignment = alignment
        self.same_width = True

        self.box_opacity = 0.35
        self.text_flags = {
            "fontsize": 18,
            "fontcolor": "black@1.0",
            "fontfile": "",
            "box": 1,
            "boxcolor": f"white@{self.box_opacity}",
            "boxborderw": 4
        }
        self.set_font("InputMonoCompressed-Thin.ttf")

    def set_font(self, filename):
        f = str(Path(__file__).parent / "fonts" / filename).replace("\\", "/").replace(":", r"\:")
        self.text_flags["fontfile"] = f"'{f}'"

    def get_x(self):
        if self.alignment == "center":
            return ':x=(w-text_w)/2'
        elif self.alignment == "right":
            return f':x=w-text_w-{self.text_padding}'
        else:
            return f':x={self.text_padding}'

    def get_y(self, i):
        if self.alignment == "center":
            return f':y=(h)-{self.text_padding * i}'
        elif self.alignment == "right":
            return f':y=(h)-{self.text_padding * i}'
        else:
            return f':y=(h)-{self.text_padding * i}'

    def get_drawtext(self):
        drawtext = []
        for i, t in enumerate(reversed(self.text), 1):
            dt = f"drawtext={':'.join([f'{k}={v}' for k, v in self.text_flags.items()])}"
            if "<frame>" in t.lower():
                t = t.replace("<frame>", "%{frame_num}")
                dt += f":start_number={self.start_number}"
            elif "<datetime>" in t.lower():
                timetext = "{0:%d.%m.%Y - %H:%M}".format(datetime.now())
                t = t.replace("<datetime>", timetext)
            t = t.replace(":", "\\\\:")
            dt += f":text={t}"
            dt += self.get_x()
            dt += self.get_y(i)
            drawtext.append(dt)
        return ','.join(drawtext)
    
    def append(self, t):
        self.text.append(t)


class Ffmpeg:
    """
    Super light wrapper to get valid ffmpeg commandlines for class SubQ.
    """
    def __init__(self, i=None, o=None, framerate=24, quality=25, exe=""):
        self.input_flags = {"-y": ""}
        self.output_flags = {}
        self.input = i
        self.output = o
        self.framerate = framerate
        self.quality = quality
        self.set_exe(exe)
        self.output_flags["-pix_fmt"] = "yuv420p"
        self.output_flags["-vcodec"] = "libx264"

        self.text = {
            "left": DrawText("left"),
            "center": DrawText("center"),
            "right": DrawText("right")
        }

    @property
    def framerate(self):
        return self.output_flags["-framerate"]

    @framerate.setter
    def framerate(self, f):
        try:
            f = int(f)
        except ValueError:
            return
        if f > 0:
            self.output_flags["-framerate"] = f
    
    @property
    def quality(self):
        return self.output_flags["-crf"]

    @quality.setter
    def quality(self, f):
        try:
            f = int(f)
        except ValueError:
            return
        if f > 0:
            self.output_flags["-crf"] = f

    @property
    def input(self):
        return self.__input
        
    @input.setter
    def input(self, i):
        if i:
            i = os.path.normpath(i)
            self.__input = i if " " not in i else f'"{i}"'

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, o):
        if o:
            o = os.path.normpath(o)
            self.__output = o if " " not in o else f'"{o}"'

    def set_exe(self, exe=""):
        if exe:
            exe = Path(exe)
        elif os.environ.get("ffmpeg", False):
            exe = Path(os.environ.get("ffmpeg"))
        self.exe = exe if " " not in str(exe) else f"\"{exe}\""

    def get_drawtext(self):
        drawtext = []
        for dt in self.text.values():
            d = dt.get_drawtext()
            if d:
                drawtext.append(d)
        if drawtext:
            return f"\"[in]{','.join(drawtext)}[out]\""

    def cmd(self):
        input_flags = " ".join([f"{k} {v}" for k, v in self.input_flags.items()])
        drawtext = self.get_drawtext()
        if drawtext:
            self.output_flags["-vf"] = drawtext
        output_flags = " ".join([f"{k} {v}" for k, v in self.output_flags.items()])
        
        return f"{self.exe} {input_flags} -i {self.input} {output_flags} {self.output}"


@dataclass
class RenderFlag:
    flag: str
    value: str
    label: str
    ui: str = ""

    def __str__(self):
        f = self.flag
        d = self.delimiter()
        v = self.get_value()
        return f"{f} {d}{v}{d}" if v else ""

    def get_value(self):
        return self.value

    def delimiter(self):
        return "" if isinstance(self.value, (int, float)) else '"'


class HW2PreRenderMel():
    def __init__(self, aa_enable=1, aa_samples=8, ao_enable=0, ao_amount=1,
                 ao_radius=16, ao_filter=16, ao_samples=16, mb_enable=0):
        self.attrs = {
            "multiSampleEnable": aa_enable,
            "multiSampleCount": aa_samples,
            "ssaoEnable": ao_enable,
            "ssaoAmount": ao_amount,
            "ssaoRadius": ao_radius,
            "ssaoFilterRadius": ao_filter,
            "ssaoSamples": ao_samples,
            "motionBlurEnable": mb_enable
        }

    def get_mel(self):
        res = ""
        for k, v in self.attrs.items():
            if v is not None:
                res += f'setAttr \\"hardwareRenderingGlobals.{k}\\" {v};'
        return res


class BatchRender:
    def __init__(self, scene=None, image_name=None, rd=None, s=1, e=10, b=1,
                 r="hw2", p=4, cam=None, x=960, y=540, of="png"):
        self.renderexe = Path(sys.executable).parent / "Render"
        scene_name = Path(pc.system.sceneName())
        self.scene = scene or scene_name
        if image_name is None:
            if scene_name:
                image_name = pc.system.sceneName().name.split(".")[-2]
        if rd is None:
            ws = pc.system.Workspace()
            rd = Path(ws.getPath()) / ws.fileRules["images"]
        self.flags = [
            RenderFlag("-s", s, "Start Frame"),
            RenderFlag("-e", e, "End Frame"),
            RenderFlag("-b", b, "Step"),
            RenderFlag("-r", r, "Renderer"),
            RenderFlag("-x", x, "Resolution X"),
            RenderFlag("-y", y, "Resolution Y"),
            RenderFlag("-cam", cam, "Render Camera"),
            RenderFlag("-im", image_name, "Image Name"),
            RenderFlag("-pad", p, "Padding Zeros"),
            RenderFlag("-rd", rd, "Render to"),
            RenderFlag("-of", of, "File Format"),
            
        ]

    def cmd(self):
        return f'"{self.renderexe}" {" ".join([str(f) for f in self.flags if f is not None])} "{self.scene}"'
        
"""
from cg3.util.process import SubQ, Ffmpeg, BatchRender

sq = SubQ()

br = BatchRender(e=100)

ff = Ffmpeg(exe="C:/Program Files/ffmpeg/bin/ffmpeg.exe")

ff.input = "F:/mayaProjects/studi_help/images/rotating_cube.%04d.png"
ff.output = f"F:/rotating_cube_hw.mp4"
ff.quality = 15
ff.text["left"].append("Crazy Show")
ff.text["left"].append(pc.system.sceneName())
ff.text["left"].append("datetime")
ff.text["right"].append("Cam: Shotcam2")
ff.text["right"].append("frame")

sq.add(br.cmd())
sq.add_message("Rendering finished.")
sq.add(ff.cmd())
sq.add_message("Encoding finished.")

sq.run()
"""
