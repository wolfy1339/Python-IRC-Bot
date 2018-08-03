import datetime
import json
import re
import requests as web
import urllib

import config
from utils.util import add_cmd

from icao import data

install_geopy = "Please install geopy via 'pip' to use weather.py"

try:
    import geopy.geocoders as geo
except ImportError:
    print(install_geopy)


r_from = re.compile(r'(?i)([+-]\d+):00 from')
r_tag = re.compile(r'<(?!!)[^>]+>')


def location(name):
    geolocator = geo.Nominatim()

    geolocator.country_bias = str()
    if re.match('\d{5}', name):
        geolocator.country_bias = 'US'

    location = geolocator.geocode(name)

    try:
        outgoing_name = location.address
        lat = location.latitude
        lng = location.longitude
    except AttributeError:
        return '', '', ''

    return outgoing_name, str(lat), str(lng)


def local(icao, hour, minute):
    '''Grab local time based on ICAO code'''
    uri = 'https://airports-api.s3-us-west-2.amazonaws.com/icao/%s.json'
    content = web.get(uri % icao.lower()).json()
    offset = content['utc_offset']
    if offset:
        lhour = str(int(hour) + int(offset))

        return (lhour + ':' + str(minute) + ', ' + str(hour) +
                str(minute) + 'Z')
    return str(hour) + ':' + str(minute) + 'Z'


def code(search):
    '''Find ICAO code in the provided database.py (find the nearest one)'''
    if search.upper() in data:
        return search.upper()
    else:
        name, latitude, longitude = location(search)
        if name == '?':
            return False
        sumOfSquares = (99999999999999999999999999999, 'ICAO')
        for icao_code in data:
            lat = float(data[icao_code][0])
            lon = float(data[icao_code][1])
            latDiff = abs(float(latitude) - float(lat))
            lonDiff = abs(float(longitude) - float(lon))
            diff = (latDiff * latDiff) + (lonDiff * lonDiff)
            if diff < sumOfSquares[0]:
                sumOfSquares = (diff, icao_code)
        return sumOfSquares[1]


def get_metar(icao_code):
    '''Obtain METAR data from NOAA for a given ICAO code'''
    url = 'http://tgftp.nws.noaa.gov/data/observations/metar/stations/%s.TXT'
    req = web.get(url % icao_code)
    page = req.text

    if req.status_code == 404:
        return False, icao_code + ': no such ICAO code, or no NOAA data.'

    return True, page


def get_icao(args, command='weather'):
    '''Provide the ICAO code for a given args'''

    icao_code = code(' '.join(args))

    if not icao_code:
        return False, 'No ICAO code found, sorry.'

    return True, icao_code


@add_cmd('metar', min_args=0)
def metar(bot, event, irc, args):
    '''.metar <location> -- shows the raw METAR data for a given location'''

    status, icao_code = get_icao(args, 'metar')
    if not status:
        return irc.reply(event, icao_code)

    status, metar = get_metar(icao_code)
    if not status:
        return irc.reply(event, metar)

    return irc.reply(event, metar.replace('\n', ' ').replace('/', ''))


def speed_desc(speed):
    '''Provide a more natural description of wind speed'''
    description = str()

    if speed < 1:
        description = 'Calm'
    elif speed < 4:
        description = 'Light air'
    elif speed < 7:
        description = 'Light breeze'
    elif speed < 11:
        description = 'Gentle breeze'
    elif speed < 16:
        description = 'Moderate breeze'
    elif speed < 22:
        description = 'Fresh breeze'
    elif speed < 28:
        description = 'str(ong) breeze'
    elif speed < 34:
        description = 'Near gale'
    elif speed < 41:
        description = 'Gale'
    elif speed < 48:
        description = 'str(ong) gale'
    elif speed < 56:
        description = 'Storm'
    elif speed < 64:
        description = 'Violen(t) storm'
    else:
        description = 'Hurricane'

    return description


