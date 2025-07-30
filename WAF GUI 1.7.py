import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox
import argparse
import sys

def read_chunks(file_bytes):
    chunks = []
    offset = 12
    while offset < len(file_bytes):
        chunk_id = file_bytes[offset:offset+4]
        chunk_size = struct.unpack('<I', file_bytes[offset+4:offset+8])[0]
        chunk_data = file_bytes[offset+8:offset+8+chunk_size]
        chunks.append((chunk_id, chunk_size, chunk_data))
        offset += 8 + chunk_size + (chunk_size % 2)
    return chunks

def find_chunk(chunks, name):
    for i, (cid, size, data) in enumerate(chunks):
        if cid == name:
            return i, (cid, size, data)
    return None, None

def replace_chunks(original_bytes, mod_chunks):
    riff_header = original_bytes[:12]
    original_chunks = read_chunks(original_bytes)

    for chunk_name in [b'fmt ', b'data']:
        mod_index, mod_chunk = find_chunk(mod_chunks, chunk_name)
        orig_index, _ = find_chunk(original_chunks, chunk_name)
        if mod_index is not None:
            if orig_index is not None:
                original_chunks[orig_index] = mod_chunk
            else:
                original_chunks.append(mod_chunk)

    chunks_data = b''.join(
        cid + struct.pack('<I', size) + data + (b'\x00' if size % 2 else b'')
        for cid, size, data in original_chunks
    )
    new_riff_size = len(chunks_data)
    new_riff_header = riff_header[:4] + struct.pack('<I', new_riff_size) + riff_header[8:]
    return new_riff_header + chunks_data

def process_folders(mod_folder, original_folder, output_folder, show_popup=True):
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    for mod_file in os.listdir(mod_folder):
        if mod_file.endswith('.wem'):
            id_part = mod_file.split(']')[-1].strip()
            mod_path = os.path.join(mod_folder, mod_file)

            original_match = None
            for orig_file in os.listdir(original_folder):
                if id_part in orig_file:
                    original_match = os.path.join(original_folder, orig_file)
                    break

            if not original_match:
                print(f"[WARN] Original not found for {mod_file}")
                continue

            output_path = os.path.join(output_folder, mod_file)

            with open(original_match, 'rb') as f_orig:
                original_bytes = f_orig.read()
            with open(mod_path, 'rb') as f_mod:
                mod_bytes = f_mod.read()

            mod_chunks = read_chunks(mod_bytes)
            final_bytes = replace_chunks(original_bytes, mod_chunks)

            with open(output_path, 'wb') as f_out:
                f_out.write(final_bytes)

            print(f"[OK] Created: {output_path}")
            count += 1

    if show_popup:
        messagebox.showinfo("Done", f"Patched {count} files.")
    else:
        print(f"Patched {count} files.")

# --- GUI Setup ---
def run_gui():
    root = tk.Tk()
    root.title("WEM Animation Fixer")
    root.geometry("500x300")

    paths = {"mod": "", "original": "", "output": ""}

    def select_folder(key):
        folder = filedialog.askdirectory()
        if folder:
            paths[key] = folder
            entries[key].delete(0, tk.END)
            entries[key].insert(0, folder)

    entries = {}

    for i, (key, label_text) in enumerate([
        ("mod", "Modded Folder"),
        ("original", "Original Folder"),
        ("output", "Output Folder")
    ]):
        tk.Label(root, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=5)
        entry = tk.Entry(root, width=40)
        entry.grid(row=i, column=1, padx=10)
        entries[key] = entry
        tk.Button(root, text="Browse", command=lambda k=key: select_folder(k)).grid(row=i, column=2)

    def on_process():
        if all(paths.values()):
            try:
                process_folders(paths["mod"], paths["original"], paths["output"])
            except Exception as e:
                messagebox.showerror("Error", f"Processing failed:\n{e}")
        else:
            messagebox.showwarning("Missing Input", "Please select all folders.")

    tk.Button(root, text="Start", command=on_process, width=20).grid(row=4, column=1, pady=20)

    root.mainloop()

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="WEM Animation Fixer")
    parser.add_argument('--mod', help='Path to modded .wem folder')
    parser.add_argument('--original', help='Path to original .wem folder')
    parser.add_argument('--output', help='Path to output folder')
    args = parser.parse_args()

    if args.mod and args.original and args.output:
        process_folders(args.mod, args.original, args.output, show_popup=False)
    else:
        run_gui()

if __name__ == "__main__":
    main()
    