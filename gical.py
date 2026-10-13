#!/usr/bin/env python3
# vim: set syntax=python nospell expandtab ts=4 sw=4:
# ###################################### #
# Author: geoffm.companionway@gmail.com  #
# ###################################### #
#       -*- coding: utf-8 -*-            #

# ## DUNDERS ### #
__VERSION__ = "0.2.0"

# ### IMPORTS ### #
import sys
import os
import re
# import inspect
from docopt import docopt, DocoptExit
import requests
from icalendar import Calendar
from datetime import datetime, date, timedelta
from gtoolz import printit, dbug, arg_val, gclr, RESET, data_type , gblock, maxof, called_from , parse_codes, gcolumnize
import shutil
# import math
import recurring_ical_events
import configparser

"""--== private/local imports ==--"""
gmod_dir = os.path.expanduser("~/dev/python/gmodules")
if gmod_dir not in sys.path:
    sys.path.insert(gmod_dir)

from gtoolz import (  # noqa
    do_edit, printit, do_close, do_logo, dbug,
    docvars, kvcols, arg_val, from_to, cat_file, setup_logging
) # noqa

# ### GLOBALS ### #
DFMT = "%Y%m%d-%H%M"
DTIME = datetime.now().strftime(DFMT)
DEBUG = False
LOG = False

# ### CLASSES ### #

# ### FUNCTIONS ### #

@docvars(os.path.basename(__file__))
def handleOPTS():
    """
    Usage:
        {0} [-h] [-v] [-d <DAYS>] [-w]

    Options:
        -h --help       show this help
        -v --version    show version and exit
        -w --weather    display current weather report
        -d <DAYS>       number of days to display [default: 7]
    """
    args = handleDOPTS() or {}
    args |= docopt(handleOPTS.__doc__)
    dbug(args)
    if args.get('--version'):
        print(f"gical v{__VERSION__}")
        sys.exit(0)
    return args
    # ### EOB def handleOPTS(): ### #


@docvars(os.path.basename(__file__))
def handleDOPTS():
    """
    Usage:
        {0} [--hidden] [--dev] [--debug] [--log[=<level>]] [--Edit]
        {0} [options] --Test <funcname> [<fargs>...]

    Options:
      --hidden           Show hidden developer options and exit.
      --debug            Enable dev debug mode (prints to screen).
      --log[=<level>]    Enable file logging (optional level: DEBUG, INFO, WARNING, ERROR).
      --Edit             Edit source code.
      --Test             Run an internal function.
    """
    global DEBUG
    # --- Configure debugging --- #
    isdebug = "--debug" in sys.argv
    DEBUG = isdebug if isdebug else globals().get('DEBUG', False)
    # --- Configure logging --- #
    global LOG
    LOG = True
    log_val = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--log=")), None)
    enable_file_log = "--log" in sys.argv or log_val is not None
    log_lvl = log_val if log_val else "DEBUG"
    setup_logging(isdebug=isdebug, enable_file_logging=enable_file_log, log_lvl=log_lvl)
    try:
        args_raw = docopt(handleDOPTS.__doc__, argv=sys.argv[1:], help=False)
    except DocoptExit:
        args_raw = {}
    # === active option branches === #
    #  Standard docopt parse for dev flags (--hidden, --dev)
    if args_raw.get("--hidden") or args_raw.get("--dev"):
        print(handleDOPTS.__doc__.strip())
        sys.exit(0)
    # --- option: --Test --- #
    if "--Test" in sys.argv:
        test_idx = sys.argv.index("--Test")
        remaining = sys.argv[test_idx + 1:]
        clean_args = [
            a for a in remaining
            if a not in ("--debug", "--hidden", "--dev", "--Edit", "--log")
            and not a.startswith("--log=")
        ]
        if clean_args:
            funcname = clean_args[0]
            fargs = clean_args[1:]
            test_func(funcname, fargs)
        else:
            print("Error: --Test requires a function name.")
            sys.exit(1)
    # --- option: --Edit --- #
    if args_raw.get("--Edit"):
        do_edit(__file__)
        sys.exit(0)
    # --- Clean dev flags out of sys.argv for handleOPTS() --- #
    dev_flags = {"--debug", "--hidden", "--dev", "--Edit"}
    sys.argv = [
        arg for arg in sys.argv
        if arg not in dev_flags and not arg.startswith("--log")
    ]
    # dbug(args_raw)
    return args_raw


