# Importing necessary libraries

import psutil  
import tkinter as tk  
from tkinter import ttk, messagebox  
from datetime import datetime  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  


# Thresholds for CPU, RAM, and Disk usage (in percentage)
CPU_THRESHOLD = 80
RAM_THRESHOLD = 80
DISK_THRESHOLD = 80

# A flag to control monitoring
monitoring = True

# Log file to store resource usage alerts
LOG_FILE = "usage_log.txt"

# A dictionary to track the last alert times for resources
last_alert_time = {"CPU": 0, "RAM": 0, "Disk": 0}
ALERT_COOLDOWN = 10  

# Function to get the current system time as a formatted string

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to fetch the top 5 resource-intensive processes

def get_top_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)  
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Handle inaccessible processes gracefully
    # Sort processes by CPU and RAM usage in descending order and return the top 5
    processes = sorted(processes, key=lambda p: (p['cpu_percent'], p['memory_percent']), reverse=True)
    return processes[:5] 

# Function to get the disk usage percentage
def get_disk_usage():
    disk_usage = psutil.disk_usage('/')  # Get disk usage for the root directory
    return disk_usage.percent

# Function to update CPU, RAM, Disk usage, and top processes every second
def update_usage():
    global monitoring, last_alert_time

    if not monitoring:  
        return

    # Get system resource usage data
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    total_ram = round(ram.total / (1024 ** 3), 2)  
    used_ram = round(ram.used / (1024 ** 3), 2)  

    disk_usage = get_disk_usage()

    # Update labels in the GUI with the latest usage stats
    cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
    ram_label.config(text=f"RAM Usage: {ram_usage}% ({used_ram}/{total_ram} GB)")
    disk_label.config(text=f"Disk Usage: {disk_usage}%")
    time_label.config(text=f"Current Time: {get_current_time()}")

    # Check thresholds and show alerts if needed
    current_time = datetime.now().timestamp()
    if cpu_usage > CPU_THRESHOLD and current_time - last_alert_time["CPU"] > ALERT_COOLDOWN:
        alert_message = f"CPU usage has exceeded {CPU_THRESHOLD}%! Current usage: {cpu_usage}%"
        show_alert("CPU Usage High", alert_message)
        log_event("CPU", alert_message)
        last_alert_time["CPU"] = current_time

    if ram_usage > RAM_THRESHOLD and current_time - last_alert_time["RAM"] > ALERT_COOLDOWN:
        alert_message = f"RAM usage has exceeded {RAM_THRESHOLD}%! Current usage: {ram_usage}%"
        show_alert("RAM Usage High", alert_message)
        log_event("RAM", alert_message)
        last_alert_time["RAM"] = current_time

    if disk_usage > DISK_THRESHOLD and current_time - last_alert_time["Disk"] > ALERT_COOLDOWN:
        alert_message = f"Disk usage has exceeded {DISK_THRESHOLD}%! Current usage: {disk_usage}%"
        show_alert("Disk Usage High", alert_message)
        log_event("Disk", alert_message)
        last_alert_time["Disk"] = current_time

    # Update the list of top processes
    top_processes = get_top_processes()
    process_text = "Top Processes:\n"
    for proc in top_processes:
        process_text += f"{proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%, RAM: {proc['memory_percent']}%\n"
    process_label.config(text=process_text)

    # Schedule the function to run again after 1 second
    root.after(1000, update_usage)

# Function to display a pop-up alert message
def show_alert(title, message):
    messagebox.showwarning(title, message)

# Function to log an alert to the log file
def log_event(resource, message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()} - {resource} Alert: {message}\n")

# Function to update the thresholds for alerts
def update_thresholds():
    global CPU_THRESHOLD, RAM_THRESHOLD, DISK_THRESHOLD
    try:
        CPU_THRESHOLD = int(cpu_threshold_entry.get())
        RAM_THRESHOLD = int(ram_threshold_entry.get())
        DISK_THRESHOLD = int(disk_threshold_entry.get())
        messagebox.showinfo("Thresholds Updated", "CPU, RAM, and Disk thresholds have been updated!")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid integers for thresholds.")

