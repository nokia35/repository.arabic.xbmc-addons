import cookielib
import re
import urllib2
from BeautifulSoup import BeautifulSoup
from models import ChannelItem

HEADER_REFERER = 'http://www.teledunet.com/'
HEADER_HOST = 'www.teledunet.com'
HEADER_USER_AGENT = 'Mozilla/5.0'
HEADER_COOKIE = 'PHPSESSID=5ee89a09bf610767e0150512f90513ed'
TELEDUNET_TIMEPLAYER_URL = 'http://www.teledunet.com/tv_/?channel=%s'

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


def _get(url):
    """Performs a GET request for the given url and returns the response"""
    conn = urllib2.urlopen(url)
    resp = conn.read()
    conn.close()
    return resp


def _html(url):
    """Downloads the resource at the given url and parses via BeautifulSoup"""
    return BeautifulSoup(_get(url), convertEntities=BeautifulSoup.HTML_ENTITIES)


def __get_channel_time_player(channel_name):
    url = TELEDUNET_TIMEPLAYER_URL % channel_name

    # Set custom header parameters to simulate request is coming from website
    req = urllib2.Request(url)
    req.add_header('Referer', HEADER_REFERER)
    req.add_header('Host', HEADER_HOST)
    req.add_header('User-agent', HEADER_USER_AGENT)
    req.add_header('Cookie', HEADER_COOKIE)

    html = _get(req)

    m = re.search('time_player=(.*);', html, re.M | re.I)
    time_player_str = eval(m.group(1))

    m = re.search('curent_media=\'(.*)\';', html, re.M | re.I)
    rtmp_url = m.group(1)
    play_path = rtmp_url[rtmp_url.rfind("/") + 1:]
    return rtmp_url, play_path, repr(time_player_str).rstrip('0').rstrip('.')


def get_rtmp_params(channel_name):
    rtmp_url, play_path, time_player_id = __get_channel_time_player(channel_name)

    return {
        'rtmp_url': rtmp_url,
        'playpath': play_path,
        'app': 'teledunet',
        'swf_url': ('http://www.teledunet.com/tv/player.swf?'
                    'bufferlength=5&'
                    'repeat=single&'
                    'autostart=true&'
                    'id0=%(time_player)s&'
                    'streamer=%(rtmp_url)s&'
                    'file=%(channel_name)s&'
                    'provider=rtmp'
                   ) % {'time_player': time_player_id, 'channel_name': play_path, 'rtmp_url': rtmp_url},
        'video_page_url': 'http://www.teledunet.com/tv/?channel=%s&no_pub' % play_path,
        'live': '1'
    }


def get_channels():
    html = _html(HEADER_REFERER)
    return [ChannelItem(el) for el in (html.findAll("div", {"class": "div_channel"}))]


def debug():
    #print get_channels()
    #print _get_channel_time_player('2m')
    #print get_rtmp_params('2m')
    pass


if __name__ == '__main__':
    debug()