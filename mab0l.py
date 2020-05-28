import os
import zipfile
import struct
import time
from collections import defaultdict

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

[os.remove(x) for x in os.listdir(".") if x.endswith('.osz')]

to_download = {
    'NoMod': [719231, 931860, 1438557, 1043346, 1434351],
    'Hidden': [1278874, 50658, 1649675],
    'HardRock': [1303812, 1616716, 834589],
    'DoubleTime': [525866, 1324653, 1414553],
    'FreeMod': [1086057, 656385, 1007896],
    'TieBreaker': [1108826]
}

tourney_acronym = '112'

osu_username = 'goeo_'
osu_password = 'not gonna leak that'

chrome_driver_path = None  # './chromedriver.exe'
chrome_path = None

mappool_hashes = defaultdict(list)

to_zip = []


def uleb128_encode(num):
    arr = bytearray()
    length = 0
    if num == 0:
        return b'\x00'
    while num > 0:
        arr.append(num & 127)
        num >>= 7
        if num != 0:
            arr[length] |= 128
        length += 1
    return arr


def make_string(string):
    if not string:
        return b'\x00'
    ret = bytearray()
    ret.append(0x0b)
    ret += uleb128_encode(len(string))
    ret += string.encode('utf-8')
    return ret


options = Options()
options.headless = True
options.add_argument('--window-size=1920,1080')
options.add_experimental_option('prefs', {'download.default_directory': str(os.getcwd())})

if chrome_path:
    options.binary_location = chrome_path

if chrome_driver_path:
    driver = webdriver.Chrome(chrome_driver_path, options=options)
else:
    driver = webdriver.Chrome(options=options)

driver.get('https://osu.ppy.sh')

wait = WebDriverWait(driver, 10)
wait.until(EC.title_contains('welcome'))

sign_in = driver.find_element_by_xpath(
    '''//div[@class='osu-layout__section osu-layout__section--full js-content home_index']'''
    '''/nav[@class='osu-layout__row']/div[@class='landing-nav hidden-xs']/div[@class='landing-nav__section'][2]'''
    '''/a[@class='landing-nav__link js-nav-toggle js-click-menu js-user-login--menu']'''
)
sign_in.click()

username = driver.find_element_by_name('username')
username.clear()
username.send_keys(osu_username)
password = driver.find_element_by_name('password')
password.clear()
password.send_keys(osu_password)
sign_in_ = driver.find_element_by_xpath(
    '''//div[@class='osu-layout__section osu-layout__section--full js-content home_index']/'''
    '''div[@class='login-box login-box--landing']/div[@class='login-box__content js-click-menu '''
    '''js-nav2--centered-popup js-nav2--login-box js-click-menu--active']/form/div[@class='login-box__row '''
    '''login-box__row--actions']/div[@class='login-box__action']/button[@class='btn-osu-big btn-osu-big--nav-popup']'''
    '''/div[@class='btn-osu-big__content']/span[@class='btn-osu-big__left']'''
)
sign_in_.click()

wait = WebDriverWait(driver, 10)
wait.until(EC.title_contains('dashboard'))

for mod, maps_mod in to_download.items():
    for beatmap in maps_mod:
        try:
            current_map = requests.get('http://ripple.moe/api/get_beatmaps?b=%s' % beatmap).json()[0]
        except KeyError:
            raise ValueError("Map %s in mod %s could not be found on the Ripple API" % (beatmap, mod))

        mappool_hashes[mod] += [current_map["file_md5"]]

        driver.get('https://osu.ppy.sh/beatmapsets/%s' % current_map["beatmapset_id"])
        download = driver.find_elements_by_xpath(
            '''//a[@class='btn-osu-big btn-osu-big--beatmapset-header js-beatmapset-download-link']'''
        )[-1]
        download.click()

# wait for downloads to finish
while any(x.endswith('.crdownload') for x in os.listdir(".")):
    time.sleep(1)
driver.close()

to_zip += [x for x in os.listdir(".") if x.endswith('.osz')]

collection_db = bytearray()
collection_db += struct.pack("<i", 20200519)
collection_db += struct.pack("<i", len(to_download))

for mod, hashes_mod in mappool_hashes.items():
    collection_db += make_string("%s %s" % (tourney_acronym, mod))
    collection_db += struct.pack("<i", len(hashes_mod))
    for map_hash in hashes_mod:
        collection_db += make_string(map_hash)

with open("collection.db", "wb") as db_file:
    db_file.write(collection_db)

to_zip += ["collection.db"]

with zipfile.ZipFile("%s_mappool.zip" % tourney_acronym, "w") as pool_zip:
    for filename in to_zip:
        pool_zip.write(filename)
