# run_worker.py
from watchfiles import run_process

def start():
    import worker  # importa tu script real (que debe tener if __name__ == '__main__')

if __name__ == "__main__":
    run_process("worker.py", target=start)