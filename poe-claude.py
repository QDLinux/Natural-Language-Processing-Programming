import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
from PIL import Image, ImageTk

import jieba
import jieba.posseg as pseg
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx
import pandas as pd
import os


# 导入上面B部分的所有函数
# 分词功能
def segment_text(text, user_dict=None):
    """
    对文本进行分词
    :param text: 待分词文本
    :param user_dict: 自定义词典路径
    :return: 分词结果列表
    """
    if user_dict and os.path.exists(user_dict):
        jieba.load_userdict(user_dict)
    words = list(jieba.cut(text))
    return words

# 词频统计功能
def count_word_frequency(word_list, top_n=None):
    """
    统计词频
    :param word_list: 分词后的列表
    :param top_n: 返回前N个高频词
    :return: 词频统计结果
    """
    counter = Counter(word_list)
    if top_n:
        return counter.most_common(top_n)
    return counter

# 词性标注功能
def pos_tagging(text):
    """
    进行词性标注
    :param text: 待标注文本
    :return: 标注结果列表 [(词, 词性)]
    """
    words_pos = list(pseg.cut(text))
    return words_pos

# 保存词性分类结果
def save_pos_results(words_pos, output_file):
    """
    保存词性标注结果
    :param words_pos: 词性标注结果
    :param output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for word, pos in words_pos:
            f.write(f"{word}\t{pos}\n")

# 柱状图可视化
def visualize_bar_chart(data, title, xlabel, ylabel, output_file=None):
    """
    生成柱状图
    :param data: 数据字典 {标签: 值}
    :param title: 图表标题
    :param xlabel: x轴标签
    :param ylabel: y轴标签
    :param output_file: 输出文件路径
    """
    plt.figure(figsize=(12, 8))
    plt.bar(data.keys(), data.values())
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
    plt.show()

# 词云可视化
def generate_wordcloud(word_freq, output_file=None, background_color='white'):
    """
    生成词云
    :param word_freq: 词频字典 {词: 频率}
    :param output_file: 输出文件路径
    :param background_color: 背景颜色
    """
    wordcloud = WordCloud(
        font_path='simhei.ttf',  # 使用中文字体
        background_color=background_color,
        width=800,
        height=600
    ).generate_from_frequencies(word_freq)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    if output_file:
        plt.savefig(output_file)
    plt.show()

# 关系图可视化
def visualize_relationship_graph(relationships, output_file=None):
    """
    生成关系图
    :param relationships: 关系列表 [(实体1, 实体2, 权重)]
    :param output_file: 输出文件路径
    """
    G = nx.Graph()
    
    # 添加节点和边
    for source, target, weight in relationships:
        G.add_edge(source, target, weight=weight)
    
    # 计算节点大小，基于度中心性
    degree = dict(nx.degree(G))
    node_size = [v * 20 for v in degree.values()]
    
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='SimHei')
    plt.axis('off')
    
    if output_file:
        plt.savefig(output_file)
    plt.show()

# 自定义词典功能
def create_custom_dict(words_dict, output_file):
    """
    创建自定义词典
    :param words_dict: 词汇字典 {词: 词频}
    :param output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for word, freq in words_dict.items():
            f.write(f"{word} {freq} n\n")  # 默认词性为n

# 统计并保存人名
def extract_and_save_names(words_pos, output_file):
    """
    提取并保存人名
    :param words_pos: 词性标注结果
    :param output_file: 输出文件路径
    :return: 人名词频字典
    """
    names = [word for word, pos in words_pos if pos == 'nr']
    name_counts = Counter(names)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for name, count in name_counts.most_common():
            f.write(f"{name}\t{count}\n")
    
    return name_counts

# 统计并保存地名
def extract_and_save_locations(words_pos, output_file):
    """
    提取并保存地名
    :param words_pos: 词性标注结果
    :param output_file: 输出文件路径
    :return: 地名词频字典
    """
    locations = [word for word, pos in words_pos if pos == 'ns']
    location_counts = Counter(locations)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for location, count in location_counts.most_common():
            f.write(f"{location}\t{count}\n")
    
    return location_counts

