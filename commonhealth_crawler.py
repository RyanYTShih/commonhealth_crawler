import datetime
import json

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


host = 'https://www.commonhealth.com.tw/'
url = host + 'channel/44'
page_total_num = 103

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

def get_posts(page_link):
    post_list = []
    r = requests.get(page_link, headers=headers)

    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        posts = soup.find('div', class_='tab__target').find_all('a', class_=['recommend recommend--channels', 'recommend__media recommend__media--top'])
        for p in posts:
            if host in p.get('href'):
                post_list.append(p.get('href'))
        return post_list
    return None

def get_post_data(link):
    post_data = {
        'title': '',
        'view_count': -1,
        'author': [],
        'publish_time': '',
        'article_source': '',
        'content': '',
        'keywords': []
    }
    post = requests.get(link, headers=headers)
    soup = BeautifulSoup(post.text, 'html.parser')
    try:
        post_data['title'] = soup.find('h1', class_='title').text
    except:
        pass

    try:
        post_data['view_count'] = int(soup.find('div', class_='info__line info__line--view').find('span').text.replace(',', ''))
    except:
        pass
    info = soup.find('div', class_='info__line info__line--data')
    try:
        post_data['author'] = [name for name in info.find('span', id='author_name').text.split('、')]
    except:
        pass

    try:
        post_data['publish_time'] = info.find('span', id='publish_time').text
    except:
        pass

    try:
        post_data['article_source'] = info.find('span', id='article_source').text.strip()
    except:
        pass

    try:
        post_data['content'] = soup.find('div', class_='essay').getText()
    except:
        pass
    
    try:
        post_data['keywords'] = [k.get('data-keyword') for k in soup.find('div', class_='keywords__content').find_all('a', class_='tags tags--normal keywords')]
    except:
        pass
    return post_data


def main():
    json_data = []
    for page_num in tqdm(range(1, page_total_num + 1)):
        posts = get_posts(url + '?page=' + str(page_num))
        for link in posts:
            json_data.append(get_post_data(link))

    result = json.dumps(json_data, ensure_ascii=False, indent=2)
    filename = 'commonhealth-' + str(datetime.datetime.now().strftime('%y%m%d-%H%M%S')) + '-' + str(page_total_num) + 'pages.json'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)


if __name__ == '__main__':
    main()