def wind_dir(degrees):
    '''Provide a nice little unicode character of the wind direction'''
    try:
        degrees = float(degrees)
    except ValueError:
        pass

    if degrees == 'VRB':
        degrees = '\u21BB'
    elif (degrees <= 22.5) or (degrees > 337.5):
        degrees = '\u2191'
    elif (degrees > 22.5) and (degrees <= 67.5):
        degrees = '\u2197'
    elif (degrees > 67.5) and (degrees <= 112.5):
        degrees = '\u2192'
    elif (degrees > 112.5) and (degrees <= 157.5):
        degrees = '\u2198'
    elif (degrees > 157.5) and (degrees <= 202.5):
        degrees = '\u2193'
    elif (degrees > 202.5) and (degrees <= 247.5):
        degrees = '\u2199'
    elif (degrees > 247.5) and (degrees <= 292.5):
        degrees = '\u2190'
    elif (degrees > 292.5) and (degrees <= 337.5):
        degrees = '\u2196'

    return degrees


@add_cmd('weather', min_args=1)
def weather(bot, event, irc, args):
    '''.weather <ICAO> - Show the weather at airport with the code <ICAO>.'''

    status, icao_code = get_icao(args)
    if not status:
        return irc.reply(event, icao_code)

    status, page = get_metar(icao_code)
    if not status:
        return irc.reply(event, page)

    metar = page.splitlines().pop()
    metar = metar.split(' ')

    if len(metar[0]) == 4:
        metar = metar[1:]

    if metar[0].endswith('Z'):
        time = metar[0]
        metar = metar[1:]
    else:
        time = None

    if metar[0] == 'AUTO':
        metar = metar[1:]
    if metar[0] == 'VCU':
        irc.reply(event, icao_code + ': no data provided')
        return

    if metar[0].endswith('KT'):
        wind = metar[0]
        metar = metar[1:]
    else:
        wind = None

    if ('V' in metar[0]) and (metar[0] != 'CAVOK'):
        metar = metar[1:]

    if ((len(metar[0]) == 4) or
            metar[0].endswith('SM')):
        visibility = metar[0]
        metar = metar[1:]
    else:
        visibility = None

    while metar[0].startswith('R') and (metar[0].endswith('L')
                                        or 'L/' in metar[0]):
        metar = metar[1:]

    if len(metar[0]) == 6 and (metar[0].endswith('N') or
                               metar[0].endswith('E') or
                               metar[0].endswith('S') or
                               metar[0].endswith('W')):
        metar = metar[1:]  # 7000SE?

    cond = []
    while (((len(metar[0]) < 5) or
            metar[0].startswith('+') or
            metar[0].startswith('-')) and (not (metar[0].startswith('VV') or
                                                metar[0].startswith('SKC') or metar[0].startswith('CLR') or
                                                metar[0].startswith('FEW') or metar[0].startswith('SCT') or
                                                metar[0].startswith('BKN') or metar[0].startswith('OVC')))):
        cond.append(metar[0])
        metar = metar[1:]

    while '/P' in metar[0]:
        metar = metar[1:]

    if not metar:
        return irc.reply(event, icao_code + ': no data provided')

    cover = []
    while (metar[0].startswith('VV') or metar[0].startswith('SKC') or
           metar[0].startswith('CLR') or metar[0].startswith('FEW') or
           metar[0].startswith('SCT') or metar[0].startswith('BKN') or
           metar[0].startswith('OVC')):
        cover.append(metar[0])
        metar = metar[1:]
        if not metar:
            return irc.reply(event, icao_code + ': no data provided')

    if metar[0] == 'CAVOK':
        cover.append('CLR')
        metar = metar[1:]

    if metar[0] == 'PRFG':
        cover.append('CLR')  # @@?
        metar = metar[1:]

    if metar[0] == 'NSC':
        cover.append('CLR')
        metar = metar[1:]

    if ('/' in metar[0]) or (len(metar[0]) == 5 and metar[0][2] == '.'):
        temp = metar[0]
        metar = metar[1:]
    else:
        temp = None

    if metar[0].startswith('QFE'):
        metar = metar[1:]

    if metar[0].startswith('Q') or metar[0].startswith('A'):
        pressure = metar[0]
        metar = metar[1:]
    else:
        pressure = None

    if time:
        hour = time[2:4]
        minute = time[4:6]
        time = local(icao_code, hour, minute)
    else:
        time = '(time unknown)'

    speed = False

    if wind:
        # if the args that is in wind[3:5] can't be converted to float
        # default to 0, this happens in rare cases when there is extra info
        # in the METAR data that either removes or replaces wind speed
        try:
            speed = float(wind[3:5])
        except Exception:
            speed = 0

        description = speed_desc(speed)

        degrees = wind[0:3]
        degrees = wind_dir(degrees)

        if not icao_code.startswith('EN') and not icao_code.startswith('ED'):
            # for any part of the world except Germany and Norway
            wind = '%s %.1fkt (%s)' % (description, speed, degrees)
        elif icao_code.startswith('ED'):
            # Germany
            kmh = float(speed * 1.852)
            wind = '%s %.1fkm/h (%.1fkt) (%s)' % (description,
                                                  kmh, speed, degrees)
        elif icao_code.startswith('EN'):
            # Norway
            ms = float(speed * 0.514444444)
            wind = '%s %.1fm/s (%.1fkt) (%s)' % (description,
                                                 ms, speed, degrees)
    else:
        wind = '(wind unknown)'

    if visibility:
        visibility = visibility + 'm'
    else:
        visibility = '(visibility unknown)'

    if cover:
        level = None
        for c in cover:
            if c.startswith('OVC') or c.startswith('VV'):
                if (level is None) or (level < 8):
                    level = 8
            elif c.startswith('BKN'):
                if (level is None) or (level < 5):
                    level = 5
            elif c.startswith('SCT'):
                if (level is None) or (level < 3):
                    level = 3
            elif c.startswith('FEW'):
                if (level is None) or (level < 1):
                    level = 1
            elif c.startswith('SKC') or c.startswith('CLR'):
                if level is None:
                    level = 0

        if level == 8:
            cover = 'Overcast \u2601'
        elif level == 5:
            cover = 'Cloudy'
        elif level == 3:
            cover = 'Scattered'
        elif (level == 1) or (level == 0):
            cover = 'Clear \u263C'.encode('utf-8')
        else:
            cover = 'Cover Unknown'
    else:
        cover = 'Cover Unknown'

    if temp:
        if '/' in temp:
            t = temp.split('/')
            temp = t[0]
            dew = t[1]
        else:
            temp = temp.split('.')[0]
        if temp.startswith('M'):
            temp = '-' + temp[1:]
        if dew.startswith('M'):
            dew = '-' + dew[1:]
        try:
            temp = float(temp)
            dew = float(dew)
        except ValueError:
            temp = '?'
            dew = '?'
    else:
        temp = '?'
        dew = '?'

    windchill = False
    if isinstance(temp, float) and isinstance(speed, float) and temp <= 10.0 and speed > 0:
        # Convert knots to kilometers per hour, https://is.gd/3dNrbW
        speed_kmh = speed * 1.852

        # Formula for Windchill: https://is.gd/SS0u6E
        windchill = 13.12 + (0.6215 * temp) - (11.37 * (speed_kmh **
                                                        (0.16))) + (0.3965 * temp * (speed_kmh ** (0.16)))
        windchill = float(windchill)

        # convert result int(o) Fahrenheit
        f = (windchill * 1.8) + 32

        if icao_code.startswith('K'):
            # if in North America
            windchill = '%.1f\u00B0F (%.1f\u00B0C)' % (f, windchill)
        else:
            # else, anywhere else in the worldd
            windchill = '%.1f\u00B0C' % windchill

    heatindex = False
    if isinstance(temp, float) and isinstance(dew, float):
        rh = make_rh_C(temp, dew)
        temp_f = (temp * 1.8) + 32.0
        if rh >= 40.0 and temp_f >= 80.0:
            heatindex = gen_heat_index(temp_f, rh)
            heatindex = '%.1f\u00B0F (%.1f\u00B0C)' % (
                heatindex, (heatindex - 32.0) / (1.8))

    if pressure:
        if pressure.startswith('Q'):
            pressure = pressure.lstrip('Q')
            if pressure != 'NIL':
                pressure = str(float(pressure)) + 'mb'
            else:
                pressure = '?mb'
        elif pressure.startswith('A'):
            pressure = pressure.lstrip('A')
            if pressure != 'NIL':
                inches = pressure[:2] + '.' + pressure[2:]
                mb = float(inches) * 33.7685
                pressure = '%sin (%.2fmb)' % (inches, mb)
            else:
                pressure = '?mb'

            if isinstance(temp, float):
                f = (temp * 1.8) + 32
                temp = '%.1f\u00B0F (%.1f\u00B0C)' % (f, temp)
            if isinstance(dew, float):
                f = (dew * 1.8) + 32
                dew = '%.1f\u00B0F (%.1f\u00B0C)' % (f, dew)
    else:
        pressure = '?mb'

    if isinstance(temp, float):
        temp = '%.1f\u00B0C' % temp
    if isinstance(dew, float):
        dew = '%.1f\u00B0C' % dew

    if cond:
        conds = cond
        cond = ''

        intensities = {
            '-': 'Light',
            '+': 'Heavy'
        }

        descriptors = {
            'MI': 'Shallow',
            'PR': 'Partial',
            'BC': 'Patches',
            'DR': 'Drifting',
            'BL': 'Blowing',
            'SH': 'Showers of',
            'TS': 'Thundery',
            'FZ': 'Freezing',
            'VC': 'In the vicinity:',
            'RA': 'Unimaginable',
            'SN': 'Snow',
        }

        phenomena = {
            'DZ': 'Drizzle',
            'RA': 'Rain',
            'SN': 'Snow',
            'SG': 'Snow Grains',
            'IC': 'Ice Crystals',
            'PL': 'Ice Pellets',
            'GR': 'Hail',
            'GS': 'Small Hail',
            'UP': 'Unknown Precipitation',
            'BR': 'Mist',
            'FG': 'Fog',
            'FU': 'Smoke',
            'VA': 'Volcanic Ash',
            'DU': 'Dust',
            'SA': 'Sand',
            'HZ': 'Haze',
            'PY': 'Spray',
            'PO': 'Whirls',
            'SQ': 'Squalls',
            'FC': 'Tornado',
            'SS': 'Sandstorm',
            'DS': 'Duststorm',
            # ? Cf. http://swhack.com/logs/2007-10-05#T07-58-56
            'TS': 'Thunderstorm',
            'SH': 'Showers'
        }

        for c in conds:
            if c.endswith('//'):
                if cond:
                    cond += ', '
                cond += 'Some Precipitation'
            elif len(c) == 5:
                intensity = intensities[c[0]]
                descriptor = descriptors[c[1:3]]
                phenomenon = phenomena.get(c[3:], c[3:])
                if cond:
                    cond += ', '
                cond += intensity + ' ' + descriptor + ' ' + phenomenon
            elif len(c) == 4:
                descriptor = descriptors.get(c[:2], c[:2])
                phenomenon = phenomena.get(c[2:], c[2:])
                if cond:
                    cond += ', '
                cond += descriptor + ' ' + phenomenon
            elif len(c) == 3:
                intensity = intensities.get(c[0], c[0])
                phenomenon = phenomena.get(c[1:], c[1:])
                if cond:
                    cond += ', '
                cond += intensity + ' ' + phenomenon
            elif len(c) == 2:
                phenomenon = phenomena.get(c, c)
                if cond:
                    cond += ', '
                cond += phenomenon

    output = str()
    output += 'Cover: ' + cover
    output += ', Temp: ' + temp
    output += ', Dew Point: ' + dew
    if windchill:
        output += ', Windchill: ' + windchill
    if heatindex:
        output += ', Heat Index: ' + heatindex
    output += ', Pressure: ' + pressure
    if cond:
        output += ' Condition: ' + cond
    output += ', Wind: ' + wind
    output += ' - %s, %s' % (str(icao_code), time)

    irc.reply(event, output)


