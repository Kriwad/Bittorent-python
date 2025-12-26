import hashlib

import secrets
from parser import bdecode , bencode

def get_peers_from_tracker(torent_file):
    with open(torent_file , 'rb') as f:
        torent_content = f.read()

    decoded_file = bdecode(torent_content)
    url = decoded_file['announce'].decode('utf-8')
    info_dict = decoded_file['info']
    info_hash = hashlib.sha1(bencode(info_dict)).digest()
    total_length = info_dict.get('length' , 0)


