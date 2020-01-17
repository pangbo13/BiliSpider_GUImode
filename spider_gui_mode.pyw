# -*- coding: UTF-8 -*-
from bilispider import spider
import os
import sys
import time
import queue
import requests
import threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkinter.messagebox as tkmsgbox
from tkinter.filedialog import askdirectory
class spider_gui_mode(spider,threading.Thread):
	def __init__(self,rid,config={}):
		threading.Thread.__init__(self,daemon=True)
		spider.__init__(self,rid,config)
	def set_logger(self,config):
		class gui_logger(object):
			def __init__(self):
				self.log = queue.Queue()
			def add_log(self,level,msg):
				self.log.put((level,time.time(),msg),block=False)
			def debug(self,msg,*args,**kwargs):
				self.add_log(1,msg)
			def info(self,msg,*args,**kwargs):
				self.add_log(2,msg)
			def warning(self,msg,*args,**kwargs):
				self.add_log(3,msg)
			def error(self,msg,*args,**kwargs):
				self.add_log(4,msg)
			def fatal(self,msg,*args,**kwargs):
				self.add_log(5,msg)
		self.SHOW_BAR = False
		self.QUITE_MODE = False
		self._logger = gui_logger()
	def run(self):
		self.auto_run()
	def get_logger(self):
		return self._logger.log
	def get_status(self):
		return self.status