def windchill(bot, event, irc, args):
    pass


def get_windchill(bot, event, irc, args):
    '''.windchill <temp> <wind speed> -- shows Windchill in F'''

    if len(args) == 1:
        # show them what we want
        return irc.reply(event, '.windchill <temp> <wind speed> -- shows Windchill in \u00B0F')

    if len(args) >= 3:
        try:
            # please, please, please be numbers...
            temp = float(args[1])
            wind = float(args[2])
        except Exception:
            # well, shit, there weren't numbers
            return irc.reply(event, 'Invalid arguments! Try, .windchill without any parameters.')
    else:
        # why couldn't the args be valid? silly users
        return irc.reply(event, 'Invalid arguments! Try, .windchill without any parameters.')

    if temp > 50:
        return irc.reply(event, 'The windchill formula only works on temperatures below 50 \u00B0F')

    if wind < 0:
        # yes, yes, I know about vectors, but this is a scalar equation
        return irc.reply(event, "You can't have negative wind speed!")
    elif wind >= 300:
        # hehe
        irc.reply(event, 'Are you okay?')

    # cf. https://is.gd/mgLuzU
    wc = 35.74 + (0.6215 * temp) - (35.75 * (wind ** (0.16))) + \
        (0.4275 * temp * (wind ** (0.16)))

    irc.reply(event, 'Windchill: %2.f \u00B0F' % wc)


dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def remove_dots(txt):
    if '..' not in txt:
        return txt
    else:
        txt = re.sub(r'\.+', ' ', txt)
        return remove_dots(txt)


def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x


def chomp_desc(txt):
    out = txt
    p = re.compile(r'(?<=[\.\?!]\s)(\w+)')

    def upper_repl(match):
        return match.group1.upper()

    def cap(match):
        return match.group().capitalize()

    out = re.sub('([Tt])hunder(storm|shower)', r'\1\2', out)
    out = re.sub('with', 'w/', out)
    out = re.sub('and', '&', out)
    out = re.sub('during', 'in', out)
    out = re.sub('becoming', '', out)
    out = re.sub('occasionally', 'occ', out)
    out = re.sub('occasional', 'occ', out)
    out = re.sub('especially', 'esp.', out)
    out = re.sub('possibly', 'poss', out)
    out = re.sub('possible', 'poss', out)
    out = re.sub('([Ss])cattered', r'\1cat', out)
    out = re.sub('([Mm])orning', 'AM', out)
    out = re.sub('evening', 'AM', out)
    out = re.sub('afternoon', 'PM', out)
    out = re.sub('in the', 'in', out)
    out = re.sub('Then the (\S)', upper_repl, out)
    out = re.sub(r'(?i)(\b)(?:the|a)(\b)', r'\1\2', out)

    out = remove_dots(out)
    out = remove_spaces(out)

    out = p.sub(cap, out)

    out = out.strip()
    return out