# Function to clear the log file
def clear_logs():
    open(LOG_FILE, "w").close()  
    messagebox.showinfo("Logs Cleared", "Usage log file has been cleared!")

# Function to create a bar graph of CPU, RAM, and Disk usage
def create_graph():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    disk_usage = get_disk_usage()

    fig, ax = plt.subplots(figsize=(5, 4))  
    ax.bar(['CPU', 'RAM', 'Disk'], [cpu_usage, ram_usage, disk_usage], color=['red', 'green', 'blue'])
    ax.set_title('Resource Usage')
    ax.set_ylabel('Percentage (%)')
    return fig

# Function to update the graph in the GUI
def update_graph():
    fig = create_graph()
    canvas.draw()

# Tkinter GUI setup
root = tk.Tk()
root.title("Enhanced CPU & RAM Monitor Tool")
root.geometry("600x700")
root.configure(bg="#2b2b2b")  

# Title label for the GUI
title_label = tk.Label(root, text="CPU, RAM & Disk Monitor Tool", font=("Helvetica", 16, "bold"), bg="#1f1f1f", fg="white", pady=10)
title_label.pack(fill=tk.X)

# Frames for different sections of the GUI
usage_frame = tk.Frame(root, bg="#343434", padx=10, pady=10)
usage_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

process_frame = tk.Frame(root, bg="#3f3f3f", padx=10, pady=10)
process_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

graph_frame = tk.Frame(root, bg="#2b2b2b", padx=10, pady=10)
graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

button_frame = tk.Frame(root, bg="#2b2b2b", pady=10)
button_frame.pack(fill=tk.X)

# Labels for displaying resource usage
cpu_label = tk.Label(usage_frame, text="CPU Usage: 0%", font=("Helvetica", 12), bg="#343434", fg="white")
cpu_label.pack(pady=5)

ram_label = tk.Label(usage_frame, text="RAM Usage: 0%", font=("Helvetica", 12), bg="#343434", fg="white")
ram_label.pack(pady=5)

disk_label = tk.Label(usage_frame, text="Disk Usage: 0%", font=("Helvetica", 12), bg="#343434", fg="white")
disk_label.pack(pady=5)

time_label = tk.Label(usage_frame, text="Current Time: 0", font=("Helvetica", 12), bg="#343434", fg="white")
time_label.pack(pady=5)

# Label for displaying top processes
process_label = tk.Label(process_frame, text="Top Processes:", font=("Courier", 10), bg="#3f3f3f", fg="white", justify="left", anchor="nw")
process_label.pack(fill=tk.BOTH, expand=True)

# Graph embedded in the graph frame
fig = create_graph()
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
canvas.draw()

# Entry fields and buttons for threshold management
threshold_frame = ttk.Frame(root)
threshold_frame.pack(pady=10)

ttk.Label(threshold_frame, text="CPU Threshold (%): ").grid(row=0, column=0, padx=5, pady=5)
cpu_threshold_entry = ttk.Entry(threshold_frame, width=5)
cpu_threshold_entry.grid(row=0, column=1, padx=5)
cpu_threshold_entry.insert(0, str(CPU_THRESHOLD))

ttk.Label(threshold_frame, text="RAM Threshold (%): ").grid(row=1, column=0, padx=5, pady=5)
ram_threshold_entry = ttk.Entry(threshold_frame, width=5)
ram_threshold_entry.grid(row=1, column=1, padx=5)
ram_threshold_entry.insert(0, str(RAM_THRESHOLD))

ttk.Label(threshold_frame, text="Disk Threshold (%): ").grid(row=2, column=0, padx=5, pady=5)
disk_threshold_entry = ttk.Entry(threshold_frame, width=5)
disk_threshold_entry.grid(row=2, column=1, padx=5)
disk_threshold_entry.insert(0, str(DISK_THRESHOLD))

update_button = ttk.Button(threshold_frame, text="Update Thresholds", command=update_thresholds)
update_button.grid(row=3, column=0, columnspan=2, pady=10)

clear_logs_button = ttk.Button(root, text="Clear Logs", command=clear_logs)
clear_logs_button.pack(pady=10)


update_usage()
root.after(1000, update_graph)


root.mainloop()