class root_window():
	def __init__(self):
		pass
	def show_window(self):
		config = {}
		root = tk.Tk()
		root.title('设置')
		root.resizable(0,0)

		show_more_choice = tk.BooleanVar(root,value=0)
		get_full_info = tk.BooleanVar(root,value=0)
		working_path = tk.StringVar(root,value=os.getcwd())
		output_choice = tk.IntVar(root,value=config.get('output',1))
		thread_num = tk.IntVar(root,value=config.get('thread_num',2))
		http_port = tk.IntVar(root,value=config.get('http',1214))
		disable_http = tk.BooleanVar(root,value=0)


		#显示基本选项
		es_frame = tk.Frame(root)
		ttk.Label(es_frame,text="分区id").grid(row=0,sticky=tk.E,padx=0)
		ttk.Label(es_frame,text="从url识别").grid(row=1,sticky=tk.E,padx=0)
		ttk.Label(es_frame,text="工作目录").grid(row=2,sticky=tk.E,padx=0)

		#加载tid输入框
		tid_entry = ttk.Combobox(es_frame,width=18)
		self.tid_entry = tid_entry
		tid_entry.grid(row=0,column=1,sticky=tk.W)
		tid_info = self.load_tid_info()
		tid_option = tuple(" - ".join(line) for line in filter(lambda line:line[1],tid_info))
		tid_entry.config(value=tid_option)
		tid_entry.insert(0,config.get('tid',''))
		self.tid_entry_focusout()
		tid_entry.bind("<FocusOut>",self.tid_entry_focusout)
		#tid_entry.bind("<Leave>",tid_entry_focusout)
		tid_entry.bind("<KeyRelease>",self.tid_entry_change)
		tid_entry.bind("<FocusIn>",self.tid_entry_focusin)
		tid_entry.bind("<ButtonRelease-1>",self.tid_entry_focusin)
		tid_entry.bind("<Return>",self.tid_entry_onreturn)
		
		#url输入框
		url_entry = ttk.Entry(es_frame,width=40)
		url_entry.grid(row=1,column=1,columnspan=3,sticky=tk.W)
		url_entry.bind("<Return>",self.get_tid)
		url_entry.bind("<FocusIn>",self.url_entry_focusin)

		#工作目录输入框
		ttk.Entry(es_frame,width=30,textvariable=working_path).grid(row=2,column=1,columnspan=2,sticky=tk.W)

		#ttk.Button(es_frame,text='确认',width=5,command=get_tid).grid(row=0,column=2,sticky=tk.W)
		ttk.Button(es_frame,text='选择',width=5,command=self.selectpath).grid(row=2,column=3,sticky=tk.W)
		tid_info_label = ttk.Label(es_frame)
		tid_info_label.grid(row=0,column=2,columnspan=2,padx=10,sticky=tk.W)
		es_frame.columnconfigure(0,minsize=80)
		es_frame.columnconfigure(1,minsize=10)
		es_frame.columnconfigure(2,minsize=80)
		es_frame.columnconfigure(3,minsize=100)
		es_frame.pack()

		#高级选项
		ad_frame = tk.Frame(root)
		#logmode_choice = tk.IntVar(root,value=config.get('logmode',1))
		#添加分割线
		ttk.Separator(ad_frame,orient=tk.HORIZONTAL).grid(row=0,column=0,columnspan=4,sticky="we",pady=8,padx=0)
		#添加标签控件
		ttk.Label(ad_frame,text='输出级别').grid(row=1,column=0,padx=(0,10))
		ttk.Label(ad_frame,text='线程数').grid(row=3,column=0)
		ttk.Label(ad_frame,text='http服务器端口').grid(row=4,column=0,padx=(0,10))
		#日志模式单选按钮
		logmode_description = ('DEBUG','INFO','ERROR')
		for i in range(3):
			ttk.Radiobutton(ad_frame,text=logmode_description[i],variable=output_choice,value=i).grid(row=1,column=i+1,stick=tk.W)

		#添加线程数滑动条
		ttk.Scale(ad_frame, from_=1, to=10,length=150,variable=thread_num,command=self.show_thread_num).grid(row=3,column=1,columnspan=2)
		thread_num_label = tk.Label(ad_frame,text='2')
		thread_num_label.grid(row=3,column=3)
		#添加端口输入框
		http_scale = ttk.Scale(ad_frame, from_=1, to=2000,length=150,variable=http_port,command=self.set_port)
		http_scale.grid(row=4,column=1,columnspan=2)
		ttk.Entry(ad_frame,textvariable=http_port,width=6).grid(row=4,column=3)
		#添加复选框
		ttk.Checkbutton(ad_frame,text='收集完整信息',variable=get_full_info).grid(row=5,rowspan=3,column=0,padx=(0,10))
		ttk.Checkbutton(ad_frame,text='禁用监视',variable=disable_http,command=self.http_switch).grid(row=5,rowspan=2,column=1)
		#高级选项结束
		

		buttom_frame = tk.Frame(root)
		ttk.Checkbutton(buttom_frame,text='展开高级选项',width=12,command=self.show_more_or_less,variable=show_more_choice).pack(side=tk.RIGHT,fill=tk.X,padx=(10,20))
		ttk.Button(buttom_frame,text='退出',width=8,command=sys.exit).pack(side=tk.RIGHT,fill=tk.X,padx=(10,20))
		ttk.Button(buttom_frame,text='开始',width=8,command=self.on_start).pack(side=tk.RIGHT,fill=tk.X,padx=(60,20))
		buttom_frame.pack(pady=(7,5))

		tid_entry.focus_set()

		self.root = root
		self.config = config
		self.working_path = working_path
		self.show_more_choice = show_more_choice
		self.ad_frame = ad_frame
		self.output_choice = output_choice
		self.thread_num = thread_num
		self.http_port = http_port
		# self.tid_entry = tid_entry
		self.tid_info_label = tid_info_label
		self.url_entry = url_entry
		self.es_frame = es_frame
		self.thread_num_label = thread_num_label
		self.tid_info = tid_info
		self.get_full_info = get_full_info
		self.http_scale = http_scale
		self.disable_http = disable_http

		#self.http_port.config(state=tk.DISABLED)

		root.mainloop()

	def get_tid(self,event):
		# if not url_entry.get():
		# 	if tid_entry.get():
		# 		tkmsgbox.showinfo("提醒","已输入分区id，请点击 开始")
		# 	else :
		# 		tkmsgbox.showinfo("错误","请填入视频url或者av号")
		# 	return
		self.tid_info_label.config(text = '正在获取')
		try:
			from bilispider.tools import get_tid_by_url,aid_decode
			info = get_tid_by_url(aid_decode(url_entry.get()))
			assert len(info[0])<40
			tid_entry.delete(0,tk.END)
			tid_entry.insert(0," - ".join(info))
			tid_info_label.config(text = "获取成功")
		except:
			self.tid_info_label.config(text = '获取失败')

	def show_more_or_less(self):
		if self.show_more_choice.get():
			self.ad_frame.pack(after=self.es_frame)
		else:
			self.ad_frame.forget()

	def http_switch(self):
		if self.disable_http.get():
			self.http_scale.config(state=tk.DISABLED)
			self.his_http = self.http_port.get()
			self.http_port.set(0)
		else:
			self.http_scale.config(state=tk.NORMAL)
			self.http_port.set(getattr(self,'his_http',1214))

	def show_thread_num(self,pos):
		self.thread_num_label.config(text=str(self.thread_num.get()))

	def set_port(self,pos):
		self.http_port.set(int(self.http_port.get()))

	def selectpath(self):
		path = askdirectory(initialdir=self.working_path.get())
		if path:
			self.working_path.set(path)

	def tid_entry_focusout(self,*args,**kwargs):
		self.tid_entry.select_clear()
		# if tid_entry.get().split("-")[0].strip().isdigit():
		# 	tid = tid_entry.get().split("-")[0].strip()
		# 	info = list(filter(lambda line:line[0]==tid,tid_inf))
		# 	if len(info) == 0:
		# 		return
		# 	elif info[0][1]:
		# 		tid_entry.delete(0,tk.END)
		# 		tid_entry.insert(0," - ".join(info[0]))

	def tid_entry_focusin(self,event):
		self.tid_info_label.config(text="")
		index = len(self.tid_entry.get().split('-')[0].strip())
		self.tid_entry.select_range(0,index)
		self.tid_entry.icursor(index)

	def tid_entry_change(self,event):
		tid_entry = self.tid_entry
		tid = tid_entry.get().split("-")[0]
		if tid.startswith(' '):
			tid = tid.lstrip()
			tid_entry.delete(0,tk.END)
			if not tid == '':
				tid_entry.insert(tid)
			
		if event.keycode == 8 :
			tid_entry.delete(tid_entry.index(tk.INSERT)-1,tk.INSERT)
		elif event.keycode in (37,39):
			if tid_entry.index(tk.INSERT) > len(tid)-1:
				tid_entry.icursor(len(tid)-1)
				tid_entry.select_range(0,tk.INSERT)
			return
		if tid:
			tid = tid.rstrip()
			info = list(filter(lambda line:line[0].startswith(tid) or line[0]==tid,self.tid_info))
			#print(info)
			if len(info) > 0:
				index = tid_entry.index(tk.INSERT)
				tid_entry.delete(0,tk.END)
				tid_entry.insert(0," - ".join(info[0]))
				tid_entry.icursor(index)
				if index < len(info[0][0]):
					#tid_entry.select_range(tk.INSERT,tk.END)
					tid_entry.select_range(tk.INSERT,len(info[0][0]))
			else :
				tid_entry.delete(tk.INSERT,tk.END)

	def tid_entry_onreturn(self,event):
		self.tid_entry_focusout(event)
		self.on_start()

	def url_entry_focusin(self,event):
		self.url_entry.select_range(0,tk.END)
		self.tid_info_label.config(text="按下回车以获取tid")

	def load_tid_info(self):
		try:
			from pkg_resources import resource_string
			tid_info_str = resource_string('bilispider', 'data/tid.txt').decode()
		except:
			print("无法载入")
			return tuple()
		tid_info = [line.split(',') for line in tid_info_str.split('\r\n')]
		return tid_info
	
	def on_start(self):
		os.chdir(self.working_path.get())
		config = self.config
		try:
			config['tid'] = (int(self.tid_entry.get().split(" - ")[0]),)
		except:
			tkmsgbox.showwarning("警告","分区id无效")
			return

		config['output'] = 0
		config['thread_num'] = int(self.thread_num.get())
		config['http'] = int(self.http_port.get())
		config['gui_output'] = self.output_choice.get()
		config['save_full'] = self.get_full_info.get()

		self.root.withdraw() #隐藏主窗口
		
		process_window(config,self).show_window()
		