@add_cmd('forecast', min_args=1)
def forecast(bot, event, irc, args):
    if not hasattr(config, 'forecastio_apikey'):
        return irc.reply(event, 'Please sign up for a Dark Sky API key at https://darksky.net/ or try .wx-noaa or .weather-noaa')

    name, lat, lng = location(" ".join(args))
    if name == 'ImportError' and not lat and not lng:
        return install_geopy

    url = 'https://api.darksky.net/forecast/%s/%s,%s'

    # do some error checking
    try:
        # if this fails, we got bigger problems
        page = web.get(url % (config.forecastio_apikey,
                              urllib.parse.quote(lat), urllib.parse.quote(lng)))
    except Exception:
        return irc.reply(event, 'Could not acess https://api.darksky.net/')

    # we want some tasty JSON
    try:
        data = page.json()
    except Exception:
        return irc.reply(event, 'The server did not return anything that was readable as JSON.')

    if 'daily' not in data or 'data' not in data['daily']:
        return irc.reply(event, 'Cannot find usable info in information returned by the server.')

    # here we go...

    days = data['daily']['data']

    output = preface_location(name)

    if 'alerts' in data:
        # TODO: modularize the colourful parsing of alerts from nws.py so this can be colourized
        for alert in data['alerts']:
            irc.reply(event, alert['title'] + ' Expires at: ' +
                      str(datetime.datetime.fromtimestamp(int(alert['expires']))))

    k = 1

    second_output = preface_location(name)  # , region, new_countryName)

    for day in days:
        # give me float(s) with only one significant digit
        form = '%.1f'

        hi = form % (day['temperatureMax'])
        low = form % (day['temperatureMin'])
        dew = form % (day['dewPoint'])

        # convert measurements in F to C
        hiC = form % ((float(day['temperatureMax']) - 32) * (5.0 / 9.0))
        lowC = form % ((float(day['temperatureMin']) - 32) * (5.0 / 9.0))
        dewC = form % ((float(day['dewPoint'] - 32)) * (5.0 / 9.0))

        # value taken from, https://is.gd/3dNrbW
        windspeedC = form % (float(day['windSpeed']) * 1.609344)
        windspeed = form % (day['windSpeed'])
        summary = day['summary']
        day_ts = day['time']
        if "sunriseTime" in day:
            day_ts = int(day['sunriseTime'])

        dotw_day = datetime.datetime.fromtimestamp(day_ts).weekday()
        dotw_day_pretty = '\x0310\x02\x1F%s\x1F\x02\x03' % (dotw[dotw_day])

        line = '%s: \x02\x0304%sF (%sC)\x03\x02 / \x02\x0312%sF (%sC)\x03\x02, \x1FDew\x1F: %sF (%sC), \x1FWind\x1F: %smph (%skmh), %s | '

        # remove extra whitespace
        dotw_day_pretty = dotw_day_pretty.strip()
        hi = hi.strip()
        low = low.strip()
        dew = dew.strip()
        windspeed = windspeed.strip()
        summary = summary.strip()

        summary = chomp_desc(summary)

        # only show 'today' and the next 3-days.
        # but only show 2 days on each line
        if k <= 2:
            output += line % (dotw_day_pretty, hi, hiC, low,
                              lowC, dew, dewC, windspeed, windspeedC, summary)
        elif k <= 4:
            second_output += line % (dotw_day_pretty, hi, hiC, low,
                                     lowC, dew, dewC, windspeed, windspeedC, summary)
        else:
            break

        k += 1

    # chomp off the ending |
    if output.endswith(' | '):
        output = output[:-3]

    # say the first part
    irc.reply(event, output)

    if second_output.endswith(' | '):
        second_output = second_output[:-3]

    # required according to ToS by darksky.net
    second_output += ' (Powered by Dark Sky, darksky.net)'
    irc.reply(event, second_output)


