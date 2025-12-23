import pprint


def parse_int(data, i):
    assert data[i]== ord('i') 
    i+=1
    j = data.index(b'e' , i)
    val = int(data[i : j])
    return val , j+1

def parse_str(data , i ):
    j = data.index(b':' , i)
    length = int(data[i: j])
    j +=1 
    val = data[j : j+length ]
    return val  , j + length
k = b"4:spam"
print(parse_str(k,0))

def parse_list(data , i):
    assert data[i] == ord('l')
    i+=1
    arr= []
    while data[i] != ord('e'):
        val , i  = parse_any(data , i)
        arr.append(val)
    return arr , i+1



def parse_dict(data , i ):
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
    elif chr(data[i]).isdigit():
        return parse_str(data , i)
    else:
        return data , i


def bencoding(data):
    if isinstance(data , int):
        return f'i{data}e'.encode()
    elif isinstance(data , bytes):
        return f'{len(data)}:'.encode() + data
    elif isinstance(data, list):
        encoded_data = [bencoding(item) for item in data]
        return b'l' + b"".join(encoded_data) +b'e'
    elif isinstance(data , dict):
        pass