# 统计并保存武器名
def extract_and_save_weapons(text, weapon_dict, output_file):
    """
    提取并保存武器名
    :param text: 文本内容
    :param weapon_dict: 武器词典路径
    :param output_file: 输出文件路径
    :return: 武器词频字典
    """
    # 加载武器词典
    jieba.load_userdict(weapon_dict)
    words = list(jieba.cut(text))
    
    # 从武器词典中读取武器列表
    weapons = []
    with open(weapon_dict, 'r', encoding='utf-8') as f:
        for line in f:
            weapon = line.strip().split()[0]
            weapons.append(weapon)
    
    # 统计武器出现频率
    weapon_counts = {}
    for word in words:
        if word in weapons:
            weapon_counts[word] = weapon_counts.get(word, 0) + 1
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        for weapon, count in sorted(weapon_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{weapon}\t{count}\n")
    
    return weapon_counts

class NLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自然语言处理系统")
        self.root.geometry("1000x700")
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧功能面板
        self.left_frame = ttk.LabelFrame(self.main_frame, text="功能选项")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 添加功能按钮
        self.create_buttons()
        
        # 创建右侧结果显示区
        self.right_frame = ttk.LabelFrame(self.main_frame, text="结果显示")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文本显示区
        self.text_area = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=60, height=15)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 可视化显示区
        self.viz_frame = ttk.Frame(self.right_frame)
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 存储当前文件路径
        self.current_file = None
        self.text_content = None
        
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开文件", command=self.open_file)
        file_menu.add_command(label="保存结果", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 功能菜单
        function_menu = tk.Menu(menu_bar, tearoff=0)
        function_menu.add_command(label="分词", command=lambda: self.process_text('segment'))
        function_menu.add_command(label="词频统计", command=lambda: self.process_text('frequency'))
        function_menu.add_command(label="词性标注", command=lambda: self.process_text('pos'))
        menu_bar.add_cascade(label="功能", menu=function_menu)
        
        # 可视化菜单
        viz_menu = tk.Menu(menu_bar, tearoff=0)
        viz_menu.add_command(label="柱状图", command=lambda: self.visualize('bar'))
        viz_menu.add_command(label="词云", command=lambda: self.visualize('wordcloud'))
        viz_menu.add_command(label="关系图", command=lambda: self.visualize('relationship'))
        menu_bar.add_cascade(label="可视化", menu=viz_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="使用帮助", command=self.show_help)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_buttons(self):
        # 文件操作按钮
        file_frame = ttk.LabelFrame(self.left_frame, text="文件操作")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="打开文件", command=self.open_file).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="保存结果", command=self.save_results).pack(fill=tk.X, padx=5, pady=2)
        
        # 文本处理按钮
        process_frame = ttk.LabelFrame(self.left_frame, text="文本处理")
        process_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(process_frame, text="分词", command=lambda: self.process_text('segment')).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(process_frame, text="词频统计", command=lambda: self.process_text('frequency')).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(process_frame, text="词性标注", command=lambda: self.process_text('pos')).pack(fill=tk.X, padx=5, pady=2)
        
        # 实体提取按钮
        entity_frame = ttk.LabelFrame(self.left_frame, text="实体提取")
        entity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(entity_frame, text="提取人名", command=lambda: self.extract_entity('name')).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(entity_frame, text="提取地名", command=lambda: self.extract_entity('location')).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(entity_frame, text="提取武器", command=lambda: self.extract_entity('weapon')).pack(fill=tk.X, padx=5, pady=2)
        
        # 可视化按钮
        viz_frame = ttk.LabelFrame(self.left_frame, text="可视化")
        viz_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(viz_frame, text="生成柱状图", command=lambda: self.visualize('bar')).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(viz_frame, text="生成词云", command=lambda: self.visualize('wordcloud')).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(viz_frame, text="生成关系图", command=lambda: self.visualize('relationship')).pack(fill=tk.X, padx=5, pady=2)
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.text_content = f.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, f"已加载文件: {os.path.basename(file_path)}\n")
                    self.text_area.insert(tk.END, f"文件长度: {len(self.text_content)} 字符\n")
                    self.text_area.insert(tk.END, "预览:\n")
                    self.text_area.insert(tk.END, self.text_content[:200] + "...\n")
                    self.status_bar.config(text=f"已加载文件: {file_path}")
            except Exception as e:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, f"错误: {str(e)}")
    
    def save_results(self):
        if not hasattr(self, 'result_data'):
            tk.messagebox.showinfo("提示", "没有可保存的结果")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_data)
                self.status_bar.config(text=f"结果已保存至: {file_path}")
            except Exception as e:
                tk.messagebox.showerror("保存错误", str(e))
    
    def process_text(self, mode):
        if not self.text_content:
            tk.messagebox.showinfo("提示", "请先加载文本文件")
            return
            
        self.status_bar.config(text="处理中...")
        
        # 使用线程避免界面卡顿
        def process_thread():
            result = ""
            try:
                if mode == 'segment':
                    words = segment_text(self.text_content)
                    result = " ".join(words[:100]) + "...\n\n共分词 " + str(len(words)) + " 个词语"
                    self.segmented_words = words
                
                elif mode == 'frequency':
                    if not hasattr(self, 'segmented_words'):
                        self.segmented_words = segment_text(self.text_content)
                    
                    word_freq = count_word_frequency(self.segmented_words, top_n=50)
                    result = "词频统计结果 (前50):\n\n"
                    for word, freq in word_freq:
                        result += f"{word}: {freq}\n"
                    
                    self.word_freq = word_freq
                
                elif mode == 'pos':
                    words_pos = pos_tagging(self.text_content)
                    result = "词性标注结果 (前100):\n\n"
                    for word, pos in words_pos[:100]:
                        result += f"{word}/{pos} "
                    
                    self.words_pos = words_pos
                
                self.result_data = result
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_result(result))
                self.root.after(0, lambda: self.status_bar.config(text="处理完成"))
                
            except Exception as e:
                error_msg = f"处理过程中发生错误: {str(e)}"
                self.root.after(0, lambda: self.update_result(error_msg))
                self.root.after(0, lambda: self.status_bar.config(text="处理出错"))
        
        # 启动线程
        threading.Thread(target=process_thread).start()
    
    def extract_entity(self, entity_type):
        if not hasattr(self, 'words_pos'):
            if not self.text_content:
                tk.messagebox.showinfo("提示", "请先加载文本文件")
                return
            self.words_pos = pos_tagging(self.text_content)
        
        self.status_bar.config(text="提取中...")
        
        def extract_thread():
            result = ""
            try:
                if entity_type == 'name':
                    temp_file = "temp_names.txt"
                    name_counts = extract_and_save_names(self.words_pos, temp_file)
                    result = "人名提取结果:\n\n"
                    for name, count in name_counts.most_common(30):
                        result += f"{name}: {count}\n"
                    
                    self.name_counts = name_counts
                
                elif entity_type == 'location':
                    temp_file = "temp_locations.txt"
                    location_counts = extract_and_save_locations(self.words_pos, temp_file)
                    result = "地名提取结果:\n\n"
                    for location, count in location_counts.most_common(30):
                        result += f"{location}: {count}\n"
                    
                    self.location_counts = location_counts
                
                elif entity_type == 'weapon':
                    # 假设有武器词典
                    if not os.path.exists("weapon_dict.txt"):
                        result = "错误: 武器词典文件不存在"
                    else:
                        temp_file = "temp_weapons.txt"
                        weapon_counts = extract_and_save_weapons(self.text_content, "weapon_dict.txt", temp_file)
                        result = "武器提取结果:\n\n"
                        for weapon, count in sorted(weapon_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
                            result += f"{weapon}: {count}\n"
                        
                        self.weapon_counts = weapon_counts
                
                self.result_data = result
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_result(result))
                self.root.after(0, lambda: self.status_bar.config(text="提取完成"))
                
            except Exception as e:
                error_msg = f"提取过程中发生错误: {str(e)}"
                self.root.after(0, lambda: self.update_result(error_msg))
                self.root.after(0, lambda: self.status_bar.config(text="提取出错"))
        
        # 启动线程
        threading.Thread(target=extract_thread).start()
    
    def visualize(self, viz_type):
        self.status_bar.config(text="生成可视化...")
        
        # 清除现有图形
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        def visualize_thread():
            try:
                # 创建图形
                fig = plt.Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                if viz_type == 'bar':
                    if not hasattr(self, 'word_freq'):
                        if not hasattr(self, 'segmented_words'):
                            if not self.text_content:
                                raise Exception("请先加载文本并进行分词")
                            self.segmented_words = segment_text(self.text_content)
                        self.word_freq = count_word_frequency(self.segmented_words, top_n=20)
                    
                    labels = [word for word, _ in self.word_freq[:15]]
                    values = [freq for _, freq in self.word_freq[:15]]
                    
                    ax.bar(labels, values)
                    ax.set_title("词频统计")
                    ax.set_xlabel("词语")
                    ax.set_ylabel("频率")
                    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
                    fig.tight_layout()
                
                elif viz_type == 'wordcloud':
                    if not hasattr(self, 'word_freq'):
                        if not hasattr(self, 'segmented_words'):
                            if not self.text_content:
                                raise Exception("请先加载文本并进行分词")
                            self.segmented_words = segment_text(self.text_content)
                        self.word_freq = count_word_frequency(self.segmented_words)
                    
                    word_freq_dict = dict(self.word_freq)
                    
                    # 生成词云图像并保存
                    temp_file = "temp_wordcloud.png"
                    generate_wordcloud(word_freq_dict, temp_file)
                    
                    # 在主线程中显示图像
                    self.root.after(0, lambda: self.show_image(temp_file))
                    self.root.after(0, lambda: self.status_bar.config(text="词云生成完成"))
                    return
                
                elif viz_type == 'relationship':
                    # 这里需要有关系数据
                    if not hasattr(self, 'relationships'):
                        # 使用示例关系数据
                        self.relationships = [('刘备', '关羽', 5), ('关羽', '张飞', 4), 
                                             ('刘备', '张飞', 5), ('曹操', '刘备', 3), 
                                             ('曹操', '孙权', 2), ('孙权', '刘备', 2)]
                    
                    # 生成关系图并保存
                    temp_file = "temp_relationship.png"
                    visualize_relationship_graph(self.relationships, temp_file)
                    
                    # 在主线程中显示图像
                    self.root.after(0, lambda: self.show_image(temp_file))
                    self.root.after(0, lambda: self.status_bar.config(text="关系图生成完成"))
                    return
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.show_matplotlib_figure(fig))
                self.root.after(0, lambda: self.status_bar.config(text="可视化生成完成"))
                
            except Exception as e:
                error_msg = f"可视化生成过程中发生错误: {str(e)}"
                self.root.after(0, lambda: self.update_result(error_msg))
                self.root.after(0, lambda: self.status_bar.config(text="可视化生成出错"))
        
        # 启动线程
        threading.Thread(target=visualize_thread).start()
    
    def update_result(self, text):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)
    
    def show_matplotlib_figure(self, figure):
        # 清除现有图形
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # 创建画布
        canvas = FigureCanvasTkAgg(figure, self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_image(self, image_path):
        # 清除现有图形
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # 加载并显示图像
        img = Image.open(image_path)
        # 调整图像大小以适应框架
        width, height = self.viz_frame.winfo_width(), self.viz_frame.winfo_height()
        if width > 1 and height > 1:  # 确保框架已经被正确调整大小
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img)
        
        # 创建标签来显示图像
        label = ttk.Label(self.viz_frame, image=photo)
        label.image = photo  # 保持引用以防止垃圾回收
        label.pack(fill=tk.BOTH, expand=True)
    
    def show_about(self):
        tk.messagebox.showinfo("关于", "自然语言处理系统 v1.0\n\n一个用于中文文本分析的工具")
    
    def show_help(self):
        help_text = """使用帮助:

1. 文件操作:
   - 打开文件: 加载文本文件进行分析
   - 保存结果: 保存当前分析结果

2. 文本处理:
   - 分词: 将文本分割成单词
   - 词频统计: 计算词语出现频率
   - 词性标注: 标注词语的词性

3. 实体提取:
   - 提取人名: 识别并提取文本中的人名
   - 提取地名: 识别并提取文本中的地名
   - 提取武器: 识别并提取文本中的武器名称

4. 可视化:
   - 生成柱状图: 显示词频统计结果
   - 生成词云: 创建词云可视化
   - 生成关系图: 显示实体之间的关系
"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, help_text)

# 主程序
def main():
    root = tk.Tk()
    app = NLPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
