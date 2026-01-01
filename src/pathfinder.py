from definitions import *


def closest_station():
    def get_detail_list(code):
        res = request_handler(f"{ENDPOINT}/station/{code}")
        return res

    try:
        _hash = file_digest(open(PROXIMITY_FILE, "rb"), "sha3_512").hexdigest()
        if datetime.now().timestamp() - PROXIMITY_FILE.stat().st_mtime > (
            60 * 60 * 24 * 15
        ):
            if input(f"{PROXIMITY_FILE.name} is stale. Wish to refresh?(y/N) ") == "y":
                raise LookupError("Stale Files")
    except Exception as e:
        print(
            tc("[ERROR] ", color="#ff0000")
            + str(e)
            + " Trying to Scape Station Location (will take some time)"
        )
        table = []
        for code in stations.values():
            row = {}
            res = get_detail_list(code)
            row["name"] = res["station_name"]
            row["latitude"] = res["latitude"]
            row["longitude"] = res["longitude"]
            row["x_coords"] = res["x_coords"]
            row["y_coords"] = res["y_coords"]
            row["color"] = (
                "#000000"
                if res["interchange"]
                else res["metro_lines"][0]["primary_color_code"]
            )
            try:
                for detail in res["parkings"]:
                    row["parking"] = True
            except:
                row["parking"] = False
            print("\r\t", row)
            table.append(row.copy())
        with open(PROXIMITY_FILE, "w") as file:
            json.dump(table, file, indent=2)
        if _hash == file_digest(open(PROXIMITY_FILE, "rb"), "sha3_512").hexdigest():
            print("Found Nothing New")
        else:
            print("Found Something New")

    finally:
        try:
            input(
                "This only works with termux-api\nPlease turn your location on. Press RETURN to continue."
            )
            res = {}
            try:
                res = get_from_sensors(["termux-location"])
            except:
                print("\r\tTrying to estimate location from IP Address")
                res_raw = request_handler("https://ipinfo.io")["loc"]
                res["latitude"] = float(res_raw.split(",")[0])
                res["longitude"] = float(res_raw.split(",")[1])

            cur_lat = res["latitude"]
            cur_lon = res["longitude"]
            print(f"\r\tCurrent Location: {round(cur_lat,3)}°N {round(cur_lon,3)}°E")
            res = get_from_sensors(["termux-sensor", "-s", "Orientation", "-n", "1"])
            orientation = res["Orientation Sensor"]["values"][0]
        except:
            print("\r\tSomething went wrong. Try again")
            sys.exit()
        with open(PROXIMITY_FILE, "r") as file:
            stats = json.load(file)
        distance_table = {}
        for stat in stats:
            del_lat_dis = (float(stat["latitude"]) - cur_lat) * LAT_DIS
            del_lon_dis = (
                (float(stat["longitude"]) - cur_lon) * LAT_DIS * cos(radians(cur_lat))
            )
            distance_table[stat["name"]] = [
                hypot(del_lat_dis, del_lon_dis),
                ((degrees(atan2(del_lon_dis, del_lat_dis)) - orientation) % 360) / 30,
            ]
            # print(del_lat_dis,del_lon_dis,orientation)
        # print(distance_table)
        print("\r\tTop 5 Nearest Metro Stations:")
        for i, (key, (_dis, _dir)) in enumerate(
            sorted(distance_table.items(), key=lambda item: item[1][0])[0:5], start=1
        ):
            print(f"\t{i}: {key} ({round(_dis,3)} km) towards {round(_dir)} o'clock")


def get_first_and_last_trains(FROM, DEST, ALGO, RETRY):
    FROM, VIA, DEST, ALGO = setup_vars(FROM, False, DEST, ALGO, RETRY)
    res = request_handler(
        f"{ENDPOINT}/first_and_last_train_with_filter/{FROM}/{DEST}/{ALGO}"
    )
    print(tc("\rFIRST TRAIN:", styles=["bold"]))
    for section in res["first_train"]["first_train_route_detail"]:
        print(
            f"\t{section['start_station_name']:35} \u2b95  {section['end_station_name']}"
        )
        print(
            f"\t{'('+section['start_time']+')':35} \u2b95  {'('+section['end_time']+')'}"
        )
    print(tc("LAST TRAIN:", styles=["bold"]))
    for section in res["last_train"]["last_train_route_detail"]:
        print(
            f"\t{section['start_station_name']:35} \u2b95  {section['end_station_name']}"
        )
        print(
            f"\t{'('+section['start_time']+')':35} \u2b95  {'('+section['end_time']+')'}"
        )


def plan_journey(FROM, VIA, DEST, ALGO, RETRY):
    def path_manager(point_a, point_b, time, ALGO):
        res = request_handler(
            f'{ENDPOINT}/station_route/{point_a}/{point_b}/{ALGO}/{time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]}'
        )
        print(
            f"{tc('\r\tTOTAL TIME: ',styles=['bold'])}{res['total_time']:<11}{tc('FARE: ₹',styles=['bold'])}{res['fare']} (₹{float(res['fare'])*0.9:<.2f})"
        )
        print(
            f"{tc('\r\tSTATIONS: ',styles=['bold'])}{res['stations']:<13}{tc('INTERCHANGES: ',styles=['bold'])}{len(res['route'])-1}"
        )
        for section in res["route"]:
            count = 0
            clr = lines[str(section["line_no"])]
            if section["station_interchange_time"]:
                sheet["timeCollection"].append(section["station_interchange_time"])
            sheet["timeCollection"].append(tc(section["path_time"], color=clr))
            sheet["body"].append(
                f"    \u25b2 {section['new_start_time']} {'from '+tc(section['platform_name'],styles=['underline','bold']) if section['platform_name'] else ''}"
            )
            for node in section["path"]:
                sheet["body"].append(
                    f"{count:<3} {tc('\u2588',color=clr)} {node['name']}"
                )
                count += 1
            sheet["body"].append(f"    \u25bc {section['new_end_time']}")
        diff = datetime.strptime(res["total_time"], "%H:%M:%S")
        time += timedelta(hours=diff.hour, minutes=diff.minute, seconds=diff.second)
        return time

    FROM, VIA, DEST, ALGO = setup_vars(FROM, VIA, DEST, ALGO, RETRY)
    time = datetime.now()
    print(
        f'\t{FROM} \u2B95 {VIA + " \u2B95" if VIA else ""} {DEST}\n\t{ALGO} @ {time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]}\n'
    )

    if VIA is False:
        time = path_manager(FROM, DEST, time, ALGO)
    else:
        time = path_manager(FROM, VIA, time, ALGO)
        sheet["body"].append("    👇")
        time = path_manager(VIA, DEST, time, ALGO)
    sheet["timeCollection"].append("==> " + str(time.strftime("%H:%M:%S")))
    print("\t󰦖 :", *sheet["timeCollection"])
    print("\n\t" + "\n\r\t".join(sheet["body"]))
