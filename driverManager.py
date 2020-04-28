import time
from selenium import webdriver
import json
import requests
from bs4 import BeautifulSoup
from threading import Thread
import exle_manager
import random

REGION = "chelyabinsk"

region_count = []


def inner(tag):
    try:
        return ''.join(tag.findAll(text=True)).replace('\n', '').replace('\t', '')
    except Exception as er:
        return " "


def save_file(data, filename, region):
    # print(data)
    try:
        g = open('beauty_pack/{0}/{1}.json'.format(region, filename), 'r')
        f = open('beauty_pack/{0}/{1}.json'.format(region, filename + '_!_' + str(random.randint(1, 1000))), 'w')
        f.write(json.dumps(data, ensure_ascii=False))
        f.close()
    except Exception:
        f = open('beauty_pack/{0}/{1}.json'.format(region, filename), 'w')
        f.write(json.dumps(data, ensure_ascii=False))
        f.close()


def get_widget(parsed_html):
    try:
        return \
        str(parsed_html.body.find('div', attrs={'class': "js-action-request-btn"}).find('script')).split('"url":')[
            1].split(',"')[0]
    except Exception as er:
        print('widget err', er)
        return 'no'


def get_reviews(parsed_html):
    reviews = []
    for i in parsed_html.body.findAll('div', attrs={'class': 'comment-container'}):
        try:
            reviews.append({
                'rating': inner(i.find('span', attrs={'class': 'stars-rating-text'})),
                'name': inner(i.find('span', attrs={'class': 'name'})),
                'comment': inner(i.find('div', attrs={'class': 'comment-text'}))
            })
        except Exception:
            continue
    return reviews


def get_images(parsed_html):
    images = []
    try:
        for i in parsed_html.body.find('ul', attrs={'class': 'photo-list'}).findAll('li'):
            images.append(i['data-src'])
    except Exception:
        print('no img list')
    return images


def get_priceList(parsed_html):
    price_list = []
    try:
        for i in parsed_html.body.findAll('div', attrs={'class': 'mp-markerlist-item'}):
            price_list.append({
                'name': inner(i.find('div', attrs={'class': 'mp-markerlist-item-name'})),
                'min-price': inner(i.find('span', attrs={'class': 'mp-markerlist-item-cost__min'})),
                'max-price': inner(i.find('span', attrs={'class': 'mp-markerlist-item-cost__max'})),
            })
    except Exception:
        print('no price list')
    return price_list


def get_stuff_List(parsed_html):
    stuff_list = []
    try:
        for i in parsed_html.body.findAll('li', attrs={'class': 'prof-item'}):
            stuff_list.append({
                'name': inner(i.find('div', attrs={'class': 'prof-name'})),
                'prof': inner(i.find('div', attrs={'class': 'prof-orientation'})),
                'img': i.find('a', attrs={'class': 'prof-photo'})['style']
            })
    except Exception:
        print('no stuff list')
    return stuff_list


def get_sales_list(parsed_html):
    promos = []
    try:
        for i in parsed_html.body.findAll('div', attrs={'class': 'promo-card-body'}):
            promos.append({
                'title': inner(i.find('div', attrs={'class': 'promo-card-title'})),
                'tag': inner(i.find('div', attrs={'class': 'promo-card-tags'})),
                'card': inner(i.find('div', attrs={'class': 'promo-card-promo'}))
            })
    except Exception:
        print('no promo')
    return promos


def get_tags_list(parsed_html):
    tags = []
    try:
        for i in parsed_html.body.findAll('span', attrs={'class': 'title'}):
            try:
                if inner(i) != '':
                    tags.append(inner(i))
            except Exception:
                pass
    except Exception:
        print('no tags')
    return tags


def social_links(parsed_html):
    result = []
    try:
        for r in parsed_html.body.findAll('div', attrs={'class': 'service-website'}):
            if r.findAll('a'):
                for i in r.findAll('a'):
                    result.append(inner(i) + ' ' + i['href'])
    except Exception:
        print('no sn')
    return result


def get_metro(parse_html):
    try:
        return [inner(m) for m in parse_html.body.findAll('div', attrs={'class': 'address-metro'})]
    except Exception as er:
        print('no metro')
        return []


