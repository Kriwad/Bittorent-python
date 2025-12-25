import hashlib
from parser import bencode
def generate_test_torrent():
    fake_piece_has = hashlib.sha1(b"fake movie torent").digest()

    torrent_data = {
        "announce": 'http://tracker.test.com/announce',
        "comment": "Testing my awesome Bencode parser",
        "created by" : "Krish khatyauda",
        "info":{
            "name": "test_movie.mp4",
            "piece_length": 262144,
            "length": 1024,
            "pieces": fake_piece_has
        }
    }


    encoded_data = bencode(torrent_data)


    with open("test.torrent", "wb") as f:
        f.write(encoded_data)
    
    print("Created 'test.torrent' successfully!")

generate_test_torrent()