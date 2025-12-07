from flask import Flask, render_template, request, jsonify
import sys
import os
import asyncio
import threading
import struct
from bleak import BleakClient, BleakScanner

# Add src to path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.append(src_path)

# Try importing the compatible controller
try:
    from working.mask_go_compatible import MaskGoCompatible
except ImportError as e:
    print(f"Warning: Could not import MaskGoCompatible: {e}. Live preview will be simulated.")
    class MaskGoCompatible:
        pass
    HAS_MASK_LIB = False
else:
    HAS_MASK_LIB = True

app = Flask(__name__)

# Constants for Shining Mask
MASK_WIDTH = 46  # Official Shining Mask width is often 46? User editor is 42. We'll stick to 42 for now, or pad?
# If we send 42 columns, and mask is 46, it might just be left aligned.
# Let's use the editor's dimensions.
MASK_WIDTH = 42
MASK_HEIGHT = 56 

class CustomRGBUploader(MaskGoCompatible):
    async def init_upload_image(self, total_len, image_index):
        """
        Initialize upload for High Res Image.
        Command 9: DATS + TotalLen(2) + ImageIndex(2) + 0
        """
        if not hasattr(self, 'current_upload') or self.current_upload is None:
             self.current_upload = {}
        
        self.current_upload.update({
            'total_len': total_len,
            'bytes_sent': 0,
            'packet_count': 0
            # complete_buffer is preserved or expected to be set
        })
        
        cmd = bytearray()
        cmd.append(9)  # Length
        cmd.extend(b"DATS")
        cmd.extend(struct.pack('>H', total_len)) 
        cmd.extend(struct.pack('>H', image_index))
        cmd.append(0)  # Final byte
        
        await self.send_command(cmd)
        self.upload_running = True
        # Wait for DATSOK
        await self.wait_for_response("DATSOK", timeout=5.0)

    async def upload_pixels_bishop_style(self, rgb_data, total_len, image_index=1):
        """
        Specific upload protocol based on BishopFox research + Manual Testing.
        - Pure RGB Data (No Bitmap Header)
        - DATS command with trailing 0x01
        - No waiting for DATSOK (optional/fast)
        - Fast upload loop
        """
        self.current_upload = {
            'total_len': total_len,
            'bytes_sent': 0,
            'packet_count': 0,
            'complete_buffer': rgb_data
        }

        try:
            # 1. DATS Command (BishopFox Style)
            # 09 + DATS + TotalLen(2) + Index(2) + 01
            cmd = bytearray()
            cmd.append(9)
            cmd.extend(b"DATS")
            cmd.extend(struct.pack('>H', total_len)) 
            cmd.extend(struct.pack('>H', image_index))
            cmd.append(1)  # <--- MAGIC PROTOCOL BYTE
            
            print(f"Sending DATS (Bishop Style): {cmd.hex()}")
            await self.send_command(cmd)
            self.upload_running = True
            
            # Wait for DATSOK (Good practice)
            if not await self.wait_for_response("DATSOK", timeout=5.0):
                 print("⚠️ No DATSOK response, continuing...")

            # 2. Upload Loop
            print(f"Uploading {total_len} bytes...")
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                # 50ms delay seems robust based on tests
                await asyncio.sleep(0.005) 
            
            # 3. Finish
            print("Finalizing (DATCP)...")
            cmd_fin = bytearray([5]) + b"DATCP"
            await self.send_command(cmd_fin)
            await self.wait_for_response("DATCPOK", timeout=5.0)
            
            # 4. Save
            print("Saving (SAVE01)...")
            await self.send_command(b"SAVE01")
            
            return True
            
        except Exception as e:
            print(f"Upload flow error: {e}")
            return False

async def send_to_mask(pixels_data):
    """
    Connects to mask and uploads properly formatted image data.
    """
    TARGET_WIDTH = 46
    TARGET_HEIGHT = 58
    
    # 1. Convert Frontend Data (Hex Strings) to Pillow Image
    # Frontend sends 42x56 grid
    SRC_WIDTH = 42
    SRC_HEIGHT = 56
    
    try:
        from PIL import Image
        
        # Create Source Image
        img = Image.new('RGB', (SRC_WIDTH, SRC_HEIGHT), (0,0,0))
        pixels = img.load()
        
        for i, hex_color in enumerate(pixels_data):
            if i >= SRC_WIDTH * SRC_HEIGHT: break
            
            x = i % SRC_WIDTH
            y = i // SRC_WIDTH
            
            if hex_color and hex_color != 'rgba(0, 0, 0, 0)':
                try:
                    h = hex_color.lstrip('#')
                    if len(h) == 6:
                        color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                        pixels[x, y] = color
                except:
                    pass
        
        # 2. Resize to Target Resolution (46x58)
        # Using LANCZOS for better quality upscale
        img_resized = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        
        # 3. Create RGB Buffer (COLUMN-MAJOR / Vertical Scan)
        # Scan X then Y
        rgb_buffer = bytearray()
        r_pixels = img_resized.load()
        
        for x in range(TARGET_WIDTH):
            for y in range(TARGET_HEIGHT):
                r, g, b = r_pixels[x, y]
                rgb_buffer.extend([r, g, b])
        
        # Verify Size
        expected_size = TARGET_WIDTH * TARGET_HEIGHT * 3 # 8004
        if len(rgb_buffer) != expected_size:
            print(f"⚠️ Warning: Buffer size {len(rgb_buffer)} != {expected_size}")
            
    except ImportError:
        print("❌ PIL not found, cannot process image")
        return False
        
    print(f"Ready to upload {len(rgb_buffer)} bytes pure RGB.")

    if HAS_MASK_LIB:
        mask = None
        try:
            mask = CustomRGBUploader()
            
            async def upload_logic():
                await mask.connect()
                
                # Use our Custom Bishop Logic
                await mask.upload_pixels_bishop_style(rgb_buffer, len(rgb_buffer))
                
                return True

            await asyncio.wait_for(upload_logic(), timeout=60.0)
            return True
            
        except asyncio.TimeoutError:
            print("❌ Upload timed out")
            return False
        except Exception as e:
            print(f"Error uploading: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if mask:
                await mask.disconnect()
            
    return True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    pixels = data.get('pixels', [])
    
    # Run async upload in a separate thread/loop
    # Since flask is sync, we need a wrapper
    success = False
    try:
        success = asyncio.run(send_to_mask(pixels))
    except Exception as e:
        print(f"Async Upload Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
        
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Failed to upload to mask"}), 500

if __name__ == '__main__':
    print("Starting Mask Editor Server...")
    # Running on 0.0.0.0 to allow access if needed, but local usage is fine
    app.run(debug=True, port=5001)
