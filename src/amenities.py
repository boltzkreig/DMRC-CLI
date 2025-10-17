from definitions import poll_station, request_handler, ENDPOINT, symbolise


def get_gates(level):
    code = poll_station("--prompt='GATES OF: '")
    print(f"Information of {code} station")
    res = request_handler(f"{ENDPOINT}/station/{code}")
    for gate in reversed(res["gates"]):
        print(
            f"\r\t{gate['gate_name'].replace('Gate No. ','⛩️ '):5} : {gate['location']}"
        )
    print()
    for lift in reversed(res["lifts"]):
        print(
            f"\t{symbolise(lift['lift_type'])} {symbolise(lift['available_outside_inside'])} : {lift['description_location']:30}"
        )
    print()
    for platform in reversed(res["platforms"]):
        print(
            f"\t{platform['platform_code'].replace('PL','🚉 '):4} : {platform['train_towards']['station_name']}"
        )

    if level < 2:
        return
    print()
    for facility in res["stations_facilities"]:
        for detail in facility["detail_list"]:
            kind = symbolise(facility["kind"])
            print(
                f"{"\t"+kind:5} : {detail['facility_name']} \u2B95 {detail['location_description']}"
            )
    try:
        for detail in res["parkings"]:
            print("\r\t" + symbolise("Parking") + "    : " + detail["location"])
    except:
        print("\r\t" + symbolise("Parking") + "    : N/A")

    if level < 3:
        return
    print()
    for place in res["nearby_places"]:
        for service in place.values():
            for kind in service.values():
                for entity in kind[1:]:
                    print(
                        f"{'\t'+symbolise(entity['types_of_place'])+' ('+str(entity['distance_from_metro'])+' Km)':<16}{entity['name']}"
                    )