def test_func(funcname, fargs):
    """
    Test harness to invoke module functions safely.
    Usage:
        script.py --Test <funcname> [fargs...]
    """
    if funcname and funcname in globals():
        func = globals()[funcname]
        # 1. Parse 'key=val' or standalone positional strings
        parsed_args = []
        parsed_kwargs = {}
        for arg in fargs:
            if "=" in arg:
                k, v = arg.split("=", 1)
                if not k.startswith("<") and not k.startswith("-"):
                    k = f"<{k}>" if not k.isidentifier() else k
                parsed_kwargs[k.strip()] = v.strip()
            else:
                parsed_args.append(arg.strip())
        # 2. Inspect target function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        # 3. Check if target function expects a single 'args' dictionary (e.g., main(args))
        if len(params) == 1 and params[0].name == 'args':
            mock_args = {}
            # Dynamically extract <positional> argument keys from handleOPTS.__doc__
            doc_keys = re.findall(r'<[^>]+>', handleOPTS.__doc__) or ['<filename>']
            for i, val in enumerate(parsed_args):
                if i < len(doc_keys):
                    mock_args[doc_keys[i]] = val
            mock_args.update(parsed_kwargs)
            # Supply dummy values for unsupplied positional keys
            for k in doc_keys:
                mock_args.setdefault(k, "dummy_val")
            call_args = (mock_args,)
            call_kwargs = {}
        else:
            call_args = tuple(parsed_args)
            call_kwargs = parsed_kwargs
        # Display function docstring
        doc_str = func.__doc__ or "No docstring provided."
        printit(doc_str, 'boxed', title=f"{funcname}()", footer=dbug('here'), box_clr="yellow!")
        try:
            kw_str = f", {call_kwargs}" if call_kwargs else ""
            dbug(f"Running {funcname}{call_args}{kw_str}")
            result = func(*call_args, **call_kwargs)
            dbug(f"{result=}")
        except Exception as e:
            print(f"Error executing {funcname}({fargs}): {e}")
        sys.exit(0)
    else:
        print(f"Error: Function '{funcname}' not found in module.")
        sys.exit(1)


def handleCONF():
    default_config_file = "~/.config/gical/gical.ini"
    conf_paths = [os.path.expanduser(default_config_file), 
                  os.path.expanduser("~/.config/gical/gical.conf"),
                  os.path.expanduser("~/.config/gical/config.ini"),
                  os.path.expanduser("~/.config/gical/config.conf"),
                  ]
    config = configparser.ConfigParser(interpolation=None)

    for path in conf_paths:
        if os.path.exists(path):
            dbug(path)
            config.read(path)
            # dbug(config, 'ask')

            if "settings" in config:
                settings = config["settings"]

                # Check secret_ics_url -> ics_url -> url
                ics_url = (
                    settings.get("secret_ics_url")
                    or settings.get("ics_url")
                    or settings.get("url")
                )

                # Check weather_location -> location
                location = (
                    settings.get("weather_location")
                    or settings.get("location")
                )

                return {
                    "ics_url": ics_url,
                    "location": location
                }
    sample_config = f""" sample {default_config_file}
    [settings]
    ics_url: https://calendar.google.com/calendar/ical/<user_email>%40gmail.com/private-XXXXXXXXXXXXXXXXXXXX/basic.ics
    location: Your+City,State_location
    """
    printit(f"Please establish a default config file at: {default_config_file}", 'boxed', box_clr="red!")
    printit(sample_config, 'boxed', box_clr="yellow!")
    return None


def fetch_weather(location, target_date):
    """
    Fetches weather from wttr.in.
    Note: wttr.in provides current/short forecasts, so we pull it for 'today'
    or use formatting options.
    """
    # If it's today, we can fetch a clean one-liner.
    if target_date == date.today():
        url = f"https://wttr.in/{location}?format=3"
        headers = {'User-Agent': 'curl'} # Forces ANSI color text output
        try:
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                return res.text.strip()
        except Exception:
            pass
    return None


def fetch_day_weather(location, target_date, width):
    """
    Fetches a single-day ANSI weather block from wttr.in
    and splits it into lines suitable for printit() boxes.
    """
    dbug(target_date)
    # wttr.in supports ?0 for current day, or we can format it nicely
    url = f"https://wttr.in/{location}?0&m"  # &m for metric or leave off for US units (°F)
    headers = {'User-Agent': 'curl'} # Forces ANSI color and ASCII art output
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            # wttr.in returns a multi-line ASCII block. Let's clean and wrap/truncate it to fit our box width.
            raw_lines = res.text.strip().split('\n')

            # Optionally filter or slice the lines so it fits nicely inside your column width
            # wttr.in outputs about 7 lines for a 1-day view. Let's grab the core forecast lines:
            box_lines = []
            for line in raw_lines:
                # Strip excessive outer borders that wttr.in adds if needed, or keep them if they fit
                if "Weather report" in line or "Follow" in line:
                    continue
                box_lines.append(line)
            return box_lines
    except Exception:
        pass
    return ["Weather unavailable"]