def get_rayon(parse_html):
    try:
        result = []
        for r in parse_html.body.findAll('div', attrs={'class': 'service-map'}):
            for d in r.findAll('div'):
                if d.findAll('a', attrs={'class': 'invisible-link'}):
                    if len(result) == 0:
                        result = [inner(t) for t in d.findAll('a')]
                    else:
                        rt = [inner(t) for t in d.findAll('a')]
                        if len(rt) < len(result): result = rt
        return result
    except Exception as er:
        print('no rayon')
        return []


def parse_page(html, title, region):
    # response = requests.get(url)
    parsed_html = BeautifulSoup(html)
    try:
        name_t = parsed_html.body.find('h2')
        name = inner(name_t)
    except Exception:
        name = title
    rating = inner(parsed_html.body.find('span', attrs={'class': 'rating-value'}))
    phone = parsed_html.body.find('a', attrs={'class': 'tel-phone'})['href']
    address = inner(parsed_html.body.find('address', attrs={'class': 'iblock'}))
    work_time = inner(parsed_html.body.find('dl', attrs={'class': 'fluid uit-cover'}))
    site = parsed_html.body.find('div', attrs={'class': 'service-website'}).find('a')['href']
    try:
        price = inner(
            parsed_html.body.find('div', attrs={'class': 'time__price'}).find('span', attrs={'itemprop': 'priceRange'}))
    except Exception:
        price = 0
    price_list = get_priceList(parsed_html)
    stuff_list = get_stuff_List(parsed_html)
    reviews = get_reviews(parsed_html)
    images = get_images(parsed_html)
    promo_list = get_sales_list(parsed_html)
    tag_list = get_tags_list(parsed_html)
    lonlat = ' , '
    for i in parsed_html.body.find_all('script'):
        if 'lonlat:' in str(i):
            lonlat = str(i).split('lonlat: [')[1].split(']	};')[0]
    witget = get_widget(parsed_html)
    metro = get_metro(parsed_html)
    rayons = get_rayon(parsed_html)
    s_n = social_links(parsed_html)
    is_reute = 'No'
    for i in parsed_html.body.findAll('dt'):
        if inner(i) == "Адреса сети":
            is_reute = 'Yes'

    result = {
        'title': name,
        'rating': rating,
        'phone': phone,
        'address': address,
        'metro': metro,
        'rayons': rayons,
        'lonlat': lonlat.split(','),
        'work_time': work_time,
        'price': price,
        'price_list': price_list,
        'stuff_list': stuff_list,
        'site': site,
        'its route': is_reute,
        'social_links': s_n,
        'reviews': reviews,
        'images': images,
        'promos': promo_list,
        'tags': tag_list,
        'witget': witget
    }
    save_file(result, title.replace(' ', '_').replace('.', '_'), region.split('_')[0])
    return result


def get_page(url, title, driver, region):
    driver.get(url)
    try:
        driver.get(driver.find_element_by_class_name('js-show-more').get_attribute('href'))
    except Exception:
        pass
    try:
        driver.find_element_by_class_name('js-next-page').click()
    except Exception:
        pass
    # driver.find_element_by_class_name('service-block-collapse').click()
    html = driver.find_element_by_tag_name('body').get_attribute('innerHTML')
    return parse_page(html, title, region)


def chrome_start(region):
    option = webdriver.ChromeOptions()
    chrome_prefs = {}
    option.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

    driver = webdriver.Chrome('driver/chromedriver', chrome_options=option)
    driver.get('https://zoon.ru/{0}/beauty/'.format(region))

    list_sa = []
    for i in range(100):
        print(i)
        try:
            driver.find_element_by_class_name('js-next-page').click()
            time.sleep(5)
        except Exception:
            continue

    hs = driver.find_elements_by_class_name('H3')
    for i in hs:
        try:
            list_sa.append({
                'name': i.find_element_by_tag_name('a').get_attribute('innerHTML').replace('\n', '').replace('\t', ''),
                'url': i.find_element_by_tag_name('a').get_attribute('href')
            })
        #     js-next-page button button-block button40 button-primary
        except Exception:
            pass
    result = json.dumps({'data': list_sa}, ensure_ascii=False)
    f = open('beauty_pack/list_clums_{0}.txt'.format(region), 'w')
    f.write(result)
    f.close()
    print(len(list_sa))


