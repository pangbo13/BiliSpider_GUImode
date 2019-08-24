# -*- coding: UTF-8 -*-
from bilispider import spider
import time
import queue
import threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsgbox
import tkinter.font as tkFont
class spider_gui_mode(spider,threading.Thread):
	def __init__(self,rid,config={}):
		threading.Thread.__init__(self)
		spider.__init__(self,rid,config)
	def set_logger(self,config):
		class gui_logger(object):
			def __init__(self):
				self.log = queue.Queue()
			def add_log(self,level,msg):
				#self.log.append((level,time.time(),msg))
				self.log.put((level,time.time(),msg),block=False)
			def debug(self,msg):
				self.add_log(1,msg)
			def info(self,msg):
				self.add_log(2,msg)
			def warning(self,msg):
				self.add_log(3,msg)
			def error(self,msg):
				self.add_log(4,msg)
		self.SHOW_BAR = True
		self._logger = gui_logger()
	def run(self):
		self.auto_run()
	def get_logger(self):
		return self._logger.log
	def get_status(self):
		return self.status

if __name__ == "__main__":
	def on_start():
		try:
			config['tid'] = config['tid'] = tuple(set(map(int,tid_entry.get().split(','))))
		except:
			tkmsgbox.showwarning("提醒","分区id无效")
			return
		config['output'] = int(output_choice.get())
		config['logmode'] = int(logmode_choice.get())
		config['thread_num'] = int(thread_num.get())
		config['http'] = int(http_port.get())

		root.withdraw() #隐藏主窗口

		global process_window,top_frame,process_bar,log_text,progress_label,s
		process_window = tk.Tk()
		top_frame = tk.Frame(process_window)
		top_frame.pack(fill=tk.BOTH)
		process_bar = ttk.Progressbar(top_frame,mode="indeterminate",length=300)
		process_bar.pack(anchor='w',side=tk.LEFT)
		progress_label = ttk.Label(top_frame,text="初始化")
		progress_label.pack(after=process_bar)
		log_text = tk.Text(process_window,height=20,width=50)
		log_text.pack(fill=tk.BOTH)
		process_bar.start()
		root.protocol("WM_DELETE_WINDOW", processwindow_on_closing)

		s = spider_gui_mode(config['tid'][0],config)
		s.start()

		threading.Thread(target=monitor_loop).start()

		process_window.mainloop()

	def monitor_loop():
		while s.status.get('process',None) != 'wait':
			time.sleep(0.1)
		
		process_bar.stop()
		process_bar.config(mode="determinate")

		log_level= ('','DEBUG','INFO','WARNING','ERROR')
		while True:
			while not s.get_logger().empty():
				log_line = s.get_logger().get(block=False)
				strtime = time.strftime("%H:%M:%S", time.localtime(log_line[1]))
				log_text.insert(tk.END,"[{}][{}]{}\n".format(strtime,log_level[log_line[0]],log_line[2]))
				#log_text.insert(tk.END," ".join((map(str,s.get_logger().get(block=False))))+"\n")
				log_text.see(tk.END)
			#persentage = s.status['got_pages']/ s.status['all_pages'] * 100
			persentage = s.status.get('percentage',0)*100
			process_bar.config(value=persentage)
			progress_label.config(text= "%.2f" % persentage +" %" )
			if not s.is_alive():
				break
			time.sleep(0.1)
		process_bar.config(value=100)
		progress_label.config(text="完成")

	def processwindow_on_closing():
		return


	def get_tid():
		if not url_entry.get():
			tkmsgbox.showinfo("错误","请填入视频url或者av号")
		tid_info_label.config(text = '正在获取')
		try:
			from bilispider.tools import get_tid_by_url,aid_decode
			tid_entry.delete(0,tk.END)
			info = get_tid_by_url(aid_decode(url_entry.get()))
			tid_entry.insert(0,int(info[0]))
			tid_info_label.config(text = '分区名:' + info[1] + ',id:' + info[0])
		except:
			tid_info_label.config(text = '获取失败')

	def show_more_or_less():
		if show_more_choice.get():
			ad_frame.pack(after=es_frame)
		else:
			ad_frame.forget()

	def show_thread_num(pos):
		thread_num_label.config(text=str(thread_num.get()))

	def set_port(pos):
		http_port.set(int(http_port.get()))

	config = {}
	root = tk.Tk()
	root.title('设置')

	show_more_choice = tk.IntVar(root,value=0)

	#显示基本选项
	es_frame = tk.Frame(root)
	ttk.Label(es_frame,text="分区id").grid(row=0,sticky=tk.E,padx=0)
	ttk.Label(es_frame,text="从url识别").grid(row=1,sticky=tk.E,padx=0)
	tid_entry = ttk.Entry(es_frame)
	tid_entry.grid(row=0,column=1,sticky=tk.W)
	url_entry = ttk.Entry(es_frame,width=40)
	url_entry.grid(row=1,column=1,columnspan=3,sticky=tk.W)
	ttk.Button(es_frame,text='确认',width=5,command=get_tid).grid(row=0,column=1,sticky=tk.E)
	tid_info_label = ttk.Label(es_frame)
	tid_info_label.grid(row=0,column=2,padx=10,sticky=tk.W)
	es_frame.columnconfigure(0,minsize=80)
	es_frame.columnconfigure(1,minsize=200)
	es_frame.columnconfigure(2,minsize=120)
	es_frame.pack()

	#高级选项
	ad_frame = tk.Frame(root)
	logmode_choice = tk.IntVar(root,value=config.get('logmode',1))
	output_choice = tk.IntVar(root,value=config.get('output',1))
	thread_num = tk.IntVar(root,value=config.get('thread_num',2))
	http_port = tk.IntVar(root,value=config.get('http',1214))
	#添加分割线
	ttk.Separator(ad_frame,orient=tk.HORIZONTAL).grid(row=0,column=0,columnspan=4,sticky="we",pady=8,padx=0)
	#添加标签控件
	ttk.Label(ad_frame,text='日志模式').grid(row=1,column=0,padx=(0,10))
	ttk.Label(ad_frame,text='输出模式').grid(row=2,column=0,padx=(0,10))
	ttk.Label(ad_frame,text='线程数').grid(row=3,column=0)
	ttk.Label(ad_frame,text='http服务器端口').grid(row=4,column=0,padx=(0,10))
	#日志模式单选按钮
	logmode_description = ('无输出','进度条模式','输出日志')
	for i in range(3):
		ttk.Radiobutton(ad_frame,text=logmode_description[i],variable=logmode_choice,value=i).grid(row=1,column=i+1,stick=tk.W)
	#输出模式单选按钮
	output_description = ('不保存','仅保存错误','保存所有输出')
	for i in range(3):
		ttk.Radiobutton(ad_frame,text=output_description[i],variable=output_choice,value=i).grid(row=2,column=i+1,stick=tk.W)
	#添加线程数滑动条
	ttk.Scale(ad_frame, from_=1, to=10,length=150,variable=thread_num,command=show_thread_num).grid(row=3,column=1,columnspan=2)
	thread_num_label = tk.Label(ad_frame,text='2')
	thread_num_label.grid(row=3,column=3)
	#添加端口输入框
	ttk.Scale(ad_frame, from_=0, to=2000,length=150,variable=http_port,command=set_port).grid(row=4,column=1,columnspan=2)
	ttk.Entry(ad_frame,textvariable=http_port,width=6).grid(row=4,column=3)
	#高级选项结束
	

	buttom_frame = tk.Frame(root)
	ttk.Checkbutton(buttom_frame,text='展开高级选项',width=12,command=show_more_or_less,variable=show_more_choice).pack(side=tk.RIGHT,fill=tk.X,padx=(10,20))
	ttk.Button(buttom_frame,text='退出',width=8,command=exit).pack(side=tk.RIGHT,fill=tk.X,padx=(10,20))
	ttk.Button(buttom_frame,text='开始',width=8,command=on_start).pack(side=tk.RIGHT,fill=tk.X,padx=(60,20))
	buttom_frame.pack(pady=(7,5))

	root.mainloop()

	# s = spider_gui_mode(54,config={'tid':(54,)})
	# s.start()
	# s.join()
	# #for line in s.get_logger().log:
	# log = s.get_logger()
	# while not log.empty():
	# 	line = log.get(block=False)
	# 	print(" ".join(map(str,line)))