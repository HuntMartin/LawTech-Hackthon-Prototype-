import subprocess
import platform
import time

def run_in_new_terminal(command, title):
    system = platform.system()

    if system == 'Darwin':  # macOS
        # Using AppleScript to open new Terminal window and run command
        apple_script = f'''
        tell application "Terminal"
            activate
            do script "echo '{title}'; {command}"
        end tell
        '''
        subprocess.run(['osascript', '-e', apple_script])
    
    elif system == 'Linux':
        # For GNOME Terminal (adjust if you use another terminal)
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'echo "{title}"; {command}; exec bash'])
    
    elif system == 'Windows':
        # Windows example using start cmd, PowerShell or Windows Terminal (adjust as needed)
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
    
    else:
        print(f"Unsupported OS: {system}")

if __name__ == '__main__':
    # Command to run Flask app (adjust if needed)
    flask_command = 'cd /Users/yuanyizhao/Downloads/Hackthon_LegalTech/buildingPrototype && source /Users/yuanyizhao/Downloads/Hackthon_LegalTech/buildingPrototype/bin/activate && python /Users/yuanyizhao/Downloads/Hackthon_LegalTech/buildingPrototype/app.py'
    
    # Command to run Node.js server (adjust path if needed)
    node_command = 'node /Users/yuanyizhao/Downloads/Hackthon_LegalTech/buildingPrototype/index.js'

    run_in_new_terminal(flask_command, "Flask App")
    time.sleep(1)  # small delay to separate startup
    run_in_new_terminal(node_command, "Node.js API")