@add_cmd('weather-darksky', min_args=1)
def forecastio_current_weather(bot, event, irc, args):
    if not hasattr(config, 'forecastio_apikey'):
        return irc.reply(event, 'Please sign up for a darksky.net API key at https://darksky.net/')

    name, lat, lng = location(" ".join(args))
    if name == 'ImportError' and not lat and not lng:
        return install_geopy

    url = 'https://api.darksky.net/forecast/%s/%s,%s'

    # do some error checking
    try:
        # if the int(ernet) is working this should work, \o/
        page = web.get(url % (config.forecastio_apikey, lat, lng))
    except Exception:
        # well, crap, check your int(ernet), and if you can access darksky.net
        return irc.reply(event, 'Could not acess https://api.darksky.net/')

    try:
        # we want tasty JSON
        data = page.json()
    except Exception:
        # that wasn't tasty
        return irc.reply(event, 'The server did not return anything that was readable as JSON.')

    if 'currently' not in data:
        # doesn't happen until the GPS coords are completely bonkers
        return irc.reply(event, 'No information obtained from darksky.net for the given location: %s,' % (name, lat, lng,))

    # let the fun begin!!

    today = data['currently']

    cond = today['icon']  # 0.17
    cover = today['cloudCover']
    temp = today['temperature']
    dew = today['dewPoint']
    pressure = today['pressure']
    speed = today['windSpeed']
    degrees = today['windBearing']
    humidity = today['humidity']
    APtemp = today['apparentTemperature']

    # this code is different than the section in the previous sectio
    # as darksky.net uses more precise measurements than NOAA
    if cover >= 0.8:
        cover_word = 'Overcast'
    elif cover >= 0.5:
        cover_word = 'Cloudy'
    elif cover >= 0.2:
        cover_word = 'Scattered'
    else:
        cover_word = 'Clear'

    temp_c = (temp - 32) / 1.8
    temp = '%.1f\u00B0F (%.1f\u00B0C)' % (temp, temp_c)

    dew_c = (dew - 32) / 1.8
    dew = '%.1f\u00B0F (%.1f\u00B0C)' % (dew, dew_c)

    APtemp_c = (APtemp - 32) / 1.8
    APtemp = '%.1f\u00B0F (%.1f\u00B0C)' % (APtemp, APtemp_c)

    humidity = str(int(float(humidity) * 100)) + '%'

    pressure = '%.2fin (%.2fmb)' % (pressure * 0.0295301, pressure)
    cond = cond.replace('-', ' ')
    cond = cond.title()

    description = speed_desc(speed)

    degrees = wind_dir(degrees)

    # value taken from, https://is.gd/3dNrbW
    speedC = 1.609344 * speed
    wind = '%s %.1fmph (%.1fkmh) (%s)' % (description, speed, speedC, degrees)

    # ISO-8601 ftw, https://xkcd.com/1179/
    time = datetime.datetime.fromtimestamp(
        int(today['time'])).strftime('%Y-%m-%d %H:%M:%S')

    # build output str(ing).
    # a bit messy, but better than other alternatives
    output = str()
    output += '\x1FCover\x1F: ' + cover_word
    output += ', \x1FTemp\x1F: ' + temp
    output += ', \x1FDew Point\x1F: ' + dew
    output += ', \x1FHumidity\x1F: ' + humidity
    output += ', \x1FApparent Temp\x1F: ' + APtemp
    output += ', \x1FPressure\x1F: ' + pressure
    if cond:
        output += ', \x1FCondition\x1F: ' + cond
    output += ', \x1FWind\x1F: ' + wind
    output += ' - '
    output += name
    output + '; %s UTC' % time

    # required according to ToS by darksky.net
    output += ' (Powered by Dark Sky, darksky.net)'
    irc.reply(event, output)


