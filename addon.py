import os
import xml.etree.ElementTree as et
import urlparse

import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmcvfs

plugin_url = sys.argv[0]
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()


class RadioSource():
    def __init__(self, xml=None, name=None):
        if xml is None:
            # Load XML node from name
            for xml in sources.iter("radio"):
                if name == xml.find("name").text:
                    break

        self.name = xml.find("name").text
        self.streams = dict((int(stream.get("bitrate", default=0)), stream.text) for stream in xml.findall("stream"))
        self.info = dict((child.tag, child.text) for child in xml if child.tag not in ("name", "stream"))
        self.url = "{}?source={}".format(plugin_url, self.name)

    def list_item(self):
        li = xbmcgui.ListItem(self.name, iconImage="DefaultAudio.png")
        li.setInfo("music", {"title": self.name, "artist": self.info.get("tagline", None)})
        li.setArt(self.__build_art())
        return li

    def play(self):
        max_bitrate = int(addon.getSetting("bitrate").split(" ")[0])
        bitrates = [bitrate for bitrate in self.streams.keys() if bitrate <= max_bitrate]
        url = streams[min(self.streams.keys())] if len(bitrates) == 0 else self.streams[max(bitrates)]

        li = self.list_item()
        li.setPath(url)
        xbmcplugin.setResolvedUrl(handle, True, li)
        

    def __build_art(self):
        art = {}
        for art_type in ("thumb", "fanart"):
            if self.info.get(art_type, None) is not None:
                path = os.path.join(addon.getAddonInfo("path"), "artwork", self.info[art_type])
                if os.path.isfile(path):
                    art[art_type] = path
        return art


def build_list():
    xbmcplugin.setContent(handle, "audio")
    # Loop through sources XML and create list item for each entry
    for item in sources.iter("radio"):
        source = RadioSource(xml=item)
        li = source.list_item()
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(handle=handle, url=source.url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(handle)


# Create sources file in addon_data folder
sources_path = os.path.join(addon.getAddonInfo("path"), "sources.xml")
if not xbmcvfs.exists(sources_path):
    xbmcvfs.copy(os.path.join(addon.getAddonInfo("path"), "resources", "sources.xml"), sources_path)

sources = et.fromstring(xbmcvfs.File(sources_path).read())
params = urlparse.parse_qs(sys.argv[2][1:])

if params.get("source", None) is None:
    build_list()
else:
    RadioSource(name=["source"][0]).play()