def list_wiget(url, name, driver):
    driver.get(url)
    try:
        # print(driver.find_element_by_class_name("js-action-request-btn").find_element_by_tag_name("script").get_attribute('innerHTML'))
        # print(driver.find_element_by_class_name("js-action-request-btn").find_element_by_tag_name("script").get_attribute('innerHTML').split('"url":'))
        div_a = \
        driver.find_element_by_class_name("js-action-request-btn").find_element_by_tag_name("script").get_attribute(
            'innerHTML').split('"url":')[1].split(',"')[0]
        print('wig', div_a)
        return {'name': name, "url_w": div_a}
    except Exception as er:
        print("wig", None)
        return {'name': name, "url_w": None}


def looper(region):
    f = open('beauty_pack/list_clums_{0}.txt'.format(region), 'r')
    res = json.load(f)
    f.close()
    count = 0
    result_list = []
    bad_list = []
    for i in res['data']:
        print(i)
        options = webdriver.ChromeOptions()
        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        options.add_argument('headless')
        driver = webdriver.Chrome('driver/chromedriver', chrome_options=options)
        try:
            result_list.append(get_page(i['url'], i['name'], driver, region))
            # result_list.append(list_wiget(i['url'], i['name'], driver))
            print('good', count, i['name'])
            time.sleep(1)
        except Exception as er:
            print(i['name'], 'bad', er)
            bad_list.append(i)
        print(region, count, ' / ', len(res['data']))
        count += 1
        driver.close()
    save_file({'data': bad_list}, 'bad_list', region.split('_')[0])


def t_start():
    # chrome_start()
    # time.sleep(60)
    f = open('beauty_pack/list_clums_{0}.txt'.format(REGION), 'r')
    res = json.load(f)
    f.close()
    # driver = webdriver.Chrome('driver/chromedriver')
    result_list = []
    widget_list = []
    bad_list = []
    count = 0
    # driver = webdriver.Chrome('driver/chromedriver')
    # print(get_page("https://zoon.ru/msk/beauty/imidzh-laboratoriya_persona_lab_na_metro_rechnoj_vokzal/", "i['name']", driver))
    for i in res['data']:
        print(i)
        driver = webdriver.Chrome('driver/chromedriver')
        try:
            result_list.append(get_page(i['url'], i['name'], driver))
            # result_list.append(list_wiget(i['url'], i['name'], driver))
            print('good', count, i['name'])
            time.sleep(1)
        except Exception as er:
            print(i['name'], count, 'bad', er)
            bad_list.append(i)
        print(count, ' / ', len(res['data']))
        count += 1
        driver.close()

    # exle_manager.create_file_from_dict_list(REGION, result_list)
    save_file({'data': bad_list}, 'bad_list')
    # url = 'https://zoon.ru/msk/beauty/imidzh-laboratoriya_persona_lab_na_metro_rechnoj_vokzal'
    # print(get_page(url, "test", driver))


class Process(Thread):

    def __init__(self, region):
        Thread.__init__(self)
        self.region = region

    def run(self):
        looper(self.region)


class Scan(Thread):

    def __init__(self, region):
        Thread.__init__(self)
        self.region = region

    def run(self):
        chrome_start(self.region)


