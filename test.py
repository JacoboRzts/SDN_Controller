from client import Action, Client, Flow, Instruction, Match
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c' ,'--controller', default='127.0.0.1', help='ODL Controller IP address (default is localhost)')
parser.add_argument('-t' ,'--table', type=int, default=100, help='Table to upload flows (default: 100)')
parser.add_argument('-s' ,'--save', action='store_true', help="Save the flows into a file.")
args = parser.parse_args()

table = args.table
c = Client(ip=args.controller, default_table=args.table)

# ARP Flows
c.setFlow(
    "2977893393545632",
    Flow(
        "100",
        "ARP",
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

c.setFlow(
    "2977893393545632",
    Flow(
        "101",
        "H1",
        table,
        100,
        Match.eth(dst_ip="10.0.0.1/32"),
        [
            Instruction.apply([
                Action.output(13),
            ])
        ]
    ),
)

c.setFlow(
    "2977893393545632",
    Flow(
        "102",
        "H1",
        table,
        100,
        Match.eth(dst_ip="10.0.0.2/32"),
        [
            Instruction.apply([
                Action.output(14),
            ])
        ]
    ),
)
