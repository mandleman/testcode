#coding:utf-8
#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time


class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        data='안녕하세요abcdef'
        udata=data.decode('utf-8')
        asciidata=udata.encode('ascii','ignore')
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default=asciidata)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        small_font = graphics.Font()
        small_font.LoadFont("../../../fonts/nanum9.bdf")
        large_font = graphics.Font()
        large_font.LoadFont("../../../fonts/nanum18.bdf")
        textColor = graphics.Color(255, 0, 0)
        pos = offscreen_canvas.width
        my_text = self.args.text

        wait_txt=['탐스에오신걸환영합니다.'.encode('utf-8')]
        wait_txt.append('안전운전하세요.'.encode('utf-8'))
        wait_txt.append( 'TOMS'.encode('utf-8'))
        a=0
        i=0
        while True: 
                    offscreen_canvas.Clear()
                    len = graphics.DrawText(offscreen_canvas, large_font, pos, 25, textColor, my_text)
                    pos =pos-10
                    if (pos + len < 0):
                        a=a+1
                        if a%2==0:
                            i=i+1
                        pos = offscreen_canvas.width
                    time.sleep(0.1)
                    offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                    if a==2:
                        break
               

# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
