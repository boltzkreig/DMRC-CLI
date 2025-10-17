from argparse import ArgumentParser
from pathfinder import closest_station, get_first_and_last_trains, plan_journey
from amenities import get_gates
from definitions import *

if __name__ == "__main__":
    parser = ArgumentParser(prog="DMRC",description="A Convenient CLI-Frontend for DMRC website")
    parser.add_argument(
        "-c",
        "--closest",
        dest="jobs",
        action="store_const",
        const="CLST",
        default=None,
        help="top 5 CLOSEST stations (uses termux-api)",
    )
    parser.add_argument(
        "-d",
        "--dest",
        dest="DEST",
        default=None,
        help="journey to this DEST station (1st partial match)",
    )
    parser.add_argument(
        "-f",
        "--from",
        dest="FROM",
        default=None,
        help="journey FROM this station (1st partial match)",
    )
    parser.add_argument(
        "-g",
        "--gate",
        dest="gate",
        action="count",
        default=0,
        help="tells GATE for station (multiplicity leads to increased verbosity)",
    )
    parser.add_argument(
        "-j",
        "--json",
        dest="JSON",
        default="False",
        action="store_true",
        help="response JSON in stderr",
    )
    parser.add_argument(
        "-m",
        "--minc",
        dest="algo",
        action="store_const",
        const="MI",
        default="LD",
        help="queries journey for Minimum-Interchanges (default: least distance)",
    )
    parser.add_argument(
        "-t",
        "--time",
        dest="jobs",
        action="store_const",
        const="FTLT",
        default=None,
        help="First & Last Train TIME for your journey",
    )
    parser.add_argument(
        "-u",
        "--update",
        dest="jobs",
        action="store_const",
        const="UPDT",
        default=None,
        help="UPDaTe metro line & station list",
    )
    parser.add_argument(
        "-v",
        "--via",
        dest="VIA",
        const=None,
        default=False,
        nargs="?",
        help="travel VIA a particular station",
    )

    args = parser.parse_args()
    environ["JSON"] = str(args.JSON)

    try:
        if args.gate > 0:
            get_gates(args.gate)
            sys.exit()

        match args.jobs:
            case "CLST":
                closest_station()
            case "UPDT":
                generate_json()
            case "FTLT":
                get_first_and_last_trains(args.FROM, args.DEST, args.algo)
            case _:
                plan_journey(args.FROM, args.VIA, args.DEST, args.algo)
    except KeyboardInterrupt:
        print("\r" + tc("[INFO] ", color="#ffff00") + " Interrupted")
    finally:
        print("\rCOURTESY: https://delhimetrorail.com")
