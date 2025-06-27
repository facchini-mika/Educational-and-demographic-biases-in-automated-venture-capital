import threading
import multiprocessing
import tkinter as tk
from tkinter import ttk, messagebox

import run_manager

# Mapping from model name to internal ID
model_mapping = {
    "OpenAI": 0,
    "Gemini": 1,
    "DeepSeek": 2,
    "Mistral": 3,
}

exp_proc: multiprocessing.Process | None = None   # reference to running experiment
stopped_by_user = False

def _run_experiment(repetitions: int, variant: str, model_ids: list[int]) -> None:
    """Set parameters on run_manager and start the experiment (blocking)."""
    run_manager.REPETITIONS = repetitions
    run_manager.CONFIG_VARIANT = variant
    run_manager.MODEL_IDS = model_ids
    run_manager.main()   # blocks until all threads in run_manager finish

def launch() -> None:
    """Validate input and start the experiment in a separate process."""
    global exp_proc, stopped_by_user
    try:
        reps = int(repetitions_var.get())
        if reps <= 0:
            raise ValueError("Repetitions must be a positive integer.")

        variant = variant_var.get()
        if variant not in {"full", "persons", "unis", "single"}:
            raise ValueError("Invalid config variant selected.")

        selected = models_listbox.curselection()
        model_ids = [model_mapping[models_listbox.get(i)] for i in selected]
        if not model_ids:
            raise ValueError("Select at least one model in the list.")

        status_var.set("Running …")
        start_btn.config(state="disabled")
        force_btn.config(state="normal")
        stopped_by_user = False

        # create experiment process
        exp_proc = multiprocessing.Process(
            target=_run_experiment,
            args=(reps, variant, model_ids),
            daemon=True,
        )

        def monitor() -> None:
            exp_proc.start()
            exp_proc.join()
            # experiment finished or was terminated
            force_btn.config(state="disabled")
            start_btn.config(state="normal")
            if stopped_by_user:
                status_var.set("Stopped ✗")
                messagebox.showinfo("Experiment stopped",
                                    "Experiment was stopped by user.")
            elif exp_proc.exitcode == 0:
                status_var.set("Finished successfully ✓")
                messagebox.showinfo("Experiment finished",
                                    "Experiment finished successfully!")
            else:
                status_var.set("Failed ✗")
                messagebox.showerror("Experiment failed",
                                     "The experiment terminated abnormally.")

        threading.Thread(target=monitor, daemon=True).start()

    except Exception as exc:
        messagebox.showerror("Input error", str(exc))

def force_quit() -> None:
    """Terminate the running experiment process immediately."""
    global exp_proc, stopped_by_user
    if exp_proc is not None and exp_proc.is_alive():
        stopped_by_user = True
        exp_proc.terminate()

root = tk.Tk()
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.title("Experiment Launcher")
# Center window on the primary screen
win_w, win_h = 360, 300
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
pos_x = (screen_w // 2) - (win_w // 2)
pos_y = (screen_h // 2) - (win_h // 2)
root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
root.focus_force()
root.resizable(False, False)

# Repetitions field
tk.Label(root, text="Repetitions:").pack(pady=(12, 0))
repetitions_var = tk.StringVar(value="1")
tk.Entry(root, textvariable=repetitions_var).pack()

# Config variant field
tk.Label(root, text="Config Variant:").pack(pady=(12, 0))
variant_var = tk.StringVar(value="single")
ttk.Combobox(
    root,
    textvariable=variant_var,
    values=("full", "persons", "unis", "single"),
    state="readonly",
).pack()

# Model selection
tk.Label(root, text="Models (select one or more):").pack(pady=(12, 0))
models_listbox = tk.Listbox(root, selectmode="multiple", height=4, exportselection=False)
for name in ("OpenAI", "Gemini", "DeepSeek", "Mistral"):
    models_listbox.insert(tk.END, name)
models_listbox.pack()

# Buttons (Start / Force Quit) side‑by‑side
btn_frame = tk.Frame(root)
btn_frame.pack(pady=18)

start_btn = tk.Button(
    btn_frame,
    text="Start Experiment",
    command=launch
)
start_btn.pack(side="left", padx=6)

force_btn = tk.Button(
    btn_frame,
    text="Force Quit",
    command=force_quit,
    state="disabled",
    fg="red"
)
force_btn.pack(side="left", padx=6)

# Status label
status_var = tk.StringVar(value="")
tk.Label(root, textvariable=status_var, fg="blue").pack(pady=(8, 12))

if __name__ == "__main__":
    root.mainloop()