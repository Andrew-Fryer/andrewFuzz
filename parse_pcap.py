import sys
import dpkt
from bitarray import bitarray
import itertools
import socket

from src.core.BinaryStream import BinaryStream
from test_dir.dns import dns
# from .csv import save_to_csv

def save_to_csv(list_of_lists, filename='tmp.csv', header=None):
    with open(filename, 'w') as f:
        if header != None:
            f.write(', '.join(header) + '/n')
        f.writelines(', '.join(str(x) for x in row) + '\n' for row in list_of_lists)

from time import time

print(dns.features([]))
base_fv = dns.vectorize()

# if len(sys.argv) != 2:
#   print("Please provide one arg (a pcap file).")
#   sys.exit()

# pcap_file = sys.argv[1]
pcap_file = "../dns_all_rr_types_udp.pcap"
f = open(pcap_file, "rb")
pcap = dpkt.pcapng.Reader(f)
pcap_elements = list(pcap)
f.close()

start_time = time()

num_parsed = 0
num_skipped = 0
num_failed = 0

def pcap_element_to_dns(pcap_element):
  ts, buf = pcap_element
  eth = dpkt.ethernet.Ethernet(buf)
  ip = eth.data
  udp = ip.data
  dns = udp.data
  return dns

def dns_bin_is_req(dns_bin):
  return not dns_bin[3] & (1 << 7)

def run_sut(dns_bin):
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.10) # timeout after 100 milliseconds
    sock.sendto(dns_bin, ('1.1.1.1', 53))
    data, _ = sock.recvfrom(4096)
    return data
  except TimeoutError:
    print('sut timed out')
  finally:
    sock.close()
  return None

n = 0
# js = []
i = 0
old_fv_list = None
corpus_feature_vectors = []
fuzzy_feature_vectors = []
corpus = {}
for pcap_element in pcap_elements:
  dns_bin = pcap_element_to_dns(pcap_element)
  
  if dns_bin == b'':
    num_skipped += 1
    continue
  if not dns_bin_is_req(dns_bin):
    num_skipped += 1
    continue

  ba = bitarray()
  ba.frombytes(dns_bin)
  stream = BinaryStream(ba)
  parse_results = list(dns.parse(stream))
  # print('here, parse results:', parse_results)
  if len(parse_results) == 1:
    req, empty_stream = parse_results[0].get_tuple()
    req_fv = req.vectorize()
    # print('dist to base:', base_fv.dist(fv))
    req_fv_list = req_fv.to_list()

    req_bin = req.serialize().tobytes()
    assert(req_bin == dns_bin)
    sut_start_time = time()
    res_bin = run_sut(req_bin)
    sut_end_time = time()
    sut_time = sut_end_time - sut_start_time
    if res_bin != None:
      ba = bitarray()
      ba.frombytes(res_bin)
      stream = BinaryStream(ba)
      res_parse_results = list(dns.parse(stream))
      if len(res_parse_results) == 1:
        res, empty_stream = res_parse_results[0].get_tuple()
        res_fv = res.vectorize()
        res_fv_list = res_fv.to_list()
        fv_list = req_fv_list + res_fv_list + [sut_time]
        fv_tuple = tuple(fv_list)
        if fv_tuple not in corpus:
          corpus[fv_tuple] = req
      elif len(parse_results) > 1:
        print('found ambiguous packet')
      else:
        print('failed to parse response')
    else:
      pass
      # fv_list = req_fv_list + [0] * 16 + [sut_time]
      # fv_tuple = tuple(fv_list)
      # if fv_tuple not in corpus:
      #   corpus[fv_tuple] = req
    # break
  elif len(parse_results) > 1:
    print('found ambiguous packet')
  else:
    num_failed += 1
    # break
  # js.append(j)
  i += 1

print('the size of the corpus is:', len(corpus))
for i in range(5):
  prev_corpus = dict(corpus)
  # corpus = {}
  for data_model in list(corpus.values()):
    fuzz_iters = [] #[data_model.fuzz()]
    for other in list(corpus.values()):
      if other == data_model:
        continue
      fuzz_iters.append(data_model.breed(other))
    j = 0
    for f in itertools.chain.from_iterable(fuzz_iters):
      # print(f.serialize())
      j += 1
      fuzzy_fv = f.vectorize()
      fuzzy_fv_list = fuzzy_fv.to_list()
      fuzzy_fv_tuple = tuple(fuzzy_fv_list)
      if fuzzy_fv_tuple not in corpus:
        corpus[fuzzy_fv_tuple] = f
      # break
  print('the size of the corpus is:', len(corpus))
end_time = time()
elapsed_time = end_time - start_time

print("parsed:", num_parsed, "skipped:", num_skipped, "failed:", num_failed)
print("generated {} fuzzy packets in {} seconds".format(n, elapsed_time))
# print(js)
print()