# #################
# ### Main Code ###
# #################
def main(args=None):
    # #############
    """
    TODO: 
    Describe script functionality here...
    Then begin coding!
    """
    # args = args or {}
    # printit(main.__doc__, 'boxed', 'centered', 'shadowed', title="Start coding and enjoy!", footer=dbug('here'), box_clr="yellow!")
    scr_col_len  = shutil.get_terminal_size((80, 24)).columns
    width = int((scr_col_len-2) / 7)
    dbug(f"{scr_col_len=} {width=}")

    # dbug(args)
    # deals with docopt gremlins
    raw_days = args.get('<DAYS>') or args.get('DAYS') if isinstance(args.get('-d'), bool) else args.get('-d')
    DAYS = int(raw_days or 7)
    # dbug(DAYS, 'ask')


    # Replace with your actual public iCal URL
    conf = handleCONF()
    if conf is None:
        sys.exit()
    ical_url = conf["ics_url"]
    weather_loc = conf["location"]
    # ical_url = handleCONF()\cc

    # 1. Define window: Today through Next 10 Days
    today = date.today()
    end_window = today + timedelta(days=DAYS-1)

    # recurring_ical_events .between() treats the end date as exclusive,
    # so we add 1 day to ensure the final day of the view is fully included.
    query_end = end_window + timedelta(days=1)

    # 2. Fetch the .ics file content
    response = requests.get(ical_url)
    response.raise_for_status()

    # 3. Parse the iCal data
    cal = Calendar.from_ical(response.content)
    expanded_events = recurring_ical_events.of(cal).between(today, query_end)


    events_by_date = {}

    for component in expanded_events:
        summary = str(component.get('summary', 'No Title'))
        dtstart_prop = component.get('dtstart')
        dtend_prop = component.get('dtend')

        if not dtstart_prop:
            continue

        start_raw = dtstart_prop.dt
        end_raw = dtend_prop.dt if dtend_prop else None

        # Handle Date vs Datetime conversion
        if isinstance(start_raw, datetime):
            start_date = start_raw.date()
            start_str = start_raw.strftime('%H:%M')
        else:
            start_date = start_raw
            start_str = "All Day"

        if end_raw:
            if isinstance(end_raw, datetime):
                end_date = end_raw.date()
                end_str = end_raw.strftime('%H:%M')
            else:
                # Note: iCal all-day end dates are exclusive (day after the event ends)
                end_date = end_raw - timedelta(days=1)
                end_str = str(end_date)
        else:
            end_date = start_date
            end_str = 'N/A'

        # Span multi-day events across every day they cover within our window
        current_span_day = max(start_date, today)
        final_span_day = min(end_date, end_window)

        while current_span_day <= final_span_day:
            if current_span_day not in events_by_date:
                events_by_date[current_span_day] = []

            events_by_date[current_span_day].append({
                'title': summary,
                'start': start_str,
                'end': end_str
            })
            current_span_day += timedelta(days=1)

    # 5. Display day-by-day output including empty days
    # print(f"Calendar Schedule: {today} to {end_window}\n" + "=" * 50)

    boxes = []
    current_day = today
    while current_day <= end_window:
        box_clr="white!"
        # day_header = current_day.strftime('%A, %b %d, %Y')
        day_header = current_day.strftime('%a, %b %d')
        # print(f"\n--- {day_header} ---")
        title = f" {day_header} "

        day_events = events_by_date.get(current_day, [])
        msgs = []



        if not day_events:
            # print("  (No events)")
            day_events = "No events"
            msgs.append(day_events)
        else:
            box_clr = "green"
            for ev in day_events:
                if ev['start'] == "All Day":
                    # print(f"  [All Day] {ev['title']}")
                    msgs.append(f"  [All Day] {ev['title']}")
                else:
                    # print(f"  {ev['start']} - {ev['end']} : {ev['title']}")
                    msgs.append(f"  {ev['start']} - {ev['end']} : {ev['title']}")
        day_events = events_by_date.get(current_day, [])


        # # Pull weather block for the day
        # weather_lines = fetch_day_weather(weather_loc, current_day, width)
        # dbug(weather_lines)
        # if weather_lines:
        #     msgs.extend(weather_lines)
        #     msgs.append("─" * max(2, width - 4)) # separator line

        box = printit(msgs, 'boxed', 'noprnt', title=title, width=width, box_clr=box_clr)
        boxes.append(box)


        current_day += timedelta(days=1)

    printit(gcolumnize(boxes))

    if args.get('--weather') or args.get('-w'):
        print("\n") # spacing
        weather_loc = conf.get("location", "Elizabeth+City,NC")
        url = f"https://wttr.in/{weather_loc}"
        headers = {'User-Agent': 'curl'} # Forces ANSI color text output
        try:
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                print(res.text.strip())
        except Exception:
            print("Weather report currently unavailable.")

if __name__ == '__main__':
    args = handleOPTS()
    main(args)
