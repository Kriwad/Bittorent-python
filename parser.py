import pprint

#converts bencoded int into bdecoded int
def parse_int(data: bytes, i:int)-> tuple[int , int]:
    assert data[i]== ord('i') 

    #checks if there is missing "e"
    if data.find(b'e' , i) == -1:
        raise ValueError("Undetermined integer (missing 'e')")

    i+=1
    j = data.index(b'e' , i)
    val = data[i : j] #converts the sliced value out into integer

    #checks if the bencoded int only consist of "0"
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
        raise IndexError("Data out of index")

    val = data[start : end]
    return val  , end

def parse_list(data:bytes, i:int) -> list:
    assert data[i] == ord('l')
    i+=1
    arr= []
    while data[i] != ord('e'):
        val , i  = parse_any(data , i)
        arr.append(val)
    return arr , i+1



def parse_dict(data:bytes , i )-> dict:
    assert data[i]== ord('d')
    i+=1 
    d={}
    while data[i] != ord('e'):
        keys , i = parse_str(data , i )
        value , i = parse_any(data , i)
        d[keys] = value
    return d , i+1

def parse_any(data , i):
    if data[i] == ord('l'):
        return parse_list(data , i)
    elif data[i] == ord('i'):
        return parse_int(data , i)
    elif data[i] == ord('d'):
        return parse_dict(data , i)
    elif ord('0') <= data[i] <= ord('9'):
        return parse_str(data , i)
    else:
        return data , i


def bencoding(data):
    if isinstance(data , int):
        return f'i{data}e'.encode()
    
    elif isinstance(data , bytes):
        return f'{len(data)}:'.encode() + data
    
    elif isinstance(data, list):
        encoded_list = [bencoding(item) for item in data]
        return b'l' + b"".join(encoded_list) +b'e'
    
    elif isinstance(data , dict):
        arr = []
        for key , value in sorted(data.items()):
            if not isinstance(data, bytes):
                raise TypeError(f'Bencode dictionary keys must be bytes , not {type(key)}')
            arr.append(bencoding(key))
            arr.append(bencoding(value))
            
        return b'd'+b''.join(arr)+b'e'
    
    else:
        raise TypeError(f'{type(data)} is not supported by the Bencoder')