def make_rh_C(temp, dewpoint):
    return 100.0 - (5.0 * (temp - dewpoint))


def make_rh_F(temp, dewpoint):
    return 100.0 - ((25.0 / 9.0) * (temp - dewpoint))


def gen_heat_index(temp, rh):
    # based on https://en.wikipedia.org/wiki/Heat_index#Formula
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783 * (10 ** (-3))
    c6 = -5.481717 * (10 ** (-2))
    c7 = 1.22874 * (10 ** (-3))
    c8 = 8.5282 * (10 ** (-4))
    c9 = -1.99 * (10 ** (-6))

    heat_index = c1 + c2*temp + c3*rh + c4*temp*rh + c5*temp*temp + \
        c6*rh*rh + c7*temp*temp*rh + c8*temp*rh*rh + c9*temp*temp*rh*rh
    return heat_index


def add_degree(txt):
    if ' F' in txt:
        txt = re.sub(' F', '\u00B0F', txt)
    else:
        txt = re.sub('F', '\u00B0F', txt)

    if ' C' in txt:
        txt = re.sub(' C', '\u00B0C', txt)
    else:
        txt = re.sub('C', '\u00B0C', txt)
    return (txt.encode('utf-8')).decode('utf-8')


@add_cmd('weather-wu', min_args=1)
def weather_wunderground(bot, event, irc, args):
    if not hasattr(config, 'wunderground_apikey'):
        return irc.reply(event, 'Please sign up for a wunderground.com API key at https://www.wunderground.com/weather/api/ or try .wx-noaa or .weather-noaa')

    apikey = config.wunderground_apikey

    url = 'https://api.wunderground.com/api/%s/conditions/geolookup/q/%s.json'

    try:
        page = web.get(url % (apikey, urllib.parse.quote(" ".join(args))))
    except Exception:
        return irc.reply(event, "We could not access wunderground.com's API at the moment.")

    useful = False

    try:
        useful = page.json()

        if 'results' in useful['response']:
            txt = useful['response']['results'][0]['zmw']
            useful = json.loads(web.get(url % (apikey, 'zmw:'+txt)))
    except Exception:
        return irc.reply(event, 'We could not obtain useful information from the wunderground.com API.')

    if 'response' in useful and 'error' in useful['response'] and 'description' in useful['response']['error']:
        return irc.reply(event, str(useful['response']['error']['description']))

    if 'current_observation' not in useful:
        return irc.reply(event, 'No observations currently found.')
    current = useful['current_observation']

    condition = current['weather']
    temp = current['temperature_str(ing)']
    wind_kph = current['wind_kph']
    wind_mph = current['wind_mph']
    wind_dir = current['wind_dir']
    feelslike = current['feelslike_str(ing)']
    dewpoint = current['dewpoint(_str(ing))']
    location = current['observation_location']['full']
    time_updated = current['observation_time']
    rh = current['relative_humidity']
    pressure_in = current['pressure_in']
    pressure_mb = current['pressure_mb']
    pressure_trend = current['pressure_trend']

    if pressure_trend == '-':
        pressure_trend = '\u2193'
    elif pressure_trend == '+':
        pressure_trend = '\u2191'
    elif pressure_trend == '0':
        pressure_trend = '\u2192'

    time_updated = re.sub('Last Updated on ',
                          '\x1FLast Updated\x1F: ', time_updated)

    output = str()
    output += '\x1FCover\x1F: ' + condition
    output += ', \x1FTemp\x1F: ' + add_degree(temp)
    output += ', \x1FDew Point\x1F: ' + add_degree(dewpoint)
    output += ', \x1FHumdity\x1F: ' + rh
    output += ', \x1FFeels Like\x1F: ' + add_degree(feelslike)
    output += ', \x1FPressure\x1F: ' + \
        '[%s] %sin (%smb)' % (pressure_trend, pressure_in, pressure_mb)
    output += ', \x1FWind\x1F: ' + \
        'From the %s at %s mph (%s kmh)' % (wind_dir, wind_mph, wind_kph)
    output += ', \x1FLocation\x1F: ' + \
        location.encode('utf-8').decode('utf-8')
    output += ', ' + time_updated

    output += ', (Powered by Wunderground, wunderground.com)'

    irc.reply(event, output)


