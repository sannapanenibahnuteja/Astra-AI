"""Dedicated disposable UI fixture for testing Bob's automation, not user apps."""
import json
from pathlib import Path
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
from System.Windows.Forms import Application,Form,TextBox,Button,Timer
from System.Drawing import Point,Size
form=Form();form.Text='Bob Automation Verification';form.Size=Size(500,230)
editor=TextBox();editor.AccessibleName='Editor';editor.Location=Point(20,20);editor.Size=Size(420,80);editor.Multiline=True
button=Button();button.Text='Record';button.Location=Point(20,120)
def record(sender,event):
 Path('.cache/window-fixture-result.json').write_text(json.dumps({'text':editor.Text}))
button.Click += record
form.Controls.Add(editor);form.Controls.Add(button);form.ActiveControl=editor
clock=Timer();clock.Interval=45000
clock.Tick += lambda sender,event:form.Close()
clock.Start();Application.Run(form)
