import psutil

mem = psutil.virtual_memory()

def to_gb(bytes_val):
    return bytes_val / (1024 ** 3)

print(f"Total: {to_gb(mem.total):.2f} GB")
print(f"Available: {to_gb(mem.available):.2f} GB")
print(f"Used: {to_gb(mem.used):.2f} GB")
print(f"Free: {to_gb(mem.free):.2f} GB")



cpu_percent = psutil.cpu_percent(interval=1)
print(f"CPU Usage: {cpu_percent}%")