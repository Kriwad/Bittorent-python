import pprint

#converts bytes into int
def parse_int(data: bytes, i:int)-> tuple[int , int]:
    assert data[i]== ord('i') 

    #checks if there is missing "e"
    if data.find(b'e' , i) == -1:
        raise ValueError("Undetermined integer (missing 'e')")

    i+=1
    j = data.index(b'e' , i)
    val = data[i : j] #converts the sliced value out into integer

    #checks if the bencoded int consist of leading"0"
    if val.startswith(b'0') and len(val)>1:
        raise ValueError("Leading zero must not be there")
    
    #checks if the bencode int only has a single - value
    if val == b'-':
        raise ValueError("Malformed integer (only a minus sign)")

    #checks if the bencode has a "-0"
    if val.startswith(b'-0'):
        raise ValueError("There should be no -0")
    
    #checks if the lenght of the data is "0"
    if len(val)==0:
        raise ValueError("Empty Integer")
    
    return int(val) , j+1

#converts bytes into str'bytes' 
def parse_str(data:bytes , i:int )-> tuple[bytes , int]:

    j = data.find(b':' , i)
    if j == -1:
        raise ValueError("Undetermined byte . Missing ':'")
    
    length_bytes = data[i: j]

    if not length_bytes.isdigit():
        raise ValueError("The length must be an integer value and shouldnt contain any -value")
        
    if len(length_bytes) > 1 and length_bytes.startswith(b'0'):
        raise ValueError("Leadin zeros are not allowed in string length")
    
    start= j +1
    end = start+ int(length_bytes)

    if end > len(data):
        raise IndexError("Data out of range")

    val = data[start : end]
    return val  , end

#converts bytes into a list
def parse_list(data:bytes, i:int , depth:int) -> tuple[list , int]:

    if len(data)-i < 2:
        raise IndexError("Data out of range")

    assert data[i] == ord('l')
    j = data.find(b'e' , i)
    if j == -1:
        raise ValueError("Undetermined list , Mising 'e'")
    
    i+=1
    arr= []
    while i< len(data) and data[i] != ord('e'):
        val , i  = parse_any(data , i , depth)
        arr.append(val)

    if i >= len(data) or data[i] != ord('e'):
        raise ValueError("List never closed: Missing 'e'")
    return arr , i+1



def parse_dict(data:bytes , i ,depth:int)-> tuple[dict , int]:
    assert data[i]== ord('d')
    i+=1 
    d={}
    last_key = None
    while i<len(data)and  data[i] != ord('e'):
        key_bytes , i = parse_str(data , i )
        if last_key is not None and key_bytes<=last_key :
            if key_bytes == last_key:
                raise ValueError(f"Duplicate key is found {key_bytes}")
            else:
                raise ValueError(f"Keys not sorted: {key_bytes} should come before {last_key}")
            
        last_key = key_bytes
        key_str = key_bytes.decode('utf-8')

        value , i = parse_any(data , i, depth)
        d[key_str] = value

    if i >= len(data) or data[i]!= ord('e'):
        raise ValueError("Dictionary never closed: Missing 'e'")
    return d , i+1

def parse_any(data , i , depth:int = 0 ):

    if depth > 100:
        raise ValueError("Nesting too deep! Possible bencode Bomb")
    if i > len(data):
        raise ValueError("Unexpected end of data")
    if data[i] == ord('l'):
        return parse_list(data , i , depth+1)
    elif data[i] == ord('i'):
        return parse_int(data , i)
    elif data[i] == ord('d'):
        return parse_dict(data , i , depth+1)
    elif ord('0') <= data[i] <= ord('9'):
        return parse_str(data , i)
    else:
        raise ValueError(f'Unknoen bencode type marker: {data[i]} , at index {i}')

def bdecode(data:bytes):
    if not isinstance(data, bytes):
        raise ValueError("Data must be byte string")
    if not data:
        raise ValueError("The data is empty")
    result , index = parse_any(data , 0)
    #checks if there is any garbage value after the byte
    if index < len(data):
        raise ValueError(f"Trailing data after bencode object at index: {index}")
    return result

def bencode(data):
    if isinstance(data , int):
        return f'i{data}e'.encode()
    
    elif isinstance(data , bytes):
        return f'{len(data)}:'.encode() + data
    
    elif isinstance(data , str):
        byte_str = data.encode('utf-8')
        return f'{len(byte_str)}:'.encode() + byte_str
    
    elif isinstance(data, list):
        encoded_list = [bencode(item) for item in data]
        return b'l' + b"".join(encoded_list) +b'e'
    
    elif isinstance(data , dict):
        items = []
        byte_items = []
        for key , value in data.items():
            key_bytes = key.encode('utf-8') if isinstance(key , str) else key
            byte_items.append((key_bytes , value))
        
        for key,value in sorted(byte_items):
            items.append(bencode(key))
            items.append(bencode(value))
            
        return b'd'+b''.join(items)+b'e'
    
    else:
        raise TypeError(f'{type(data)} is not supported by the Bencoder')


