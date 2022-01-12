from datetime import datetime, timedelta
import pandas as pd
import pytz


def time(datetime_str):
    return datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")


def get_shedule(shedule: dict):

    final = []

    for i in shedule["shedule"]:
        tmp = {}

        if shedule.get("start_before"):
            start_before = int(f'{shedule.get("start_before")}')
            start_time = time(f'{shedule["date"]} {i["start"]}') + timedelta(
                minutes=start_before
            )
        else:
            start_time = time(f'{shedule["date"]} {i["start"]}')

        if shedule.get("end_after"):
            end_after = int(f'{shedule.get("end_after")}')
            end_time = time(f'{shedule["date"]} {i["end"]}') + timedelta(
                minutes=end_after
            )
        else:
            end_time = time(f'{shedule["date"]} {i["end"]}')

        tmp["start"] = start_time
        tmp["end"] = end_time
        tmp["desired_count"] = i["count"]

        final.append(tmp)

    df = pd.DataFrame(final)

    s: list = []
    for i in range(len(df)):

        start = df.start.get(i)
        end = df.end.get(i)
        d_c = df.desired_count.get(i)
        s.append({"time": start, "d_count": d_c})
        s.append({"time": end, "d_count": -d_c})

    tf = pd.DataFrame(s)
    tf = tf.sort_values("time")
    tf = tf.reset_index(drop=True)

    f: dict = {}
    #     count = 0

    for index, row in tf.iterrows():
        if row["time"] in f:
            f[row["time"]] = f[row["time"]] + row["d_count"]
        else:
            f[row["time"]] = row["d_count"]

    tf = pd.DataFrame({"time": [i for i in f], "count": [f[i] for i in f]})

    return tf


def shedule(df):

    c = 0
    f = []
    for i in range(len(df)):
        c = c + df["count"][i]
        t = df.time[i]
        strf = time(t.strftime("%d/%m/%Y %H:%M:%S"))

        # to convert ist to utc, utc = ist - 5:30
        utc = strf - timedelta(hours=5, minutes=30)

        tmp = {
            "time": t,
            "utc_time": utc,
            "count": c,
        }
        f.append(tmp)

    # lastly
    end_time = df["time"][len(df.time) - 1]

    tf = pd.DataFrame(f)

    return tf, end_time
