import hashlib
import requests
import secrets
from parser import bdecode , bencode

def get_peers_from_tracker(torent_file, port = 6881):
    with open(torent_file , 'rb') as f:
        torent_content = f.read()

    decoded_file = bdecode(torent_content)
    #checks if announce os there in torrent file 
    if b'announce' not in decoded_file:
        raise ValueError("Torrent file missing 'announce'")
    
    tracker_urls = []
    #checks if there is announce and announce-list
    if b'announce' in decoded_file:
        tracker_urls.append(decoded_file[b'announce'].decode('utf-8'))
    
    if b'announce-list' in decoded_file:
        for tier in decoded_file.get(b'announce-list' , []):
            for url_bin in tier:
                url = url_bin.decode('utf-8')
                if url not in tracker_urls and url.startswith("http"):
                    tracker_urls.append(url)

    info_dict = decoded_file[b'info']
    info_hash = hashlib.sha1(bencode(info_dict)).digest()

    #returns 0 if there is no length in the info dictionary
    if b'length' in info_dict:
        left = info_dict[b'length']

    #checks if there is list of files instead of length
    elif b'files' in info_dict:
        left = sum(f[b'length'] for f in info_dict[b'files'])
    else:
        raise ValueError(f"Torrent file missing 'length' and 'file key' ")

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
    #list to store the discovered peers
    discovered_peers = []

    #looping throught the url we got 
    for url in tracker_urls:

        #trying to see if the tracker server is hanging or not
        try:

            import urllib.parse
            #turn characters like . / and space into a % symbol followed by its hex code
            encoded_info_hash = urllib.parse(info_dict, safe = '')
            encoded_peer_id = urllib.parse(my_id, safe = '' )

            query_string = {
                f"info_hash={encoded_info_hash}"
                f"&peer_id={encoded_peer_id}"
                f"&port={params["port"]}"
                f"&uploaded={params["uploaded"]}"
                f"&downloaded={params["downloaded"]}"
                f"&compact={params["compact"]}"
                f"&event={params["event"]}"
                f"&left={params["left"]}"
            }
            if '/scrape' in url:
                url = url.replace('/scrape', '/announce')
            
            connector = "&" if "?" in url else "?"
            full_url = f"{url}{connector}{query_string}"

            headers= {"User_Agent":"BitTorrent/1.0"}

            response = requests.get(full_url , headers=headers , timeout = 10)
            response.raise_for_status()

        #continues to try the other url if one is hanging
        except requests.exceptions.RequestException as e:
            print(f"connection to traker failes:{e}")
            continue


        if response.status_code == 200:
            tracker_detail = bdecode(response.content)
            print("Tracker reached successfully")

        #sends error message if the tracker send some failure reason
            if b'failure reason' in tracker_detail:
                error_msg = tracker_detail[b'failure reason'].decode('utf-8')
                print(f"Tracker reason {error_msg}")
                continue
            
        #shows small notes that the tracker might have for you
            if b'warning message' in tracker_detail:
                warning = tracker_detail[b'warning message'].decode('utf-8')
                print(f'Tracker warning ({url}): {warning}')

        # sees if the tracker sent the list of peer or not
            current_peer_blobs = [] 
            if b'peers' in tracker_detail:
                current_peer_blobs.append((tracker_detail[b'peers'] , 6))
            
            if b'peers6' in tracker_detail:
                current_peer_blobs.append((tracker_detail[b'peers6'], 18))
            
            if not current_peer_blobs:

                print(f"Skipping {url}: No peers or peers6 key found")
                continue 
            
            #handles if the peers are in list instead of compact 1 format
            for peers_blob , stride in current_peer_blobs:

                if isinstance(peers_blob , list):
                    for p in peers_blob:
                        ip = p.get(b'ip' , b"").decode('utf-8')
                        port = p.get(b'port' , 0)
                        if ip and port:
                            discovered_peers.append([ip , port])
                        else:
                            print("Found a malformed peer entry in list , skipping one peer....")
                #Handles when the peers repsonse is in bytes
                elif isinstance(peers_blob , bytes): 

                    if len(peers_blob) % stride != 0:
                        print(f"Skipping {url}: Compact list length is not a multiple of {stride}")
                        continue
                    
                    for i in range(0 , len(peers_blob) , stride):
                        ip_bytes = peers_blob[i: i+(stride-2)]
                        port_bytes = peers_blob[i+(stride-2) :  i+stride]
                        port = int.from_bytes(port_bytes , byteorder='big')

                        if stride == 6:
                            ip = ".".join(map(str , ip_bytes))
                        else:
                            import ipaddress
                            ip = str(ipaddress.IPv6Address(ip_bytes))
                        
                        if ip == '0.0.0.0' or ip == "::" or port == 0:
                            continue
                        
                        discovered_peers.append([ip , port])
                    
            #continues with other url if the peer format is unkown 
            else:
                print(f"Unknown peers format from {url}, skipping...")
                continue
    
    unique_peer = []
    seen_peer = set()
    for ip , port in discovered_peers:
        if (ip , port) not in seen_peer:
            unique_peer.append([ip , port])
            seen_peer.add((ip , port))

    print(f"Total unique peers found: {len(unique_peer)}")
    return unique_peer , info_hash , my_id

