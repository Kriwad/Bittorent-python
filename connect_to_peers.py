import hashlib
import requests
import secrets
from parser import bdecode , bencode

def get_peers_from_tracker(torent_file, port = 6881):
    with open(torent_file , 'rb') as f:
        torent_content = f.read()

    decoded_file = bdecode(torent_content)
    if b'announce' not in decoded_file:
        raise ValueError("Torrent file missing 'announce'")
    
    url = decoded_file['announce'].decode('utf-8')
    info_dict = decoded_file['info']
    info_hash = hashlib.sha1(bencode(info_dict)).digest()

    if b'length' in info_dict:
        left = info_dict.get('length' , 0)
    else:
        raise ValueError("Info Dictionary missing 'length'")

    my_id = b'-PC0001-' + secrets.token_bytes(12)

    params= {
        'peer_id': my_id,
        'info_hash': info_hash,
        'uploaded': 0,
        'downloaded': 0,
        'compact': 1,
        'left': left,
        'port': port,
        'event': 'started'
    }

    response = requests.get(url , params)
    if response.status_code == 200:
        tracker_detail = bdecode(response.content)
        print("Tracker reached successfully")
    else:
        print(f"Failed to reach tracker:{response.status_code}")

    peers_blob= tracker_detail[b'peer']
    discovered_peers = []
    
    for i in range(0 , len(peers_blob) , 6):
        peer_bytes = peers_blob[i: i+6]

        ip = ".".join(str(b) for b in peer_bytes[:4])
        port = int.from_bytes(peer_bytes[4:] , byteorder='big')

        discovered_peers.append([ip , port])
    

        




