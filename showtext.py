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
        small_font.LoadFont("./fonts/nanum9.bdf")
        large_font = graphics.Font()
        large_font.LoadFont("./fonts/nanum18.bdf")
        middle_font = graphics.Font()
        middle_font.LoadFont("./fonts/nanum12.bdf")
        yellow_text = graphics.Color(255, 255, 5)
        green_text = graphics.Color(5, 255, 5)
        red_text = graphics.Color(255, 15, 15)
        pos =int( offscreen_canvas.width/2)
        
        my_text = self.args.text

        wait_txt=['환영합니다.'.encode('utf-8')]
        wait_txt.append('안전운전하세요.'.encode('utf-8'))
        wait_txt.append( '------TOMS------'.encode('utf-8'))

        try_count=0

        line=''
        while True:
            now=time.strftime('%H',time.localtime(time.time()))
            int_now=int(now)
            int_now=6
            if int_now>=5 and int_now<=18:
                a=0
                i=0
                while True:
                    with open('./flagfile/text.txt','r') as f:
                        line=f.readline()
                    if 'wait' in line:
                        offscreen_canvas.Clear()
                        len = graphics.DrawText(offscreen_canvas, middle_font, pos+10, 20, green_text, wait_txt[i])
                        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                        time.sleep(1)
                        a=a+1
                        if a%2==0:
                            i=i+1
                        if a==6:
                            a=0
                            i=0
                    elif 'stop' in line:
                        while True:
                            with open('./flagfile/status.txt','r') as f:
                                line=f.readline()
                            if 'retry' in line:
                                msg='다시시도해주세요'
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, middle_font, pos, 20, yellow_text,msg)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(1)
                            elif 'fail' in line:
                                msg='지정된카드가아닙니다.'
                                msg2='Error...'
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 15, red_text,msg2)
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 25, red_text,msg)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(15)
                                break
                            elif 'success' in line:
                                msgs=line.split(',')
                                msg='차량번호'+msgs[1]
                                msg2='금일:'+msgs[2]
                                msg3='주간:'+msgs[3]
                                msg2=msg2+msg3
                                print('recieved')
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 15, red_text,msg)
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 25, red_text,msg2)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(1)
                                break
                            elif 'timeout' in line:
                                msg='시간초과!!!'
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, middle_font, pos, 20, red_text,msg)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(5)
                                break
                            #time.sleep(1)

                #time.sleep(1)
            else:
                print('sleep texting...')
                time.sleep(60)
# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
