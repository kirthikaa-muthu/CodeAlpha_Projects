from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw, wrpcap
from datetime import datetime

packet_count = 0
tcp_count = 0
udp_count = 0
icmp_count = 0
other_count = 0

captured_packets = []


def process_packet(packet):

    global packet_count
    global tcp_count
    global udp_count
    global icmp_count
    global other_count

    if IP not in packet:
        return

    packet_count += 1
    captured_packets.append(packet)

    source = packet[IP].src
    destination = packet[IP].dst
    length = len(packet)
    timestamp = datetime.now().strftime("%H:%M:%S")

    print("\n" + "=" * 65)
    print(f"Packet #{packet_count}")
    print(f"Time           : {timestamp}")
    print(f"Source IP      : {source}")
    print(f"Destination IP : {destination}")
    print(f"Packet Length  : {length} bytes")

    if TCP in packet:

        tcp_count += 1

        print("Protocol       : TCP")
        print(f"Source Port    : {packet[TCP].sport}")
        print(f"Destination Port: {packet[TCP].dport}")

    elif UDP in packet:

        udp_count += 1

        print("Protocol       : UDP")
        print(f"Source Port    : {packet[UDP].sport}")
        print(f"Destination Port: {packet[UDP].dport}")

    elif ICMP in packet:

        icmp_count += 1

        print("Protocol       : ICMP")

    else:

        other_count += 1

        print(f"Protocol       : {packet[IP].proto}")

    if Raw in packet:

        payload = packet[Raw].load

        print(f"Payload Length : {len(payload)} bytes")

        try:
            decoded = payload.decode(errors="replace")
            print(f"Payload        : {decoded[:150]}")
        except Exception:
            print(f"Payload        : {payload[:150]}")


print("=" * 65)
print("              BASIC NETWORK SNIFFER")
print("=" * 65)
print("Capturing packets...")
print("Press CTRL+C to stop.")
print()

sniff(prn=process_packet, store=False)

print("\n\n" + "=" * 65)
print("                 CAPTURE SUMMARY")
print("=" * 65)

print(f"Total packets  : {packet_count}")
print(f"TCP packets    : {tcp_count}")
print(f"UDP packets    : {udp_count}")
print(f"ICMP packets   : {icmp_count}")
print(f"Other packets  : {other_count}")

if captured_packets:
    wrpcap("capture.pcap", captured_packets)
    print("\nCapture saved as: capture.pcap")
else:
    print("\nNo IP packets were captured.")

print("=" * 65)
print("Sniffer stopped.")
