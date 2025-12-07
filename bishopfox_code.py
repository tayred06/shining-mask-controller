import time
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.services.nordic import Service
from adafruit_ble.uuid import VendorUUID, UUID
from adafruit_ble import BLEConnection
import _bleio as bleio
from aesio import AES, MODE_ECB

import bfox

# Fixed list of MAC addresses to ignore. You can put your own mask's
# MAC address here to prevent it from being changed. Use the last 
# 6 digits of your mask name as the last 6 digits here. For example,
# MASK-123456 in the example below.
IGNORE_LIST = [
    # "98:74:2f:12:34:56",  # Example MAC address to ignore
]


def mask_encrypt(value):
        key = b'\x32\x67\x2f\x79\x74\xad\x43\x45\x1d\x9c\x6c\x89\x4a\x0e\x87\x64'
        cipher = AES(key, MODE_ECB)
        e_msg = bytearray(16)
        cipher.encrypt_into(value, e_msg)
        return e_msg


class MaskService(Service):
    # pylint: disable=no-member
    uuid = VendorUUID("0000fff0-0000-1000-8000-00805f9b34fb")

    cmd = Characteristic(uuid=VendorUUID("d44bc439-abfd-45a2-b575-925416129600"), properties=Characteristic.WRITE, max_length=128)
    upload = Characteristic(uuid=VendorUUID("d44bc439-abfd-45a2-b575-92541612960a"), properties=Characteristic.WRITE_NO_RESPONSE, max_length=100)

    def __init__(self, service=None):
        super().__init__(service=service)
        self.connectable = True


class BLEConnectionFIXED(BLEConnection):
    def _discover_remote(self, uuid: UUID) -> bleio.Service:
        remote_service = None
        if uuid in self._discovered_bleio_services:
            remote_service = self._discovered_bleio_services[uuid]
        else:
            results = self._bleio_connection.discover_remote_services()
            # There's a bug where discover_remote_services doesn't filter by UUID properly
            # so we have to do it ourselves here. I suspect it's related to 
            # https://github.com/adafruit/Adafruit_Blinka_bleio/issues/66.
            results = [s for s in results if s.uuid == uuid.bleio_uuid]

            if results:
                remote_service = results[0]
                self._discovered_bleio_services[uuid] = remote_service
        
        return remote_service


def mask_connect_and_act(connection: BLEConnection) -> bool:
    if connection is None:
        print("[ERROR] Empty connection was given!")
        return False
    
    if not connection.connected:
        print("[ERROR] Connection is not connected!")
        return False

    try:
        # Cast connection to our custom BLEConnection to use the overridden method
        connection = BLEConnectionFIXED(connection._bleio_connection)

        mask_service = connection[MaskService]

        if mask_service is None:
            print("[ERROR] Mask Service is None after accessing connection[]")
            connection.disconnect()
            return False

        # From this point on we can send messages to do what we need.
        # mask_service.cmd = mask_encrypt(b'\x06PLAY\x01' + int(2).to_bytes(1,'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b')

        print("[INFO] Connected to mask, starting face change process...")
        # Tell the mask we want to upload a new face
        data = mask_encrypt(b"\x09\x44\x41\x54\x53\x1f\x44\x00\x01\x01\x00\x00\x00\x00\x00\x00")
        mask_service.cmd = data
        time.sleep(0.1) # small delay to allow mask to process

        # Upload the face data in chunks
        for data_chunk in bfox.upload_bfox_face:
            mask_service.upload = data_chunk
            time.sleep(0.1)  # small delay to avoid overwhelming the mask
        
        print("[INFO] Finished uploading face data.")

        # Tell the mask we are done uploading
        mask_service.cmd = mask_encrypt(b"\x09\x44\x41\x54\x43\x50\xff\xf9\xc5\x07\x00\x00\x00\x00\x00\x00")

        print("[INFO] Successfully uploaded the mask face")
        connection.disconnect()
        return True
        
    except Exception as e:
        print("[ERROR] Something went wrong: ", str(e))
        if connection.connected:
            try:
                connection.disconnect()
            except:
                pass
        return False

# PyLint can't find BLERadio for some reason so special case it here.
ble = adafruit_ble.BLERadio()  # pylint: disable=no-member

# Stores a list of found connections to avoid duplicates
connection_addr_list = []

# Add ignored addresses to the connection list to skip them
for ignore_addr in IGNORE_LIST:
    tmp_str = ""
    for b in ignore_addr.split(":")[::-1]:
        tmp_str += b

    connection_addr_list.append(tmp_str)
    print("[INFO] Ignoring address: " + ignore_addr)

print("[INFO] Starting main processing loop")
while True:
    advertisements = ble.start_scan(ProvideServicesAdvertisement, timeout=5)

    for adv in advertisements:
        # This allows us to skip addresses we've already seen, or that have been ignored
        if adv.address.address_bytes.hex() in connection_addr_list:
            continue

        addr = adv.address.address_bytes
        connection_addr_list.append(addr.hex())

        if MaskService in adv.services: 
            ble.stop_scan()             
            mask_connect_and_act(ble.connect(adv))

    time.sleep(0.1)  # debounce delay