class process_window():
	def __init__(self,config,father):
		self.config = config
		self.father = father

	def show_window(self):
		root = tk.Tk()
		root.title("bilispider")
		root.resizable(0,0)

		top_frame = tk.Frame(root)
		top_frame.pack(fill=tk.BOTH)
		process_bar = ttk.Progressbar(top_frame,mode="indeterminate",length=300)
		process_bar.pack(anchor='w',side=tk.LEFT)
		progress_label = ttk.Label(top_frame,text="初始化")
		progress_label.pack(after=process_bar)

		mid_frame = tk.Frame(root)
		mid_frame.pack()
		log_text = tk.Text(mid_frame,height=20,width=60)
		log_text.pack(side=tk.LEFT,fill=tk.Y)
		log_scrollbar = tk.Scrollbar(mid_frame)
		log_scrollbar.pack(side=tk.LEFT,after=log_text,fill=tk.Y)

		log_scrollbar.config(command=log_text.yview)
		log_text.config(yscrollcommand=log_scrollbar.set)

		buttom_frame = ttk.Frame(root)
		buttom_frame.pack(fill=tk.BOTH)
		ttk.Button(buttom_frame,text="显示更多",command=self.show_more_info).pack(side=tk.LEFT,padx=(80,0))
		pause_botton = ttk.Button(buttom_frame,text="暂停",command=self.set_pause)
		pause_botton.pack(side=tk.RIGHT,padx=(0,80))

		process_bar.start()
		root.protocol("WM_DELETE_WINDOW", self.processwindow_on_closing)

		spider = spider_gui_mode(self.config['tid'][0],self.config)
		spider.start()

		self.root = root
		self.process_bar = process_bar
		self.log_text = log_text
		self.progress_label = progress_label
		self.spider = spider
		self.pause_botton = pause_botton

		threading.Thread(target=self.monitor_loop,daemon=True).start()

		root.mainloop()

	def set_pause(self,multi=False):
		if multi:
			self.pause_botton.config(state=tk.DISABLED)
			self.root.update()
			self.spider.set_pause(1)
			self.pause_botton.config(text='继续',command=self.set_continue)
			self.pause_botton.config(state=tk.NORMAL)
		else:
			threading.Thread(target=self.set_pause,args=(True,),name="set_pause").start()
			

	def set_continue(self):
		self.pause_botton.config(state=tk.DISABLED)
		self.root.update()
		self.spider.set_pause(0)
		self.pause_botton.config(text='暂停',command=self.set_pause)
		self.pause_botton.config(state=tk.NORMAL)

	def processwindow_on_closing(self):
		if self.spider.is_alive():
			if tkmsgbox.askokcancel("确认退出", "爬虫正在运行，若强制退出可能损失部分数据"):
				# if self.spider.get_http_thread():
				# 	try:
				# 		requests.get('http://localhost:1214/exit',timeout=0.1)
				# 	except:
				# 		pass
				self.father.root.destroy()
				self.root.destroy()
				sys.exit()
		else:
			# if self.spider.get_http_thread():
			# 		try:
			# 			requests.get('http://localhost:1214/exit',timeout=0.1)
			# 		except:
			# 			pass
			self.father.root.destroy()
			self.root.destroy()
			sys.exit()

	def show_log(self):
		log_text = self.log_text
		while not self.spider.get_logger().empty():
			log_line = self.spider.get_logger().get(block=False)
			if self.output_level == 1 and log_line[0] < 2:
				continue
			elif self.output_level == 2 and log_line[0] < 4:
				continue
			strtime = time.strftime("%H:%M:%S", time.localtime(log_line[1]))
			line_index = int(log_text.index(tk.END).split('.')[0])-1
			log_level = self.log_level_list[log_line[0]]
			log_text.insert(tk.END,"[{}][{}]{}\n".format(strtime,log_level,log_line[2]))
			log_text.tag_add(log_level,"%s.%s"%(line_index,10),"%s.%s"%(line_index,len(log_level)+12))
			log_text.tag_add("time","%s.%s"%(line_index,0),"%s.%s"%(line_index,10))
			log_text.see(tk.END)

	def monitor_loop(self):

		log_text = self.log_text

		self.process_bar.stop()
		self.process_bar.config(mode="determinate")

		self.output_level = self.config['gui_output']
		self.log_level_list= ('','DEBUG','INFO','WARNING','ERROR','FATAL')
		log_text.tag_config("DEBUG",foreground="forestgreen")
		log_text.tag_config("INFO",foreground="blue")
		log_text.tag_config("WARNING",foreground="orange")
		log_text.tag_config("ERROR",foreground="yellow",background="red")
		log_text.tag_config("FATAL",foreground="orangered",background="black")
		log_text.tag_config("time",foreground="dimgray")

		while True:
			self.show_log()
			persentage = self.spider.status.get('percentage',0)*100
			self.process_bar.config(value = persentage)
			self.progress_label.config(text= "%.2f" % persentage +" %" )
			if not self.spider.is_alive():
				break
			time.sleep(0.1)
		self.show_log()
		if self.spider.status['progress'] == 'fatal':
			self.process_bar.config(value=0)
			self.progress_label.config(text="失败")
		else:
			self.process_bar.config(value=100)
			self.progress_label.config(text="完成")

	def show_more_info(self):
		detail_window(self).show_window()

class detail_window():
	def __init__(self,father):
		self.father = father
	def show_window(self):
		root = tk.Tk()

		self.detail_text = tk.Text(root,height = 13,width = 45)
		self.detail_text.pack()
		root.protocol("WM_DELETE_WINDOW", self.detailwindow_on_closing)
		self.flag = True
		threading.Thread(target=self.refresh,daemon=True).start()
		
		self.root = root
		root.mainloop()

	def refresh(self):
		#self.detail_text.insert(1.0,' ')
		while self.flag:
			self.detail_text.delete(1.0,tk.END)
			detail = "\n".join(":".join(map(str,i)) for i in self.father.spider.status.items())
			self.detail_text.insert(1.0,detail)
			time.sleep(0.5)

	def detailwindow_on_closing(self):
		self.flag = False
		self.root.destroy()

if __name__ == "__main__":
	root_window().show_window()