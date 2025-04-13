from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, OVSController
from mininet.link import TCLink
from mininet.topo import Topo
import os, time

os.system('mn -c')

class CustomTopology(Topo):
    def build(self):
        s1 = self.addSwitch('s1', stp=True)
        s2 = self.addSwitch('s2', stp=True)
        s3 = self.addSwitch('s3', stp=True)
        s4 = self.addSwitch('s4', stp=True)

        h1 = self.addHost('h1', ip='10.1.1.2/24')
        h2 = self.addHost('h2', ip='10.1.1.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')
        h9 = self.addHost('h9')

        self.addLink(h1, h9, delay='5ms')
        self.addLink(h2, h9, delay='5ms')
        self.addLink(h9, s1, delay='5ms')
        self.addLink(h4, s2, delay='5ms')
        self.addLink(h3, s2, delay='5ms')
        self.addLink(h6, s3, delay='5ms')
        self.addLink(h5, s3, delay='5ms')
        self.addLink(h7, s4, delay='5ms')
        self.addLink(h8, s4, delay='5ms')
        self.addLink(s1, s2, delay='7ms')
        self.addLink(s3, s2, delay='7ms')
        self.addLink(s1, s3, delay='7ms')
        self.addLink(s1, s4, delay='7ms')
        self.addLink(s4, s3, delay='7ms')

def setup_network():
    network = Mininet(topo=CustomTopology(), controller=OVSController, switch=OVSKernelSwitch, link=TCLink)
    network.start()

    h1, h2, h9 = network.get('h1', 'h2', 'h9')
    h3, h4, h5, h6, h7, h8 = network.get('h3', 'h4', 'h5', 'h6', 'h7', 'h8')

    for sw in ['s1', 's2', 's3', 's4']:
        network.get(sw).cmd(f'ovs-vsctl set Bridge {sw} stp_enable=true')

    h9.cmd('ip link add name natbr type bridge')
    h9.cmd('ip link set natbr up')
    h9.cmd('ip link set h9-eth0 master natbr')
    h9.cmd('ip link set h9-eth1 master natbr')
    h9.cmd('ip addr add 10.1.1.1/24 dev natbr')

    h1.cmd('ip route add default via 10.1.1.1')
    h2.cmd('ip route add default via 10.1.1.1')

    for host in [h3, h4, h5, h6, h7, h8]:
        host.cmd('ip route add default via 10.0.0.1')

    h9.cmd('sysctl -w net.ipv4.ip_forward=1')
    h9.cmd('iptables -t nat -F')
    h9.cmd('iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth2 -j MASQUERADE')

    h9.cmd('ip addr flush dev h9-eth0')
    h9.cmd('ip addr flush dev h9-eth1')
    h9.cmd('ip addr flush dev h9-eth2')

    h9.cmd('ip link add name natbr type bridge')
    h9.cmd('ip link set natbr up')
    h9.cmd('ip link set h9-eth0 master natbr')
    h9.cmd('ip link set h9-eth1 master natbr')
    h9.cmd('ip addr add 10.1.1.1/24 dev natbr')

    h9.setIP('10.0.0.1/24', intf='h9-eth2')
    h9.cmd('ip addr add 172.16.10.10/24 dev h9-eth2')

    print("Allowing time for network initialization...")
    time.sleep(30)

    print("\nRunning full ping test across all nodes:")
    network.pingAll()

    print("\nPart A: Internal to External Communication")
    for i in range(3):
        print(f"\nTry {i+1}: h1 to h5")
        print(h1.cmd('ping -c 4 10.0.0.6'))
        print(f"\nTry {i+1}: h2 to h3")
        print(h2.cmd('ping -c 4 10.0.0.4'))

    print("\nPart B: External to Internal Communication")
    for i in range(3):
        print(f"\nTry {i+1}: h8 to h1")
        print(h8.cmd('ping -c 4 10.1.1.2'))
        print(f"\nTry {i+1}: h6 to h2")
        print(h6.cmd('ping -c 4 10.1.1.3'))

    print("\nPart C: Performance (iperf3) tests")
    h1.cmd('iperf3 -s -D')
    time.sleep(2)
    for i in range(3):
        print(f"\nBandwidth Check {i+1}: h6 to h1")
        print(h6.cmd('iperf3 -c 10.1.1.2 -t 10'))
        time.sleep(3)
    h1.cmd('pkill iperf3')

    h8.cmd('iperf3 -s -D')
    time.sleep(2)
    for i in range(3):
        print(f"\nBandwidth Check {i+1}: h2 to h8")
        print(h2.cmd('iperf3 -c 10.0.0.9 -t 10'))
        time.sleep(3)
    h8.cmd('pkill iperf3')

    network.stop()

if __name__ == '__main__':
    setup_network()
