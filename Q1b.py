from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import OVSSwitch, OVSController
import os
import time

# Reset Mininet state
os.system('mn -c')

class NetworkLayout(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.2/24')
        h2 = self.addHost('h2', ip='10.0.0.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')

        # Inter-switch links
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')

        # Host-to-switch links
        self.addLink(h1, s1, cls=TCLink, delay='5ms')
        self.addLink(h2, s1, cls=TCLink, delay='5ms')
        self.addLink(h3, s2, cls=TCLink, delay='5ms')
        self.addLink(h4, s2, cls=TCLink, delay='5ms')
        self.addLink(h5, s3, cls=TCLink, delay='5ms')
        self.addLink(h6, s3, cls=TCLink, delay='5ms')
        self.addLink(h7, s4, cls=TCLink, delay='5ms')
        self.addLink(h8, s4, cls=TCLink, delay='5ms')

def initiate_network():
    simulation = Mininet(topo=NetworkLayout(), controller=OVSController, link=TCLink, switch=OVSSwitch)
    simulation.start()

    # Turn on STP
    for sw_name in ['s1', 's2', 's3', 's4']:
        current_sw = simulation.get(sw_name)
        current_sw.cmd(f'ovs-vsctl set Bridge {sw_name} stp_enable=true')

    h3 = simulation.get('h3')
    h5 = simulation.get('h5')
    h8 = simulation.get('h8')

    print("Gap of 60 seconds for each test to converge STP")
    time.sleep(60)

    for i in range(3):
        print(f"\n--- Ping Test {i+1}/3: h3 → h1 ---")
        print(h3.cmd('ping -c 4 10.0.0.2'))
        time.sleep(30)

    for i in range(3):
        print(f"\n--- Ping Test {i+1}/3: h5 → h7 ---")
        print(h5.cmd('ping -c 4 10.0.0.8'))
        time.sleep(30)

    for i in range(3):
        print(f"\n--- Ping Test {i+1}/3: h8 → h2 ---")
        print(h8.cmd('ping -c 4 10.0.0.3'))
        time.sleep(30)

    CLI(simulation)
    simulation.stop()

if __name__ == '__main__':
    initiate_network()
