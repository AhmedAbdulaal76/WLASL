import os
import json
import time
import sys
import urllib.request
import random
import logging

logging.basicConfig(filename='download_{}.log'.format(int(time.time())), filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Set this to youtube-dl if you want to use youtube-dl.
youtube_downloader = "yt-dlp"

def request_video(url, referer=''):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent}
    
    if referer:
        headers['Referer'] = referer

    request = urllib.request.Request(url, None, headers)
    logging.info('Requesting {}'.format(url))
    response = urllib.request.urlopen(request)
    data = response.read()
    return data

def save_video(data, saveto):
    with open(saveto, 'wb+') as f:
        f.write(data)
    time.sleep(random.uniform(0.5, 1.5))

def download_aslpro(url, dirname, video_id):
    saveto = os.path.join(dirname, '{}.swf'.format(video_id))
    if os.path.exists(saveto):
        logging.info('{} exists at {}'.format(video_id, saveto))
        return 

    data = request_video(url, referer='http://www.aslpro.com/cgi-bin/aslpro/aslpro.cgi')
    save_video(data, saveto)

def download_others(url, dirname, video_id):
    saveto = os.path.join(dirname, '{}.mp4'.format(video_id))
    if os.path.exists(saveto):
        logging.info('{} exists at {}'.format(video_id, saveto))
        return 
    
    data = request_video(url)
    save_video(data, saveto)

def select_download_method(url):
    if 'aslpro' in url:
        return download_aslpro
    else:
        return download_others

def download_nonyt_videos(indexfile, saveto='raw_videos'):
    content = json.load(open(indexfile))

    if not os.path.exists(saveto):
        os.mkdir(saveto)

    for entry in content:
        gloss = entry['gloss']
        instances = entry['instances']

        for inst in instances:
            video_url = inst['url']
            video_id = inst['video_id']
            
            logging.info('gloss: {}, video: {}.'.format(gloss, video_id))

            download_method = select_download_method(video_url)    
            try:
                download_method(video_url, saveto, video_id)
            except Exception as e:
                logging.error('Unsuccessful downloading - video {}'.format(video_id))

if __name__ == '__main__':
    index_file = 'WLASL_100.json'  # Use the WLASL-100 dataset
    logging.info('Start downloading non-youtube videos.')
    download_nonyt_videos(index_file)