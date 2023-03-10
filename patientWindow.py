import sys
import tkinter
import tkinter as tk

import threading
from doctest import master

from psychopy import monitors, __all__, visual
from psychopy.visual import helpers
from screeninfo import get_monitors

from datetime import timedelta
import GSR_rec
import ScreenRecording
import eyeTracker
# import eyeTrackerV
import ffmpeg
import ffmpeg_video_audio
# import videoPlayer as vp
from tkinter import *
import openpyxl, xlrd
from openpyxl import Workbook
import pathlib
from tkinter import messagebox, filedialog
from tkinter import ttk
import eyeTracker as ey
import os
import csv
import json
# import WebsiteExperiment
from PIL import Image, ImageTk
#import Xlsxwriter

mydata = []

# from PyQt5.QtWebEngineWidgets import QWebEngineView
from GSR.GSR_RECORD_SIGNAL import gsr_thread_record


class PatientWindow():
    def __init__(self, parent, id, name=None, surname=None, video_source=0):
        self.frame1 = None
        self.next_image = None
        self.name = name
        self.surname = surname
        self.participantId = id
        self.count_number = 0
        self.images_list = []
        self.surques = 0
        self.after_id = None
        self.imag_exp = 0
        self.web_exp = 0
        self.video_ep = 0
        self.time_conversion = None
        self.parent = parent  # window
        self.widgets = self.addWidgets()
        self.settings = None  # possible settings : 'lab' or 'home'

        self.frame = None  # to enable lab setting frame in the experiment
        self.camera_on = False
        self.experiment = False
        self.timer = 0

    def add_webcam_frame(self):
        top = Toplevel()
        top.title("Webcam output")
        top.geometry("600x600")
        Label(top, text=' Webcam ', font='Times 25').grid(row=1, column=3, pady=40)

    def browseFiles(self):
        self.no_participant1.config(text="Mark is our friend!")

    def export(self):
        if len(mydata) < 1:
            messagebox.showerror("No Data available to export")
            return False

        fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save CSV",
                                           filetypes=(("CSV File", "*.csv"), ("All Files", "*.*")))
        with open(fln, mode='w') as myfile:
            exp_writer = csv.writer(myfile, delimiter=',')
            for i in mydata:
                exp_writer.writerow()

        messagebox.showinfo("Data Exported",
                            "Your data has been exported to " + os.path.basename(fln) + "successfully.")

    def addWidgets(self, neuro_frame=None):
        widgets = []
        style = ttk.Style()
        style.configure('Wild.TButton', background="white")
        style.map('Wild.TButton', background=[('disabled', 'yellow'), ('pressed', 'red')])
        var = tk.IntVar()
        self.x = IntVar()
        self.x.set(0)

        experiments_frame = ttk.LabelFrame(self.parent)
        experiments_frame.columnconfigure(1, weight=1)

        experiments_frame.grid(row=1, column=1, pady=3, padx=50, sticky=tk.E + tk.W + tk.N + tk.S)
        ttk.Label(experiments_frame, text="Participant " + self.participantId, font='Times 18').grid(row=0, column=1)

        but_frame = ttk.LabelFrame(self.parent)
        but_frame.columnconfigure(2, weight=1)

        but_frame.grid(row=1, column=2, pady=1, padx=50, sticky=tk.E + tk.W + tk.N + tk.S)

        start_camera_button = ttk.Button(but_frame, command=self.start_camera, text="Start Recording")
        start_camera_button.grid(row=0, column=1, pady=10)

        stop_camera = ttk.Button(but_frame, command=self.stop_cam, text="Stop Recording")
        stop_camera.grid(row=1, column=1, pady=10)

        angraphic = ttk.Button(but_frame, command=self.show_anagraphic, text="Show Anagraphic")
        angraphic.grid(row=2, column=1, pady=100)

        self.lab_button = ttk.Radiobutton(but_frame, text="Switch to Lab Settings", command=self.switch_lab,
                                          variable=var, value=1)
        self.lab_button.grid(row=4, column=1)

        self.home_button = ttk.Radiobutton(but_frame, text="Switch to Home Settings",
                                           command=self.switch_home, variable=var, value=2)
        self.home_button.grid(row=5, column=1)

        widgets.append(experiments_frame)

        neuro_frame = ttk.LabelFrame(experiments_frame, text="Experiments", relief=tk.RIDGE)
        neuro_frame.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=30, pady=15)

        button1 = ttk.Button(neuro_frame, text="Image Experiment", command=self.run_expimage)
        button1.grid(row=1, column=1, pady=15)
        """button2 = ttk.Button(neuro_frame, text="Video Experiment", command=self.run_expvideo)
        button2.grid(row=2, column=1, pady=15)
        button3 = ttk.Button(neuro_frame, text="Browser Experiment", command=self.openfile)
        button3.grid(row=3, column=1, pady=15)"""
        neuro_frame.columnconfigure(1, weight=1)
        self.no_participant1 = ttk.Label(neuro_frame, text="Please select one mode of settings!", font='Times 18')
        self.no_participant1.grid(row=4, column=1, padx=30, pady=20)

        show_data_but = ttk.Button(experiments_frame, text="Mark", command=self.browseFiles)
        show_data_but.grid(row=2, column=1, pady=10)

        export_data_but = ttk.Button(experiments_frame, text="Export Data", command=self.export)
        export_data_but.grid(row=3, column=1, pady=10)

        del_data_but = ttk.Button(experiments_frame, text="Delete data", command=self.delete_data)
        del_data_but.grid(row=4, column=1, pady=10)

        widgets.extend([neuro_frame, button1, show_data_but])

        return widgets

    def stop_cam(self):
        ffmpeg.stop()

    def delete_data(self):
        print("data has been deleted!")
        path = filedialog.askopenfilename(initialdir=os.getcwd() + "/data/")

    def openfile(self):
        # self.web_exp = 1
        if (self.settings == 'lab') | (self.settings == 'home'):
            self.root = Tk()
            self.root.title("Enter URL")
            self.root.geometry("800x800")
            '''
            fp = open('ffmpeg.txt', 'r')
            self.reso = json.load(fp)
            fp.close()
            self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry('%sx%s+%s+%s' % (self.reso['tobii_width'], self.reso['tobii_hight'], -self.sw + self.reso['screen_shift'], 0))
            '''
            fp = open('websites.txt', 'r')
            self.websites = json.load(fp)
            fp.close()

            Label(self.root, text="Select Experiment", font='Times 16').grid(row=5, column=1, pady=20)

            Button(self.root, text="web1", command=self.run_websiteExp).grid(row=7, column=1, padx=10, pady=20)
            Button(self.root, text="web2", command=self.run_websiteExp).grid(row=8, column=1, padx=10, pady=20)
            Button(self.root, text="web3", command=self.run_websiteExp).grid(row=9, column=1, padx=10, pady=20)
            Button(self.root, text="web4", command=self.run_websiteExp).grid(row=10, column=1, padx=10, pady=20)

            Label(self.root, text=self.websites['website1'], font='Times 14').grid(row=7, column=2, pady=20)
            Label(self.root, text=self.websites['website2'], font='Times 14').grid(row=8, column=2, pady=20)
            Label(self.root, text=self.websites['website3'], font='Times 14').grid(row=9, column=2, pady=20)
            Label(self.root, text=self.websites['website4'], font='Times 14').grid(row=10, column=2, pady=20)
            Label(self.root, text="To change website configuration please edit 'websites.txt' file",
                  font='Times 16').grid(row=12, column=2, pady=20)

            def on_closing():
                self.root.destroy()

            close_but = Button(self.root, text="Close", command=on_closing)
            close_but.grid(row=13, column=2, padx=10, pady=20)

            self.parent.columnconfigure(6)
            self.parent.bind("<Return>", lambda e: self.web1())
        else:
            self.no_participant1.config(text="No mode selected!")

        self.finish = Label(self.root, text="", font='Times 14')
        self.finish.grid(row=11, column=2, pady=20)

    """def run_websiteExp(self):
        self.experiment = True

        if self.settings == "lab":
            labExp = ey.run_browser_experiment(os.getcwd() + self.websites['website5'], 1, self.participantId, self.parent,
                                               self.root, True)
            labExp.runexpweb()
        elif self.settings == "home":

            WebsiteExperiment.launch_browser(os.getcwd() + self.websites['website5'], 1, self.participantId,
                                             self.root, self.settings, False)
        else:
            self.no_participant1.config(text="No mode selected!")"""

    # -------------------------------------Image Experiment-------------------------------------------

    def run_expimage(self):
        if self.settings == "lab":
            """
            if self.camera_on is False:
                print("You need to turn the camera on")
            else:
                eyeTracker.runexpImage(self.participantId)
                os.startfile(
                    "https://docs.google.com/forms/d/e/1FAIpQLSfZ89WXRbBi00SrtwIb7W_FLGMzkd9IkS8Ot5McfHF137sCqA/viewform")"""

            ey.runexpImage(self.participantId)
            os.startfile(
                "https://docs.google.com/forms/d/e/1FAIpQLSfZ89WXRbBi00SrtwIb7W_FLGMzkd9IkS8Ot5McfHF137sCqA/viewform")

        elif self.settings == "home":
            self.inst_win = Toplevel()
            self.inst_win.title("Instruction")
            self.inst_win.attributes('-fullscreen', True)

            fp = open('ffmpeg.txt', 'r')
            self.reso = json.load(fp)
            fp.close()

            img_5 = ImageTk.PhotoImage(master=self.inst_win, image=Image.open(os.getcwd() + '/Instructions.png'))
            tk.Label(self.inst_win, image=img_5).pack()

            ttk.Button(self.inst_win, text="Start Experiment!", command=self.start_image_exp).pack()

            self.inst_win.mainloop()
            os.startfile(
                "https://docs.google.com/forms/d/e/1FAIpQLSfZ89WXRbBi00SrtwIb7W_FLGMzkd9IkS8Ot5McfHF137sCqA/viewform")

        else:
            self.no_participant1.config(text="No mode selected!")

    def countdown(self, remaining=None):
        if remaining is not None:
            self.remaining = remaining

        if self.remaining <= 0:
            self.chronometer.configure(text="time's up!")
        else:
            self.chronometer.configure(text="remaining %d" % self.remaining)
            self.remaining = self.remaining - 1
            self.top.after(1000, self.countdown)

    def start_image_exp(self):

        self.inst_win.destroy()
        self.top = Toplevel()
        self.top.title("Image Experiment")
        self.top.geometry("1500x1500")
        self.top.attributes('-fullscreen', True)

        frame_1 = tk.Frame(self.top)
        frame_1.columnconfigure(0, weight=1)
        frame_1.pack()

        fp1 = open('Images.txt', 'r')
        counts = json.load(fp1)
        fp1.close()

        durations = [int(counts['count_1']), int(counts['count_2']), int(counts['count_3']), int(counts['count_4'])]
        total_duration = sum(durations)
        self.time_conversion = str(timedelta(seconds=total_duration))

        (h, m, s) = self.time_conversion.split(':')
        duration_result = int(h) * 3600 + int(m) * 60 + int(s)

        self.chronometer = tk.Label(frame_1, text=" ", width=20)
        self.chronometer.grid(row=0, column=2)
        self.remaining = 0
        self.countdown(duration_result)

        frame_2 = ttk.Frame(self.top)
        frame_2.columnconfigure(1, weight=2)
        frame_2.pack()

        cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording, args=(self.participantId, 1, 0, False,
                                                                                  self.time_conversion))
        cam1.start()
        sc = threading.Thread(target=ScreenRecording.ScreenRec,
                              args=(self.participantId, 1, 0, False, self.time_conversion))

        sc.start()

        directory = os.getcwd() + '/Image'

        for image_file in os.listdir(directory):
            image_path = os.path.join(directory, image_file)
            image_show = Image.open(image_path)
            image_show = image_show.resize((1000, 600), Image.ANTIALIAS)
            image_PIL = ImageTk.PhotoImage(master=frame_2, image=image_show)
            self.images_list.append(image_PIL)

        label1 = tk.Label(frame_2, image=self.images_list[self.count_number])
        label1.pack()



        # transition of images based on the user defined count timer
        def img_count(count):
            if count == 0:
                self.top.after_cancel(self.after_id)
                self.count_number += 1
                label1.config(image=self.images_list[self.count_number])
                iterateCounter(self.count_number)
            else:
                self.after_id = self.top.after(2000, img_count, count - 1)

        def sur_count(count):
            if count == 0:
                self.top.after_cancel(self.after_id)
                self.count_number += 1
                label1.after_idle(survey)
                iterateCounter(self.count_number)
            else:
                self.after_id = self.top.after(4000, sur_count, count - 1)

        def iterateCounter(count_number):
            if count_number == 0:
                #img_count(int(durations[0]))
                sur_count(int(durations[0]))
            if count_number == 1:
                #img_count(int(durations[1]))
                sur_count(int(durations[1]))
            if count_number == 2:
                #img_count(int(durations[2]))
                sur_count(int(durations[2]))
            if count_number == 3:
                #img_count(int(durations[3]))
                sur_count(int(durations[3]))
            if count_number == 4:
                self.top.destroy()

        # iterate the individual counters based on the user defined count timers
        iterateCounter(self.count_number)

        def survey():

            self.sur_frame = Toplevel()
            self.sur_frame.title("Survey")
            self.sur_frame.geometry("1500x1500")
            self.sur_frame.attributes('-fullscreen', True)



            ra = IntVar()
            rb = IntVar()
            rc = IntVar()
            rd = IntVar()
            re = IntVar()
            rf = IntVar()
            rg = IntVar()
            rh = IntVar()
            ri = IntVar()
            rj = IntVar()
            rk = IntVar()

            def click(value):
                Label1 = Label(self.sur_frame, text=value)
                Label1.config(text=ra.get())
                Label1.pack()

                Label2 = Label(self.sur_frame, text=value)
                Label2.config(text=rb.get())
                Label2.pack()

                Label3 = Label(self.sur_frame, text=value)
                Label3.config(text=rc.get())
                Label3.pack()

                Label4 = Label(self.sur_frame, text=value)
                Label4.config(text=rd.get())
                Label4.pack()

                Label5 = Label(self.sur_frame, text=value)
                Label5.config(text=re.get())
                Label5.pack()

                Label6 = Label(self.sur_frame, text=value)
                Label6.config(text=rf.get())
                Label6.pack()

                Label7 = Label(self.sur_frame, text=value)
                Label7.config(text=rg.get())
                Label7.pack()

                Label8 = Label(self.sur_frame, text=value)
                Label8.config(text=rh.get())
                Label8.pack()

                Label9 = Label(self.sur_frame, text=value)
                Label9.config(text=ri.get())
                Label9.pack()

                Label10 = Label(self.sur_frame, text=value)
                Label10.config(text=rj.get())
                Label10.pack()

                Label11 = Label(self.sur_frame, text=value)
                Label11.config(text=rk.get())
                Label11.pack()

                xa = ra.get()
                xb = rb.get()
                xc = rc.get()
                xd = rd.get()
                xe = re.get()
                xf = rf.get()
                xg = rg.get()
                xh = rh.get()
                xi = ri.get()
                xj = rj.get()
                xk = rk.get()

            for i in range(10):
                self.sur_frame.columnconfigure(0 + i, weight=1)

            ttk.Label(self.sur_frame, text="1", font=('Times New Roman', 20)).grid(row=0, column=1)
            ttk.Label(self.sur_frame, text="2", font=('Times New Roman', 20)).grid(row=0, column=2)
            ttk.Label(self.sur_frame, text="3", font=('Times New Roman', 20)).grid(row=0, column=3)
            ttk.Label(self.sur_frame, text="4", font=('Times New Roman', 20)).grid(row=0, column=4)
            ttk.Label(self.sur_frame, text="5", font=('Times New Roman', 20)).grid(row=0, column=5)
            ttk.Label(self.sur_frame, text="6", font=('Times New Roman', 20)).grid(row=0, column=6)
            ttk.Label(self.sur_frame, text="7", font=('Times New Roman', 20)).grid(row=0, column=7)
            ttk.Label(self.sur_frame, text="8", font=('Times New Roman', 20)).grid(row=0, column=8)
            ttk.Label(self.sur_frame, text="9", font=('Times New Roman', 20)).grid(row=0, column=9)



            a = ttk.Label(self.sur_frame, text="Anger:", font=('Times New Roman', 25)).grid(column=0, row=1, sticky=tk.W,padx=5, pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=ra, value=range, command= lambda: click(ra.get())).grid(row=1, column=1 + i)

            b = ttk.Label(self.sur_frame, text="Contempt:", font=('Times New Roman', 25)).grid(column=0, row=2,sticky=tk.W, padx=5,pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rb, value=range, command=lambda: click(rb.get())).grid(row=2,column=1 + i)

            c = ttk.Label(self.sur_frame, text="Disgust:", font=('Times New Roman', 25)).grid(column=0, row=3,sticky=tk.W, padx=5, pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rc, value=range, command=lambda: click(rc.get())).grid(row=3,column=1 + i)

            d = ttk.Label(self.sur_frame, text="Fear:", font=('Times New Roman', 25)).grid(column=0, row=4, sticky=tk.W,padx=5, pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rd, value=range, command=lambda: click(rd.get())).grid(row=4,column=1 + i)

            e = ttk.Label(self.sur_frame, text="Sadness:", font=('Times New Roman', 25)).grid(column=0, row=5,sticky=tk.W, padx=5, pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=re, value=range, command=lambda: click(re.get())).grid(row=5,column=1 + i)

            f = ttk.Label(self.sur_frame, text="Surprise:", font=('Times New Roman', 25)).grid(column=0, row=6,sticky=tk.W, padx=5,pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rf, value=range, command=lambda: click(rf.get())).grid(row=6,column=1 + i)

            g = ttk.Label(self.sur_frame, text="Engagement:", font=('Times New Roman', 25)).grid(column=0, row=7,sticky=tk.W, padx=5,pady=5)

            for i in range(9):
                Radiobutton(self.sur_frame, variable=rg, value=range, command=lambda: click(rg.get())).grid(row=7,column=1 + i)

            h = ttk.Label(self.sur_frame, text="Valence:", font=('Times New Roman', 25)).grid(column=0, row=8,sticky=tk.W, padx=5, pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rh, value=range, command=lambda: click(rh.get())).grid(row=8,column=1 + i)


            i = ttk.Label(self.sur_frame, text="Sentimental:", font=('Times New Roman', 25)).grid(column=0, row=9,sticky=tk.W, padx=5,pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=ri, value=range, command=lambda: click(ri.get())).grid(row=9,column=1 + i)


            j = ttk.Label(self.sur_frame, text="Confusion:", font=('Times New Roman', 25)).grid(column=0, row=10,sticky=tk.W, padx=5,pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rj, value=range, command=lambda: click(rj.get())).grid(row=10,column=1 + i)


            k = ttk.Label(self.sur_frame, text="Neutral:", font=('Times New Roman', 25)).grid(column=0, row=11,sticky=tk.W, padx=5, pady=5)
            for i in range(9):
                Radiobutton(self.sur_frame, variable=rk, value=range, command=lambda: click(rk.get())).grid(row=11,column=1 + i)

            def Stop():
                self.sur_frame.destroy()
                self.start_image_exp()
                next_image()
                click()

            NextBut = ttk.Button(self.sur_frame, command = Stop, text="Next").grid(row=13, sticky=tk.E,pady=15)


        def next_image():

            if self.count_number == 0:
                #img_count(0)
                sur_count(0)
            elif self.count_number == 1:
                #img_count(1)
                sur_count(0)
            elif self.count_number == 2:
                #img_count(2)
                sur_count(0)
            elif self.count_number == 3:
                #img_count(3)
                sur_count(0)
            elif self.count_number == 4:
                #img_count(5)
                sur_count(0)
            else:
                self.top.destroy()

        SkipBut = ttk.Button(frame_1, command=next_image, text="Skip").grid(row=0, column=10, pady=5)

        #SurveyBut = ttk.Button(frame_1, command=survey, text="Survey").grid(row=0, column=20, pady=5)

        self.top.mainloop()




    def switch_lab(self):
        if (self.settings == 'lab'):
            self.no_participant1.config(text="Already in the lab setting Mode!")
        else:
            self.no_participant1.config(text="lab setting Mode selected!")
            self.settings = 'lab'

    def GSR_rec(self, pat, id, type):
        main = GSR_rec.Record(pat, id, type)
        main.create_stream()
        main.on_rec()

    def start_camera(self):
        if (self.settings == 'lab') & (self.experiment == True):
            self.camera_on = True
            if self.imag_exp == 1:
                cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording,
                                        args=(self.participantId, 1, 0, self.frame,
                                              self.time_conversion))
                cam1.start()
                sc = threading.Thread(target=ScreenRecording.ScreenRec, args=(self.participantId, 1, 0, True,
                                                                              self.time_conversion))
                sc.start()
                gsr = threading.Thread(target=self.GSR_rec, args=(self.participantId, 1, 0))
                gsr.start()
            elif self.imag_exp == 2:
                cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording, args=(self.participantId, 2, 0,
                                                                                          self.time_conversion))
                cam1.start()
                sc = threading.Thread(target=ScreenRecording.ScreenRec,
                                      args=(self.participantId, 2, 0, self.time_conversion))
                sc.start()
                gsr = threading.Thread(target=self.GSR_rec, args=(self.participantId, 2, 0))
                gsr.start()
            elif self.imag_exp == 3:
                cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording, args=(self.participantId, 3, 1,
                                                                                          self.time_conversion))
                cam1.start()
                sc = threading.Thread(target=ScreenRecording.ScreenRec, args=(self.participantId, 3, 1,
                                                                              self.time_conversion))
                sc.start()
                gsr = threading.Thread(target=self.GSR_rec, args=(self.participantId, 3, 1))
                gsr.start()

        elif (self.settings == 'home') & (self.experiment == True):
            self.camera_on = True
            if self.imag_exp == 1:
                cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording,
                                        args=(self.participantId, 1, 0, self.frame,
                                              self.time_conversion))
                cam1.start()
                sc = threading.Thread(target=ScreenRecording.ScreenRec, args=(self.participantId, 1, 0, self.frame,
                                                                              self.time_conversion))
                sc.start()

            elif self.imag_exp == 2:
                cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording, args=(self.participantId, 2, 0,
                                                                                          self.time_conversion))
                cam1.start()
                sc = threading.Thread(target=ScreenRecording.ScreenRec,
                                      args=(self.participantId, 2, 0, self.time_conversion))
                sc.start()

            elif self.imag_exp == 3:
                cam1 = threading.Thread(target=ffmpeg_video_audio.Camera_recording, args=(self.participantId, 3, 1,
                                                                                          self.time_conversion))
                cam1.start()
                sc = threading.Thread(target=ScreenRecording.ScreenRec,
                                      args=(self.participantId, 3, 1, self.time_conversion))
                sc.start()
        else:
            self.no_participant1.config(text="experiment is not started yet!")

    def switch_home(self):
        print("home setting mode")

        if (self.settings == 'home'):
            self.no_participant1.config(text="Already in the home setting Mode!")
            print('already using home settings mode !')
        else:
            self.no_participant1.config(text="home setting Mode selected!")
            self.settings = 'home'

    def show_anagraphic(self):
        top = tk.Toplevel()
        top.title("Anagraphic data")
        top.geometry("500x500")

        fp = open('anagraphicData.txt', 'r')
        data = json.load(fp)

        participants = data['Participants']

        user = None

        for p in participants:
            if str(p['id']) == self.participantId:
                user = p
                break

        if user is not None:

            ttk.Label(top, text="Participant n " + self.participantId, font='Times 26').grid(row=0, column=1, pady=30,
                                                                                             padx=20)
            ttk.Label(top, text="Age :  " + user['age'], font='Times 18').grid(row=1, column=1, sticky=tk.W, pady=20,
                                                                               padx=5)
            ttk.Label(top, text="Gender :  " + user['gender'], font='Times 18').grid(row=2, column=1, sticky=tk.W,
                                                                                     pady=20, padx=5)
            ttk.Label(top, text="Educational Level :  " + user['edu'], font='Times 18').grid(row=3, column=1,
                                                                                             sticky=tk.W, pady=20,
                                                                                             padx=5)



        else:
            ttk.Label(top, text="Data on Participant " + self.participantId + " not found.", font='Times 18').grid(
                row=0,
                column=1,
                padx=5)
            top.rowconfigure(0, weight=1)

        ttk.Button(top, text="Close", command=top.destroy).grid(row=4, column=1, pady=50)
