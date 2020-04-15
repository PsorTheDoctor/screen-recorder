import numpy as np
import cv2
from PIL import ImageGrab
import pyautogui
from playsound import playsound
# import pyaudio
# import wave
from tkinter import *
import threading
import datetime

target = 'screen'
is_recorded = False
show_preview = True

seconds = 0
minutes = 0
hours = 0


def update_src():
  global target
  if target == 'screen':
    target = 'cam'
    src_btn['text'] = 'SRC: Camera'
  elif target == 'cam':
    target = 'audio'
    src_btn['text'] = 'SRC: Microphone'
  # else:
  # target = 'screen'
  # src_btn['text'] = 'SRC: Screen'


def update_show_preview():
  global target, show_preview
  # if target != 'audio':
  preview_btn['state'] = NORMAL
  if show_preview:
    show_preview = False
    preview_btn['text'] = "Preview: OFF"
  else:
    show_preview = True
    preview_btn['text'] = "Preview: ON"
  # else:
  #    preview_btn['state'] = DISABLED
  #    preview_btn['text'] = "Preview: OFF"


def update_rec_btn():
  global is_recorded
  if is_recorded:
    # rec_btn['text'] = 'STOP'
    rec_btn['state'] = DISABLED
    msg_label['text'] = 'Press ESC to quit.'
  else:
    # rec_btn['text'] = 'REC'
    rec_btn['state'] = NORMAL


def display_time():
  global is_recorded, seconds, minutes, hours
  if is_recorded:
    if seconds == 60:
      seconds = 0
      minutes += 1
    elif minutes == 60:
      minutes = 0
      hours += 1

    counter_label.config(text=str(hours) + ':' + str(minutes) + ':' + str(seconds))
    seconds += 1
    counter_label.after(1000, display_time)


def reset_time():
  global seconds, minutes, hours
  seconds = 0
  minutes = 0
  hours = 0


def take_screenshot():
  name = 'shot'
  now = datetime.datetime.now()
  date = now.strftime("%H%M%S")
  file_format = 'png'
  filename = name + str(date) + '.' + file_format
  pyautogui.screenshot(filename)
  playsound('camera_shutter_snap.mp3')
  msg_label['text'] = 'Screenshot was saved as ' + filename


"""
def record_audio():
    name = 'audio'
    now = datetime.datetime.now()
    date = now.strftime("%H%M%S")
    file_format = 'wav'
    filename = name+str(date)+'.'+file_format
    audio_format = pyaudio.paInt16
    channels = 2
    rate = 44100
    chunk = 1024
    duration = 5

    audio = pyaudio.PyAudio()
    stream = audio.open(format=audio_format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
    frames = []
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wave_file = wave.open(filename, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(audio.get_sample_size(audio_format))
    wave_file.setframerate(rate)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
"""


def record_screen():
  global show_preview, is_recorded
  name = 'screen'
  now = datetime.datetime.now()
  date = now.strftime("%H%M%S")
  file_format = 'avi'
  filename = name + str(date) + '.' + file_format
  fps = 24
  resolution = (1366, 768)
  thumb_resolution = (342, 192)

  fourcc = cv2.VideoWriter_fourcc(*'XVID')
  writer = cv2.VideoWriter(filename, fourcc, fps, resolution)

  while True:
    img = ImageGrab.grab()
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    writer.write(frame)
    if show_preview:
      thumb = cv2.resize(frame, dsize=thumb_resolution)
      cv2.imshow('Preview - Screen Recorder', thumb)
    if cv2.waitKey(1) == 27:
      is_recorded = False
      msg_label['text'] = 'Video was saved as ' + filename
      update_rec_btn()
      break

  writer.release()
  cv2.destroyAllWindows()


def record_camera():
  global show_preview, is_recorded
  name = 'cam'
  now = datetime.datetime.now()
  date = now.strftime("%H%M%S")
  file_format = 'avi'
  filename = name + str(date) + '.' + file_format
  fps = 24
  thumb_resolution = (342, 192)

  cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print('Unable to open a camera.')

  frame_width = int(cap.get(3))
  frame_height = int(cap.get(4))

  fourcc = cv2.VideoWriter_fourcc(*'MJPG')
  writer = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

  while True:
    ret, frame = cap.read()
    if ret:
      # frame = cv2.cvtColor(cap, cv2.COLOR_BGR2RGB)
      writer.write(frame)
      if show_preview:
        thumb = cv2.resize(frame, dsize=thumb_resolution)
        cv2.imshow('Preview - Camera', thumb)
      if cv2.waitKey(1) == 27:
        is_recorded = False
        msg_label['text'] = 'Video was saved as ' + filename
        update_rec_btn()
        break
    else:
      break

  cap.release()
  writer.release()
  cv2.destroyAllWindows()


def start_recording():
  global is_recorded
  is_recorded = not is_recorded
  reset_time()

  rec_btn_thread = threading.Thread(target=update_rec_btn)
  counter_thread = threading.Thread(target=display_time)
  screen_thread = threading.Thread(target=record_screen)
  cam_thread = threading.Thread(target=record_camera)
  # audio_thread = threading.Thread(target=record_audio)

  if is_recorded:
    rec_btn_thread.start()
    counter_thread.start()
    if target == 'screen':
      screen_thread.start()
    elif target == 'cam':
      cam_thread.start()
    # else:
    # audio_thread.start()


col_width = 14
bg = 'black'
clicked_bg = '#222'
font_color = 'white'
border = 0

window = Tk()
window.title('Screen Recorder')
window.geometry('360x100')
window.resizable(width=False, height=False)
window.configure(bg=bg)

frame = Frame(window)
frame.configure(bg=bg)
frame.pack()

src_btn = Button(frame, text='SRC: Screen', command=update_src,
                 width=col_width, bg=bg, fg=font_color, bd=border,
                 activebackground=clicked_bg, activeforeground=font_color)
src_btn.grid(row=1, column=1)

rec_btn = Button(frame, text='REC', command=start_recording,
                 width=col_width, bg='#e50914', fg=font_color, bd=border,
                 activebackground='#ab070f', activeforeground=font_color)
rec_btn.grid(row=1, column=2)

counter_label = Label(frame, text='0:0:0',
                      width=col_width, bg=bg, fg=font_color)
counter_label.grid(row=1, column=3)

preview_btn = Button(frame, text="Preview: ON", command=update_show_preview,
                     width=col_width, bg=bg, fg=font_color, bd=border,
                     activebackground=clicked_bg, activeforeground=font_color)
preview_btn.grid(row=2, column=1)

shot_btn = Button(frame, text='Take screenshot', command=take_screenshot,
                  width=col_width, bg=bg, fg=font_color, bd=border,
                  activebackground=clicked_bg, activeforeground=font_color)
shot_btn.grid(row=2, column=3)

msg_frame = Frame(window)
msg_frame.configure(bg=bg)
msg_frame.pack()

msg_label = Label(msg_frame, width=3 * col_width, bg=bg, fg=font_color)
msg_label.pack()

window.mainloop()
