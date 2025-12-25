
import hashlib
from parser import bdecode , bencode

def open_torrent(torent_file):
    with open(torent_file , 'rb') as f:
        torent_data = f.read()
    
    decoded_torent = bdecode(torent_data)
    if 'info' not in decoded_torent:
        raise ValueError("Torent file doesnot contain any 'info' dictionary")
    
    info_dict = decoded_torent['info']

    info_bencode = bencode(info_dict)

    info_hash= hashlib.sha1(info_bencode).digest()

    return info_hash