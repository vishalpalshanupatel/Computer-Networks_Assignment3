from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class CustomLoopTopo(Topo):
    def build(self):
        # Create switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Create hosts with IPs
        h1 = self.addHost('h1', ip='10.0.0.2/24')
        h2 = self.addHost('h2', ip='10.0.0.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')

        # Add host-switch links with 5ms latency
        self.addLink(h1, s1, cls=TCLink, delay='5ms')
        self.addLink(h2, s1, cls=TCLink, delay='5ms')
        self.addLink(h3, s2, cls=TCLink, delay='5ms')
        self.addLink(h4, s2, cls=TCLink, delay='5ms')
        self.addLink(h5, s3, cls=TCLink, delay='5ms')
        self.addLink(h6, s3, cls=TCLink, delay='5ms')
        self.addLink(h7, s4, cls=TCLink, delay='5ms')
        self.addLink(h8, s4, cls=TCLink, delay='5ms')

        # Add switch-switch links with 7ms latency
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')

def run():
    topo = CustomLoopTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    print("\n=== Running Ping Tests ===\n")
    h1 = net.get('h1')
    h3 = net.get('h3')
    h5 = net.get('h5')
    h7 = net.get('h7')
    h2 = net.get('h2')
    h8 = net.get('h8')

    print("Ping h1 from h3:")
    h3.cmdPrint('ping -c 3 10.0.0.2')

    print("Ping h7 from h5:")
    h5.cmdPrint('ping -c 3 10.0.0.8')

    print("Ping h2 from h8:")
    h8.cmdPrint('ping -c 3 10.0.0.3')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
