import sys
from bitarray import bitarray

from src.core.BinaryStream import BinaryStream
from test_dir.dns import dns

input_file = sys.argv[1]
output_file = sys.argv[2]

dns_bin = None
with open(input_file, 'rb') as f:
    dns_bin = f.read()

ba = bitarray()
ba.frombytes(dns_bin)
stream = BinaryStream(ba)
parse_results = list(dns.parse(stream))
if len(parse_results) != 1:
    exit(1)
data_model, empty_stream = parse_results[0].get_tuple()

fv = data_model.vectorize()
with open(output_file, mode='w') as f:
    f.write(', '.join([str(x) for x in fv.to_list()]) + '\n')
