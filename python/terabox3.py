import re, requests, hashlib, time
import logging
from urllib.parse import quote, urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_between(text, start, end):
    try:
        start_index = text.index(start) + len(start)
        end_index = text.index(end, start_index)
        return text[start_index:end_index]
    except ValueError:
        return None

class TeraboxFile():

    #--> Initialization (requests, headers, and result)
    def __init__(self) -> None:

        self.r : object = requests.Session()
        self.headers : dict[str,str] = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6',
            'Connection': 'keep-alive',
            'Cookie': 'csrfToken=x0h2WkCSJZZ_ncegDtpABKzt; browserid=Bx3OwxDFKx7eOi8np2AQo2HhlYs5Ww9S8GDf6Bg0q8MTw7cl_3hv7LEcgzk=; lang=en; TSID=pdZVCjBvomsN0LnvT407VJiaJZlfHlVy; __bid_n=187fc5b9ec480cfe574207; ndus=Y-ZNVKxteHuixZLS-xPAQRmqh5zukWbTHVjen34w; __stripe_mid=895ddb1a-fe7d-43fa-a124-406268fe0d0c36e2ae; ndut_fmt=FF870BBFA15F9038B3A39F5DDDF1188864768A8E63DC6AEC54785FCD371BB182',
            'DNT': '1',
            'Host': 'www.4funbox.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        self.result : dict[str,any] = {'status':'failed', 'sign':'', 'timestamp':'', 'shareid':'', 'uk':'', 'list':[]}

    #--> Main control (get short_url, init authorization, and get root file)
    def search(self, url:str) -> None:

        try:
            logger.info(f"Searching URL: {url}")
            # First request to get jsToken and logid
            response = self.r.get(url, headers=self.headers, allow_redirects=True)
            response_text = response.text
            
            # Extract jsToken and logid
            js_token = find_between(response_text, 'fn%28%22', '%22%29')
            logid = find_between(response_text, 'dp-logid=', '&')
            
            if not js_token or not logid:
                logger.error("Failed to extract jsToken or logid")
                self.result['status'] = 'failed'
                return
                
            logger.info(f"Extracted jsToken: {js_token[:10]}... and logid: {logid}")
            
            # Parse the URL to get surl
            parsed_url = urlparse(response.url)
            query_params = parse_qs(parsed_url.query)
            surl = query_params.get('surl', [None])[0]
            
            if not surl:
                logger.error("Failed to extract surl")
                self.result['status'] = 'failed'
                return
                
            # Get file list
            list_params = {
                'app_id': '250528',
                'web': '1',
                'channel': 'dubox',
                'clienttype': '0',
                'jsToken': js_token,
                'dplogid': logid,
                'page': '1',
                'num': '20',
                'order': 'time',
                'desc': '1',
                'site_referer': response.url,
                'shorturl': surl,
                'root': '1'
            }
            
            list_response = self.r.get('https://www.4funbox.com/share/list', 
                                     params=list_params, 
                                     headers=self.headers)
            
            if list_response.status_code == 200:
                data = list_response.json()
                if 'list' in data and len(data['list']) > 0:
                    file_info = data['list'][0]
                    self.result['shareid'] = file_info.get('shareid', '')
                    self.result['uk'] = file_info.get('uk', '')
                    self.result['list'] = data['list']
                    self.result['status'] = 'success'
                    logger.info(f"Successfully got file info. ShareID: {self.result['shareid']}, UK: {self.result['uk']}")
                else:
                    logger.error("No files found in response")
                    self.result['status'] = 'failed'
            else:
                logger.error(f"Failed to get file list. Status code: {list_response.status_code}")
                self.result['status'] = 'failed'
                
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            self.result['status'] = 'failed'
            self.result['error'] = str(e)

    #--> Generate sign & timestamp
    def generateSign(self) -> None:

        try:
            # Generate timestamp
            timestamp = str(int(time.time()))
            
            # Generate sign using file information
            data = f"{self.result['shareid']}{self.result['uk']}{timestamp}"
            sign = hashlib.md5(data.encode()).hexdigest()
            
            self.result['sign'] = sign
            self.result['timestamp'] = timestamp
            self.result['status'] = 'success'
            logger.info(f"Generated sign: {sign} with timestamp: {timestamp}")
        except Exception as e:
            logger.error(f"Error generating sign: {str(e)}")
            self.result['status'] = 'failed'
            self.result['error'] = str(e)

    #--> Get payload (root / top layer / overall data) and init packing file information
    def getMainFile(self) -> None:

        try:
            url: str = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{self.short_url}&root=1'
            logger.info(f"Fetching main file info from: {url}")
            req : object = self.r.get(url, headers=self.headers, timeout=10).json()
            all_file = self.packData(req, self.short_url)
            if len(all_file):
                self.result['shareid']   = req['shareid']
                self.result['uk']        = req['uk']
                self.result['list']      = all_file
                logger.info(f"Successfully got file info. ShareID: {req['shareid']}, UK: {req['uk']}")
        except Exception as e:
            logger.error(f"Error getting main file: {str(e)}")
            self.result['status'] = 'failed'
            self.result['error'] = str(e)

    #--> Get child file data recursively (if any) and init packing file information
    def getChildFile(self, short_url, path:str='', root:str='0') -> list[dict[str, any]]:

        params = {'app_id':'250528', 'shorturl':short_url, 'root':root, 'dir':path}
        url = 'https://www.terabox.com/share/list?' + '&'.join([f'{a}={b}' for a,b in params.items()])
        req : object = self.r.get(url, headers=self.headers).json()
        return(self.packData(req, short_url))

    #--> Pack each file information
    def packData(self, req:dict, short_url:str) -> list[dict[str, any]]:
        all_file = [{
            'is_dir' : item['isdir'],
            'path'   : item['path'],
            'fs_id'  : item['fs_id'],
            'name'   : item['server_filename'],
            'type'   : self.checkFileType(item['server_filename']) if not bool(int(item.get('isdir'))) else 'other',
            'size'   : item.get('size') if not bool(int(item.get('isdir'))) else '',
            'image'  : item.get('thumbs',{}).get('url3','') if not bool(int(item.get('isdir'))) else '',
            'list'   : self.getChildFile(short_url, item['path'], '0') if item.get('isdir') else [],
        } for item in req.get('list', [])]
        return(all_file)

    # Check Format File
    def checkFileType(self, name:str) -> str:
        name = name.lower()
        if any(ext in name for ext in ['.mp4', '.mov', '.m4v', '.mkv', '.asf', '.avi', '.wmv', '.m2ts', '.3g2']):
            typefile = 'video'
        elif any(ext in name for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            typefile = 'image'
        elif any(ext in name for ext in ['.pdf', '.docx', '.zip', '.rar', '.7z']):
            typefile = 'file'
        else:
            typefile = 'other'
        return(typefile)

class TeraboxLink():

    #--> Initialization (requests, headers, payload, and result)
    def __init__(self, shareid:str, uk:str, sign:str, timestamp:str, fs_id:str) -> None:

        self.r = requests.Session()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6',
            'Connection': 'keep-alive',
            'Cookie': 'csrfToken=x0h2WkCSJZZ_ncegDtpABKzt; browserid=Bx3OwxDFKx7eOi8np2AQo2HhlYs5Ww9S8GDf6Bg0q8MTw7cl_3hv7LEcgzk=; lang=en; TSID=pdZVCjBvomsN0LnvT407VJiaJZlfHlVy; __bid_n=187fc5b9ec480cfe574207; ndus=Y-ZNVKxteHuixZLS-xPAQRmqh5zukWbTHVjen34w; __stripe_mid=895ddb1a-fe7d-43fa-a124-406268fe0d0c36e2ae; ndut_fmt=FF870BBFA15F9038B3A39F5DDDF1188864768A8E63DC6AEC54785FCD371BB182',
            'DNT': '1',
            'Host': 'www.4funbox.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        self.result = {'status': 'failed', 'download_link': {}}
        
        self.params = {
            'app_id': '250528',
            'channel': 'dubox',
            'product': 'share',
            'clienttype': '0',
            'shareid': str(shareid),
            'uk': str(uk),
            'sign': str(sign),
            'timestamp': str(timestamp),
            'fs_id': str(fs_id)
        }
        logger.info(f"Initialized TeraboxLink with params: {self.params}")

    def generate(self) -> None:
        try:
            # First get the page to extract jsToken and logid
            url = 'https://www.4funbox.com/share/download'
            logger.info(f"Generating download link from: {url}")
            
            response = self.r.get(url, params=self.params, headers=self.headers, timeout=10)
            response_text = response.text
            
            # Extract jsToken and logid
            js_token = find_between(response_text, 'fn%28%22', '%22%29')
            logid = find_between(response_text, 'dp-logid=', '&')
            
            if not js_token or not logid:
                logger.error("Failed to extract jsToken or logid")
                self.result['status'] = 'failed'
                return
                
            # Add jsToken and logid to params
            download_params = self.params.copy()
            download_params.update({
                'jsToken': js_token,
                'dplogid': logid,
                'web': '1'
            })
            
            # Make the download request
            download_response = self.r.get(url, params=download_params, headers=self.headers, timeout=10)
            
            try:
                data = download_response.json()
                if data.get('errno') == 0:
                    download_url = data.get('dlink')
                    self.result['download_link'] = download_url
                    self.result['status'] = 'success'
                    logger.info(f"Successfully generated download link: {download_url[:100]}...")
                else:
                    error_msg = f"API Error: {data.get('errno')} - {data.get('errmsg', 'Unknown error')}"
                    logger.error(error_msg)
                    self.result['status'] = 'failed'
                    self.result['error'] = error_msg
            except ValueError as e:
                logger.error(f"Invalid JSON response: {str(e)}")
                self.result['status'] = 'failed'
                self.result['error'] = 'Invalid response from server'
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out"
            logger.error(error_msg)
            self.result['status'] = 'failed'
            self.result['error'] = error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            self.result['status'] = 'failed'
            self.result['error'] = error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            self.result['status'] = 'failed'
            self.result['error'] = error_msg

class Test():

    def __init__(self) -> None:
        pass

    def file(self) -> None:

        # url = 'https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg' #-> Test File Besar
        url = 'https://dm.terabox.com/indonesian/sharing/link?surl=KKG3LQ7jaT733og97CBcGg' #-> Test File All Format (Video, Gambar)
        # url = 'https://www.terabox.com/wap/share/filelist?surl=cmi8P-_NCAHAzxj7MtzZAw' #-> Test File (Zip)

        TF = TeraboxFile()
        TF.search(url)

        print(TF.result)
        open('backend/json/test_file.json', 'w', encoding='utf-8').write(str(TF.result))

    def link(self) -> None:

        #--> Example parameters
        fs_id     = '854989261567890'
        uk        = '4400994387999'
        shareid   = '21362218376'

        #--> Fatal
        timestamp = str(int(time.time()))
        data = f"{shareid}{uk}{timestamp}"
        sign = hashlib.md5(data.encode()).hexdigest()

        TL = TeraboxLink(shareid, uk, sign, timestamp, fs_id)
        TL.generate()

        print(TL.result)
        open('backend/json/test_link.json', 'w', encoding='utf-8').write(str(TL.result))

if __name__ == '__main__':

    T = Test()
    # T.file()
    # T.link()

# [ Reference ]
# https://terabox.hnn.workers.dev/
# https://github.com/NamasteIndia/Terabox-Downloader-2023