def preface_location(ci, reg='', cty=''):
    out = str()
    out += '[' + ci
    if reg:
        out += ', ' + reg
    if cty:
        out += ', %s' % cty
    out += '] '
    return out


@add_cmd('forecast-wu', min_args=1)
def forecast_wg(bot, event, irc, args):
    if not hasattr(config, 'wunderground_apikey'):
        return irc.reply(event, 'Please sign up for a wunderground.com API key at https://www.wunderground.com/weather/api/ or try .wx-noaa or .weather-noaa')

    apikey = config.wunderground_apikey

    url = 'https://api.wunderground.com/api/%s/forecast10day/geolookup/q/%s.json'

    url_new = url % (apikey, args[0])

    try:
        page = web.get(url_new)
    except Exception:
        return irc.reply(event, "We could not access wunderground.com's API at the moment.")

    try:
        useful = page.json()
        if 'results' in useful['response']:
            txt = useful['response']['results'][0]['zmw']
            useful = web.get(url % (apikey, 'zmw:'+txt)).json()
    except Exception:
        return irc.reply(event, 'We could not obtain useful information from the wunderground.com API.')

    if 'response' in useful and 'error' in useful['response'] and 'description' in useful['response']['error']:
        return irc.reply(event, str(useful['response']['error']['description']))

    if 'forecast' not in useful:
        return irc.reply(event, 'We could not find a forecast for the given location.')

    days = useful['forecast']['simpleforecast']['forecastday']
    forecast_args = useful['forecast']['txt_forecast']['forecastday']

    days_args = list()

    for each in forecast_args:
        txt = each['fctargs']
        temp = txt.split('. Low')
        temp = temp[0]

        temp = temp.split('. High')
        temp = temp[0]

        temp = chomp_desc(temp)

        days_args.appendtemp

    city = useful['location']['city']

    region = str()
    if 'state' in useful['location']:
        region += useful['location']['state']

    country = useful['location']['country_name']

    output = preface_location(city, region, country)
    output_second = preface_location(city, region, country)

    k = 0
    for day in days:
        day_of_week = day['date']['weekday_short']
        highs = '\x02\x0304%s\u00B0F (%s\u00B0C)\x03\x02' % (
            day['high']['fahrenheit'], day['high']['celsius'])
        lows = '\x02\x0302%s\u00B0F (%s\u00B0C)\x03\x02' % (
            day['low']['fahrenheit'], day['low']['celsius'])

        days_args_temp = days_args[k]
        if not days_args[k].endswith('.'):
            days_args_temp += '.'

        days_args1_temp = days_args[k + 1]
        if not days_args[k + 1].endswith('.'):
            days_args1_temp += '.'

        temp = '\x02\x0310%s\x03\x02: %s / %s, AM: %s PM: %s | ' % (
            day_of_week, highs, lows, days_args_temp, days_args1_temp)

        k += 2
        if (k / 2.) <= 2:
            output += temp
        elif 4 >= (k / 2.) > 2:
            output_second += temp

    output = output[:-3]
    output_second = output_second[:-3]

    irc.reply(event, output)
    irc.reply(event, output_second)