def start():
    # regions = ['biysk', 'blag', 'bratsk', 'bryansk', 'vladimir', 'volgograd', 'vologda', 'voronezh', 'gorno-altaisk', 'ivanovo', 'izhevsk', 'irkutsk', 'kazan', 'kaluga', 'kirov', 'komsomolsk', 'kostroma', 'krasnodar', 'kurgan', 'kursk']
    # regions = ['voronezh', 'lipetsk', 'magnitogorsk', 'makhachkala', 'murmansk', 'chelny', 'nizhnevartovsk', 'nn', 'tagil', 'novokuznetsk', 'novorossiysk', 'omsk', 'orenburg', 'orel', 'penza', 'perm', 'pskov', 'rostov', 'samara', 'saransk', 'saratov', 'smolensk', 'sochi', 'surgut', 'syktyvkar', 'tambov', 'tver', 'togliatti', 'tomsk', 'tula', 'tyumen', 'ulan-ude', 'ulyanovsk', 'ufa', 'khabarovsk', 'cheboksary', 'chita', 'yuzhnosakhalinsk', 'yakutsk', 'yaroslavl']
    regions = ['msk_1', 'msk_2', 'msk_3', 'msk_4', 'msk_5', 'msk_6', 'msk_7', 'msk_8', 'msk_9', 'msk']
    for r in range(95):
        if r < 51:
            continue
        proccess = Process('msk_{0}'.format(r))
        proccess.start()
        time.sleep(20 * 60)


def Q_start():
    regi = 'yakutsk'
    s = Scan(regi)
    s.start()
    regi = 'yaroslavl'
    s = Scan(regi)
    s.start()


def e_start():
    driver = webdriver.Chrome('driver/chromedriver')
    print(get_page('https://zoon.ru/msk/beauty/salon_epilyatsii_wax_go_na_maloj_bronnoj_ulitse/', 'w&n', driver, 'msk'))


def chrome_start_for_loc(region, url, driver):
    driver.get(url)

    list_sa = []
    for i in range(30):
        try:
            driver.find_element_by_class_name('js-next-page').click()
            time.sleep(1)
        except Exception:
            print('brake in ', i)
            break

    hs = driver.find_elements_by_class_name('H3')
    for i in hs:
        try:
            list_sa.append({
                'name': i.find_element_by_tag_name('a').get_attribute('innerHTML').replace('\n', '').replace('\t', ''),
                'url': i.find_element_by_tag_name('a').get_attribute('href')
            })
        #     js-next-page button button-block button40 button-primary
        except Exception:
            pass
    return list_sa


def start_4_nastia():
    urls_s = ['https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Митино',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Мичуринский%20проспект',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Молодёжная',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Мякинино',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Нагатинская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Нагорная',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Нахимовский%20проспект',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Некрасовка',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Нижегородская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новогиреево',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новокосино',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новокузнецкая',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новопеределкино',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новослободская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новохохловская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новоясеневская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Новые%20Черёмушки',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Озёрная',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Окружная',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Окская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Октябрьская',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Октябрьское%20поле',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Ольховая',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Орехово',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Отрадное',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Сокольники',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Солнцево',
              'https://zoon.ru/msk/beauty/?search_query_form=1&locations-metro%5B%5D=Спартак'
              ]
    list_sa = []
    pos = 0
    good = True
    i = 0
    option = webdriver.ChromeOptions()
    chrome_prefs = {}
    option.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    # stop
    stop = 92
    driver = webdriver.Chrome('driver/chromedriver.exe', chrome_options=option)
    for u in urls_s:
        if i < stop:
            i += 1
            pos += 1
            continue
        try:
            resi = chrome_start_for_loc('msk', u, driver)
            list_sa += resi
            f = open('beauty_pack/list_clums_{0}.txt'.format('msk_{0}'.format(pos)), 'w')
            f.write(json.dumps({'data': resi}, ensure_ascii=False))
            f.close()
            print(pos, '/', len(urls_s.split(' ')))
            pos += 1
            i += 1
        except Exception as er:
            print(er)
            print(pos, ' <- position faled')
            break
    print(pos, ' <- position complite')
    result = json.dumps({'data': list_sa}, ensure_ascii=False)
    f = open('beauty_pack/list_clums_{0}.txt'.format('msk_1000'), 'w')
    f.write(result)
    f.close()


def start_oo():
    options = webdriver.ChromeOptions()
    chrome_prefs = {}
    options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    options.add_argument('headless')
    driver = webdriver.Chrome('driver/chromedriver', chrome_options=options)
    try:
        print(get_page('https://zoon.ru/msk/beauty/salon_krasoty_moskvichka_na_metro_vystavochnaya/',
                       'Студия маникюра Алены Котовой на улице Адмирала Руднева', driver, 'msk'))
    except Exception as er:
        print(er)

    driver.close()
