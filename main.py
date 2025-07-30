import os
import threading
import time
from obswebsocket import obsws, requests
import win32gui
import tkinter as tk
from tkinter import ttk
import json
from cryptography.fernet import Fernet
from tkinter import messagebox
 
def get_open_windows():
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                result.append(title)
    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    return windows
 
def get_focused_window():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)
 
class WindowMonitorApp:
    def __init__(self, root):
       
        self.DATA_FILE = "data.enc"
        self.KEY_FILE = "key.key"
        self.root = root
        self.root.title("Window Focus Monitor")
        self.OBS_SCENE = "obs_scene"
        self.OBS_SOURCE_NAME = "obs_source_name"
        self.OBS_ADDRESS = "obs_address"
        self.OBS_PASSWORD = "obs_password"
        self.WINDOWS_LIST = "window"
        self.obs_scene_name = ""
        self.obs_scene_uuid = ""
        self.obj_uuid = ""
        self.obs_address_var = tk.StringVar()
        self.obs_address_var.set("")
        self.obs_password_var = tk.StringVar()
        self.obs_password_var.set("")
        self.obs_obj_var = tk.StringVar()
        self.obs_obj_var.set("")
        self.obs_connection_button:tk.Button = None
        self.obs_sources_combobox:ttk.Combobox = None
 
        self.windows_var = tk.StringVar()
        self.windows_list:list[str]=[]
        self.window_combobox:ttk.Combobox = None
       
        self.obs:obsws = None
       
        self.monitoring = False
        self.monitoring_last = False
        self.last_window = ""
        self.create_widgets()
        self.load_data()    
        root.protocol("WM_DELETE_WINDOW", self.on_close)
 
    def on_close(self):
        self.save()
        self.root.destroy()
        if self.obs:
            self.obs.disconnect()
       
    def create_widgets(self):
        row = 0
        tk.Label(self.root, text="Address:").grid(row=row, column=0, sticky="e")
        self.obs_address_entry = tk.Entry(self.root, textvariable=self.obs_address_var)
        self.obs_address_entry.grid(row=row, column=1)
       
        row+=1
        tk.Label(self.root, text="Password:").grid(row=row, column=0, sticky="e")
        self.obs_password_entry = tk.Entry(self.root, textvariable=self.obs_password_var,show="*")
        self.obs_password_entry.grid(row=row, column=1)
       
        row+=1
        self.obs_connection_button = tk.Button(self.root,text="Connect to obs",bg="green",fg="white",command=self.toggle_obs_connection)
        self.obs_connection_button.grid(row=row, column=1)
       
        row+=1
        tk.Label(self.root,text="Sources:").grid(row=row,column=0,sticky="e")
        self.obs_sources_combobox = ttk.Combobox(self.root,textvariable=self.obs_obj_var)
        self.obs_sources_combobox.grid(row=row,column=1)
      
        row+=1
        self.obs_source_refresh_button = tk.Button(self.root,text="Refresh sources",bg="gray",fg="white",command=self.refresh_obs_obj_list)
        self.obs_source_refresh_button.grid(row=row,column=1)
       
        row+=1
        tk.Label(self.root,text="Window:").grid(row=row,column=0,sticky="e")
        self.window_combobox = ttk.Combobox(self.root,textvariable=self.windows_var,postcommand=self.refresh_window)
        self.window_combobox.grid(row=row,column=1)
       
        row+=1
        self.window_secondary_button = tk.Button(self.root,text="Add window",bg="gray",fg="white",command=self.add_window)
        self.window_secondary_button.grid(row=row,column=1)
       
        row+=1
        self.window_secondary_frame = tk.Frame(self.root)
        self.window_secondary_frame.grid(row=row,column=1,sticky='w')
       
        row+=1
        self.monitoring_button = tk.Button(self.root,text="Start monitoring",bg="green",fg="white",command=self.toggle_monitoring)
        self.monitoring_button.grid(row=row,column=1)
   
    def save(self):
        json_data = {
            self.OBS_ADDRESS:self.obs_address_var.get(),
            self.OBS_PASSWORD:self.obs_password_var.get(),
            self.OBS_SOURCE_NAME:self.obs_obj_var.get(),
            self.WINDOWS_LIST:self.windows_list,
            self.OBS_SCENE:self.obs_scene_name
        }
       
        key = self.load_key()
        encrypted = Fernet(key).encrypt(json.dumps(json_data).encode())
        with open(self.DATA_FILE,"wb") as f:
            f.write(encrypted)
                   
    def load_key(self):
        
        if os.path.exists(self.KEY_FILE):
            with open(self.KEY_FILE,"rb") as f:
                return f.read()     
        else:
            key = Fernet.generate_key()
            with open(self.KEY_FILE, "wb") as f:
                f.write(key)
            return key
            
 
    def load_data(self):
        key = self.load_key()
        if not os.path.exists(self.DATA_FILE):
            return
        with open(self.DATA_FILE,'rb') as f:
            encrypted = f.read()
        decrypted:str = ""
        try:
            decrypted = Fernet(key).decrypt(encrypted).decode()
        except Exception as e:
            os.remove(self.KEY_FILE)
            os.remove(self.DATA_FILE)
            self.load_data
        data =  json.loads(decrypted)
           
        if self.OBS_ADDRESS not in data:
            data[self.OBS_ADDRESS] = ""
            
        if self.OBS_PASSWORD not in data :
            data[self.OBS_PASSWORD] = ""
            
        if self.OBS_SCENE not in data or self.OBS_SOURCE_NAME not in data:
            data[self.OBS_SCENE] = ""
            data[self.OBS_SOURCE_NAME] = ""
            
        if self.WINDOWS_LIST not in data:
            data[self.WINDOWS_LIST] = []
        
        self.obs_address_var.set(data[self.OBS_ADDRESS])
        self.obs_password_var.set(data[self.OBS_PASSWORD])
        self.obs_obj_var.set(data[self.OBS_SOURCE_NAME])
        self.obs_scene_name = data[self.OBS_SCENE]
        for item in data[self.WINDOWS_LIST]:
            self.add_window(item)
       
   
    def get_ip_port(self):
        return self.obs_address_var.get().split(":")
   
    def toggle_obs_connection(self):
        if self.obs:
            self.obs_disconnect()
        else:
            self.obs_connect()
   
    def obs_disconnect(self):
        self.obs.disconnect()
        self.obs_connection_button.config(text="Connect to obs",bg="green")
        self.obs = None
   
    def obs_connect(self):
        if self.obs:
            return True
        ip = ""
        port = ""
        try:
            ip, port = self.get_ip_port()
        except Exception as e:
            messagebox.showerror(message="IP and port not valid format")
            return False
        try:
           
            self.obs = obsws(ip,port,self.obs_password_var.get())
            self.obs.connect()
            self.obs_connection_button.config(text="Disconnect from obs",bg="red")
            return True
        except Exception as e:
            print(e)
            messagebox.showerror(message="Error while trying to connect to obs")
            self.obs = None
            return False
   
    def refresh_obs_obj_list(self):
        if not self.obs_connect():
            return
        scene_list = self.obs.call(requests.GetSceneList())
        self.obs_scene_name = scene_list.__dict__["datain"]["currentProgramSceneName"]
        self.obs_scene_uuid = scene_list.__dict__["datain"]["currentProgramSceneUuid"]
        response = self.obs.call(requests.GetSceneItemList(sceneName=self.obs_scene_name,
                                                           sceneUuid=self.obs_scene_uuid))
        objs =[]
        for source in response.__dict__['datain']['sceneItems']:
            objs.append(source['sourceName'])
        self.obs_sources_combobox["values"] = objs
   
    def refresh_window(self):
        self._refresh_window_list(self.window_combobox)
   
    def _refresh_window_list(self,obj:ttk.Combobox):
        windows = get_open_windows()
        obj["values"] = windows
   
    def add_window(self,window:str=""):
       
        if window != "":
            if window in self.windows_list:
                return
            self.windows_list.append(window)
        else:
            if self.windows_var.get() in self.windows_list or self.windows_var.get() == "":
                return
 
            self.windows_list.append(self.windows_var.get())
        frame = tk.Frame(self.window_secondary_frame)
        frame.grid(row=len(self.windows_list)-1,column=1)
        tk.Label(frame,text=self.windows_list[-1]).grid(row=0,column=0,sticky='w')
        button = tk.Button(frame,text="Remove",bg="red",command=lambda:self.delete_window(frame,len(self.windows_list)-1))
        button.grid(row=0,column=1,sticky='e')
           
    def delete_window(self,item:tk.Frame,number):
        item.destroy()
        del self.windows_list[number]
        self.refresh_window()
   
   
    def toggle_monitoring(self):
        if self.monitoring:
            self.monitoring_button.config(bg="green",text="Start monitoring")
            self.monitoring = False
        else:
            if not self.obs_connect():
                return
            if not self.obs_obj_var.get():
                return
            scene_list = self.obs.call(requests.GetSceneList())
            self.obs_scene_uuid = ""
            for scene in scene_list.datain["scenes"]:
                if scene["sceneName"] == self.obs_scene_name:
                    self.obs_scene_uuid = scene["sceneUuid"]
            if not self.obs_scene_uuid:
                return
            response = self.obs.call(requests.GetSceneItemId(
                sceneName=self.obs_scene_name,
                sceneUuid=self.obs_scene_uuid,
                sourceName=self.obs_obj_var.get(),
                searchOffset=0
            ))
            self.obj_uuid = response.datain['sceneItemId']
            self.monitoring = True
            self.monitoring_button.config(bg="red",text="Stop monitoring")
            thread = threading.Thread(target=self.monitor)
            thread.start()
       
    def get_var_safe(callback,a):
        # This runs in the main thread
        value = a.get()
        callback(value)
      
    def monitor(self):
        while self.monitoring:
            time.sleep(0.001)
            focus_window = get_focused_window()
            if not focus_window or focus_window == self.last_window:
                continue
            self.obs.call(requests.SetSceneItemEnabled(
                sceneItemId=self.obj_uuid,
                sceneItemEnabled= not focus_window in self.windows_list,
                sceneName=self.obs_scene_name,
                sceneUuid=self.obs_scene_uuid
                ))
            self.last_window = focus_window
 
if __name__ == "__main__":
    root = tk.Tk()
    app = WindowMonitorApp(root)
   
    root.mainloop()
 
