import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 项目目录（Git仓库目录）
PROJECT_DIR = "e:\\BaiduSyncdisk\\heat-transfer-monitor"

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
        # 避免频繁触发，设置冷却时间（秒）
        self.cooldown = 10
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        current_time = time.time()
        # 检查是否在冷却期内
        if current_time - self.last_modified < self.cooldown:
            return
        
        self.last_modified = current_time
        print(f"文件更新: {event.src_path}，触发Git自动化流程...")
        self.git_commit_and_push()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        current_time = time.time()
        if current_time - self.last_modified < self.cooldown:
            return
        
        self.last_modified = current_time
        print(f"文件创建: {event.src_path}，触发Git自动化流程...")
        self.git_commit_and_push()
    
    def git_commit_and_push(self):
        try:
            # 切换到Git仓库目录
            os.chdir(PROJECT_DIR)
            
            # 检查是否有修改
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not status_result.stdout.strip():
                print("没有检测到代码变化，跳过提交")
                return
            
            # 暂存所有修改
            subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                check=True
            )
            print("已暂存所有修改")
            
            # 生成Commit Message
            commit_msg = "自动提交: 代码更新 " + time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 提交代码
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"提交成功: {commit_msg}")
            print(commit_result.stdout)
            
            # 推送代码到远程仓库
            push_result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                check=True
            )
            print("推送成功！")
            print(push_result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"Git命令执行失败: {e}")
            print(f"错误输出: {e.stderr}")
        except Exception as e:
            print(f"发生错误: {e}")

def main():
    print(f"启动自动Git同步守护进程，监控目录: {PROJECT_DIR}")
    print(f"冷却时间: {CodeChangeHandler().cooldown}秒")
    print("按 Ctrl+C 停止守护进程...")
    
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, PROJECT_DIR, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到停止信号，正在退出...")
        observer.stop()
    observer.join()
    print("守护进程已停止")

if __name__ == "__main__":
    main()
