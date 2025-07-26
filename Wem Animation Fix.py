import os
import struct

def read_chunks(file_bytes):
    """Reads all RIFF chunks from a WEM file"""
    chunks = []
    offset = 12  # Skip RIFF header
    while offset < len(file_bytes):
        chunk_id = file_bytes[offset:offset+4]
        chunk_size = struct.unpack('<I', file_bytes[offset+4:offset+8])[0]
        chunk_data = file_bytes[offset+8:offset+8+chunk_size]
        chunks.append((chunk_id, chunk_size, chunk_data))
        offset += 8 + chunk_size + (chunk_size % 2)  # Align to even byte
    return chunks

def find_chunk(chunks, name):
    for i, (cid, size, data) in enumerate(chunks):
        if cid == name:
            return i, (cid, size, data)
    return None, None

def replace_chunks(original_bytes, mod_chunks):
    """Replaces 'fmt ' and 'data' chunks in the original with those from mod"""
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

def process_folders(mod_folder, original_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for mod_file in os.listdir(mod_folder):
        if mod_file.endswith('.wem'):
            id_part = mod_file.split(']')[-1].strip()
            mod_path = os.path.join(mod_folder, mod_file)

            # Find original by partial ID
            original_match = None
            for orig_file in os.listdir(original_folder):
                if id_part in orig_file:
                    original_match = os.path.join(original_folder, orig_file)
                    break

            if not original_match:
                print(f"[WARN] Original not found for {mod_file}")
                continue

            # Use the modded filename (with brackets) for output
            output_path = os.path.join(output_folder, mod_file)

            # Read both files
            with open(original_match, 'rb') as f_orig:
                original_bytes = f_orig.read()
            with open(mod_path, 'rb') as f_mod:
                mod_bytes = f_mod.read()

            mod_chunks = read_chunks(mod_bytes)
            final_bytes = replace_chunks(original_bytes, mod_chunks)

            with open(output_path, 'wb') as f_out:
                f_out.write(final_bytes)

            print(f"[OK] Created: {output_path}")

# 📁 Folder paths (change if needed)
process_folders(
    mod_folder=r'D:\Games\backups\Wem Mod',
    original_folder=r'D:\Games\backups\Wem Original',
    output_folder=r'D:\Games\backups\Working Wem'
)
