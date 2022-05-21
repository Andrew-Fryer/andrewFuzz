import sys
import dpkt
from bitarray import bitarray

from src.core.BinaryStream import BinaryStream
from test_dir.dns import dns

# if len(sys.argv) != 2:
#   print("Please provide one arg (a pcap file).")
#   sys.exit()

# pcap_file = sys.argv[1]
pcap_file = "../dns.pcap"
f = open(pcap_file, "rb")
pcap = dpkt.pcapng.Reader(f)
pcap_elements = list(pcap)
f.close()

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

i = 0
for pcap_element in pcap_elements:
  dns_bin = pcap_element_to_dns(pcap_element)
  
  if dns_bin == b'':
    num_skipped += 1
    continue
  dns_bin = pcap_element_to_dns(pcap_element)
  ba = bitarray()
  ba.frombytes(dns_bin)
  stream = BinaryStream(ba)
  parse_results = list(dns.parse(stream))
  print('here, parse results:', parse_results)
  if len(parse_results) == 1:
    parsed_packet, empty_stream = parse_results[0].get_tuple()
    num_parsed += 1
    print(parsed_packet)
    for f in parsed_packet.fuzz():
      print(f.serialize())
      break
    # break
  elif len(parse_results) > 1:
    print('found ambiguous packet')
  else:
    num_failed += 1
    # break
  i += 1

print("parsed:", num_parsed, "skipped:", num_skipped, "failed:", num_failed)
print()
