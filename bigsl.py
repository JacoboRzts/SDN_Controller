from client import Action, Client, Flow, Instruction, Match
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c' ,'--controller', default='127.0.0.1', help='ODL Controller IP address (default is localhost)')
parser.add_argument('-t' ,'--table', type=int, default=100, help='Table to upload flows (default: 100)')
parser.add_argument('-s' ,'--save', action='store_true', help="Save the flows into a file.")
parser.add_argument('--n_spine', type=int, default=2, help="Number of spine switches to configure.")
parser.add_argument('--n_leaf', type=int, default=3, help='Number of leaf swiches to configure')
parser.add_argument('--n_host', type=int, default=3, help='Number of host per leaf switch to configure.')
args = parser.parse_args()

table = args.table

spines = list(range(1, args.n_spine + 1))
leafs = list(range(args.n_spine + 1, args.n_spine + args.n_leaf + 1))
switches = spines + leafs
ports = spines
subnets = list(range(1, args.n_leaf + 1))
hosts = list(range(1, args.n_host + 1))

print(f"Spines: {spines}")
print(f"Leaf: {leafs}")
print(f"Hosts: {hosts}")
print(f"Switches: {switches}")
print(f"Ports: {ports}")
print(f"Subnets: {subnets}")


c = Client(ip=args.controller, default_table=args.table)

# ARP Flows
for sw in leafs + spines[:1]:
    c.setFlow(
        sw,
        Flow(
            f"{sw}00",
            f"{sw}-ARP",
            table,
            100,
            Match.arp(),
            [
                Instruction.apply([
                    Action.output("FLOOD")
                ])
            ]
        ),
    )

# Spine leaf distribution flows
for spine in spines:
    for subnet in subnets:
        c.setFlow(
            spine,
            Flow(
                f"{spine}{subnet}0",
                f"L{subnet}",
                table,
                100,
                Match.eth(dst_ip=f"10.0.{subnet}.0/24"),
                [
                    Instruction.apply([
                        Action.output(str(subnet)),
                    ])
                ]
            ),
        )

# Leaf distribution
for dpid in leafs:
    # Leaf -> spine distribution flows
    this = dpid - args.n_spine
    nextport = 0
    for subnet in subnets:
        if subnet == this:
            continue
        c.setFlow(
            dpid,
            Flow(
                f"{dpid}{subnet}0",
                f"NET-{subnet}",
                table,
                90,
                Match.eth(dst_ip=f"10.0.{subnet}.0/24"),
                [
                    Instruction.apply([
                        Action.output(ports[nextport]),
                    ])
                ]
            )
        )
        nextport = (nextport + 1) % args.n_spine
    # Leaf -> host distribution flows
    for host in hosts:
        hostname = (dpid - args.n_spine - 1) * args.n_host + host
        c.setFlow(
            dpid,
            Flow(
                f"{dpid}0{hostname}",
                f"H{hostname}",
                table,
                100,
                Match.eth(dst_ip=f"10.0.{dpid-args.n_spine}.{host}/32"),
                [
                    Instruction.apply([
                        Action.output((host) + args.n_spine)
                    ])
                ]
            ),
        )
