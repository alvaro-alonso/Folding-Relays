import json
from pprint import pprint
import hashlib
import binascii
import sys


def littleEndian(string):
    splited = [str(string)[i:i + 2] for i in range(0, len(str(string)), 2)]
    splited.reverse()
    return "".join(splited)

def write_prety_print_json(file_name: str, output) -> None:
    assert(file_name[-5:] == ".json")
    with open(file_name, "w") as output_file:
        output_file.write(
            json.dumps(output, indent=4)
        )

# convert a long string of numbers into a u32 array (the format of zokrates)
def string_to_u32(val: str) -> [int]:
    byte_array = bytes.fromhex(val)
    u32_array = [str(int.from_bytes(byte_array[i:i+4], "big")) for i in range(0,len(byte_array), 4)]
    return u32_array

#
def createZokratesInputFromBlock(block):
    version = littleEndian(block['versionHex'])
    little_endian_previousHash = littleEndian(block['previousblockhash']) if block['height'] > 0 else 64 * '0'
    little_endian_merkleRoot = littleEndian(block['merkleroot'])
    little_endian_time = littleEndian(hex(block['time'])[2:])
    little_endian_difficultyBits = littleEndian(block['bits'])
    nonce = hex(block['nonce'])[2:]
    nonce = '0' * (8 - len(nonce)) + nonce #ensure nonce is 4 bytes long
    little_endian_nonce = littleEndian(nonce)
    header = version + little_endian_previousHash + little_endian_merkleRoot + little_endian_time + little_endian_difficultyBits + little_endian_nonce

    # used for debugging
    # print(f"version: {version}\nlittle_endian_previousHash: {string_to_u32(little_endian_previousHash)}")

    return header

# source form: https://www.herongyang.com/Bitcoin/Block-Data-Block-Hash-Calculation-in-Python.html
def bitcoin_hash(header:str) -> str:
    header = binascii.unhexlify(header)
    result_1024 = hashlib.sha256(header).digest()
    hash_result_256 = hashlib.sha256(result_1024).digest()
    hash_result =  binascii.hexlify(hash_result_256)

    # used for debugging
    # print("1024 hash: " + ", ".join([f"0x{result_1024[i:i+4].hex()}" for i in range(0, len(result_1024), 4)]))
    # print("256 hash: " + ", ".join([f"0x{hash_result_256[i:i+4].hex()}" for i in range(0, len(hash_result_256), 4)]))
    
    return bytes.hex(binascii.unhexlify(hash_result)[::-1])

# return an array of blocks ready to consume from the test/data
def read_blocks(number_of_blocks: int) -> [dict]:
    with open("./data/ten_btc_blocks.json", "r") as json_data:
        d = json.load(json_data)
        json_data.close()

    return [d[i]['http_responses'][2][0]['result'] for i in range(number_of_blocks)]
    

# generate the witness string for a number of blocks
def generate_witness(number_of_blocks: int) -> str:
    assert(number_of_blocks <= 10)
    data = read_blocks(number_of_blocks)
    headers = [createZokratesInputFromBlock(block) for block in data]
    
    # QA 
    hashes = [bitcoin_hash(header) for header in headers][:-1]
    previous_hashes = [block['previousblockhash'] for block in data[1:]]
    for (hash, prev_hash) in zip(hashes, previous_hashes):
        assert(hash == prev_hash)

    # put together witness
    zok_headers = [string_to_u32(header) for header in headers]
    first_prev_block_hash = string_to_u32(littleEndian(data[0]['previousblockhash']))
    witness = first_prev_block_hash + [y for x in zok_headers for y in x]
    assert(len(witness) == 8 + (20 * number_of_blocks))
    write_prety_print_json("../circuit/init.json", first_prev_block_hash)
    headers = []
    for header in zok_headers:
        headers.append([header[i:i+4] for i in range(0, len(header), 4)])

    write_prety_print_json("../circuit/steps.json", headers)
    return ' '.join(witness)

if __name__ == '__main__':
    number_of_blocks = sys.argv[1]
    try:
        blocks_int = int(number_of_blocks)
        assert(blocks_int <= 10 and blocks_int > 0)
        blocks = generate_witness(blocks_int)
    except ValueError:
        print("Unable to parse code as an integer")
        sys.exit(1)
    except AssertionError:
        print("block number most be between 1 and 10")
        sys.exit(1)
    
    
    