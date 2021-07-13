import os,sys

def show_text(txt):
    if txt=='wait':
        cmd='sudo python showtext.py -t wait --led-cols 64'
        os.system(cmd)
    elif 'grant' in txt:
        cmd3='sudo python grant_text.py -t '+txt+' --led-cols 64'
        os.system(cmd3)
    else:
        cmd2='sudo python short_text.py -t '+txt+' --led-cols 64'
        os.system(cmd2)

show_text('wait')
