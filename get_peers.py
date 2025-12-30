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
    
    tracker_urls = []
    if b'announce' in decoded_file:
        tracker_urls.append(decoded_file['announce'].decode('utf-8'))
    
    if b'announce-list' in decoded_file:
        for tier in decoded_file.get(b'announce-list' , []):
            for url_bin in tier:
                url = url_bin.decode('utf-8')
                if url not in tracker_urls and url.startswith("http"):
                    tracker_urls.append(url)

    info_dict = decoded_file['info']
    info_hash = hashlib.sha1(bencode(info_dict)).digest()

    if b'length' in info_dict:
        left = info_dict.get('length' , 0)
    elif b'files' in info_dict:
        left = sum(f[b'length'] for f in info_dict[b'files'])
    else:
        raise ValueError(f"Torrent file missing 'lenght' and 'file key' ")

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

    discovered_peers = []
    for url in tracker_urls:

        try:
            if not url.startswith('http'):
                continue
            if '/scrape' in url:
                url = url.replace('/scrape', '/announce')

            response = requests.get(url , params , timeout = 10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"connection to traker failes:{e}")
            continue

        if response.status_code == 200:
            tracker_detail = bdecode(response.content)
            print("Tracker reached successfully")

            if b'failure reason' in tracker_detail:
                error_msg = tracker_detail[b'failure reason'].decode()
                print(f"Tracker reason {error_msg}")
                return []
            
            if b'peers' not in tracker_detail:
                raise ValueError(f"Tracker response missing 'peers' key ")
            
            peers_blob= tracker_detail[b'peers']

            if isinstance(peers_blob , list):
                for p in peers_blob:
                    ip = p[b'ip'].decode()
                    port = p[b'port']
                    discovered_peers.append([ip , port])
            elif isinstance(peers_blob , bytes):
                if len(peers_blob) % 6 != 0:
                    raise ValueError("Invalid compact peers format")
                
                for i in range(0 , len(peers_blob) , 6):
                    peer_bytes = peers_blob[i: i+6]
                    ip = ".".join(str(b) for b in peer_bytes[:4])
                    port = int.from_bytes(peer_bytes[4:] , byteorder='big')
                    discovered_peers.append([ip , port])
            else:
                print(f"Unknown peers format from {url}, skipping...")
                continue
            
            if discovered_peers:
                break

    return discovered_peers , info_hash , my_id


    

        




