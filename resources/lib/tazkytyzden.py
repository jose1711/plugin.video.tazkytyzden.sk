# -*- coding: UTF-8 -*-
# /*
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import re
import urllib
import urllib2
import cookielib
import xbmcaddon
import xbmcgui
from xml.etree.ElementTree import fromstring
from demjson import demjson

import util
import resolver
from provider import ResolveException
from provider import ContentProvider


__addon__ = xbmcaddon.Addon()


class TazkytyzdenContentProvider(ContentProvider):
    def __init__(self, username=None, password=None, filter=None,
                 tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'tazkytyzden.sk',
                                 'https://tazkytyzden.sk',
                                 username, password, filter, tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.url = 'https://tazkytyzden.sk/'

    def capabilities(self):
        return ['list_episodes', 'resolve']

    def list(self, url):
        return self.list_episodes()

    def categories(self):
        url = self.url
        result = []
        data = util.parse_html(url)
        for episode_data in data.select('[data-slick]')[1].select('a.cz_grid_link'):
            # print(episode_data)
            link = episode_data.get('href')
            img = episode_data.img.get('data-src')
            title = episode_data.parent.h3.text
            item = self.video_item()
            item['title'] = title
            item['duration'] = 0
            item['img'] = img
            item['url'] = link
            result.append(item)

        item = self.dir_item()
        item['type'] = 'prev'
        item['url'] = 'nada'
        result.append(item)
        return result

    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        resolved = []
        item = item.copy()
        url = self._url(item['url'])
        data = util.parse_html(url)
        video_url = [x for x in data.select('[src]') if 'video.azet.sk/embed' in x['src']][0]['src']
        # print(video_url)
        video_index = video_url.split('/')[-1]
        video_json = demjson.decode(util.request('https://video.azet.sk/embed/playlistVideoJson/{0}?v=17&ref=video.azet.sk'.format(video_index)))
        stream_url = video_json[0]['sources'][0]['file']
        item = self.video_item()
        item['url'] = stream_url
        item['quality'] = 0
        item['surl'] = stream_url
        result.append(item)
        return result
