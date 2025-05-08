import re, requests, hashlib, time
import logging
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://www.terabox.com',
    'referer': 'https://www.terabox.com/'
}

class TeraboxFile():

    #--> Initialization (requests, headers, and result)
    def __init__(self) -> None:

        self.r : object = requests.Session()
        self.headers : dict[str,str] = headers
        self.result : dict[str,any] = {'status':'failed', 'sign':'', 'timestamp':'', 'shareid':'', 'uk':'', 'list':[]}

    #--> Main control (get short_url, init authorization, and get root file)
    def search(self, url:str) -> None:

        try:
            logger.info(f"Searching URL: {url}")
            req : str = self.r.get(url, allow_redirects=True)
            self.short_url : str = re.search(r'surl=([^ &]+)',str(req.url)).group(1)
            logger.info(f"Extracted short URL: {self.short_url}")
            self.getMainFile()
            self.generateSign()
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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.terabox.com',
            'referer': 'https://www.terabox.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
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

    def get_verify_token(self) -> str:
        try:
            # Get verification token from TeraBox
            verify_url = 'https://www.terabox.com/api/gettemplatevariable'
            verify_params = {
                'app_id': '250528',
                'channel': 'dubox',
                'clienttype': '0',
                'web': '1'
            }
            
            logger.info(f"Requesting verification token from: {verify_url}")
            response = self.r.get(verify_url, params=verify_params, headers=self.headers, timeout=10)
            logger.info(f"Verification token response status: {response.status_code}")
            logger.info(f"Verification token response content: {response.text[:200]}...")
            
            if response.status_code != 200:
                logger.error(f"Failed to get verification token. Status code: {response.status_code}")
                return ''
                
            try:
                data = response.json()
                if data.get('errno') == 0:
                    token = data.get('token', '')
                    logger.info(f"Successfully got verification token: {token[:10]}...")
                    return token
                else:
                    logger.error(f"API error getting verification token: {data.get('errno')} - {data.get('errmsg', 'Unknown error')}")
                    return ''
            except ValueError as e:
                logger.error(f"Invalid JSON response from verification token endpoint: {str(e)}")
                return ''
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while getting verification token")
            return ''
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed while getting verification token: {str(e)}")
            return ''
        except Exception as e:
            logger.error(f"Unexpected error getting verification token: {str(e)}")
            return ''

    #--> Generate download link
    def generate(self) -> None:

        try:
            # First get verification token
            verify_token = self.get_verify_token()
            if not verify_token:
                # Try direct download without verification
                logger.info("Attempting direct download without verification")
                self.params.pop('verify_token', None)
            else:
                self.params['verify_token'] = verify_token
            
            url = 'https://www.terabox.com/share/download'
            logger.info(f"Generating download link from: {url}")
            
            # First request to get verification
            response = self.r.get(url, params=self.params, headers=self.headers, timeout=10)
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response content: {response.text[:200]}...")
            
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Invalid JSON response: {str(e)}")
                self.result['status'] = 'failed'
                self.result['error'] = 'Invalid response from server'
                return
            
            if data.get('errno') == 0:
                download_url = data.get('dlink')
                self.result['download_link'] = download_url
                self.result['status'] = 'success'
                logger.info(f"Successfully generated download link: {download_url[:100]}...")
            elif data.get('errno') == 400310:  # Need verification
                # Get verification code from response
                verify_code = data.get('verify_code', '')
                if verify_code:
                    # Add verification code to params
                    self.params['verify_code'] = verify_code
                    
                    # Second request with verification code
                    response = self.r.get(url, params=self.params, headers=self.headers, timeout=10)
                    try:
                        data = response.json()
                    except ValueError as e:
                        logger.error(f"Invalid JSON response after verification: {str(e)}")
                        self.result['status'] = 'failed'
                        self.result['error'] = 'Invalid response after verification'
                        return
                    
                    if data.get('errno') == 0:
                        download_url = data.get('dlink')
                        self.result['download_link'] = download_url
                        self.result['status'] = 'success'
                        logger.info(f"Successfully generated download link after verification: {download_url[:100]}...")
                    else:
                        error_msg = f"API Error after verification: {data.get('errno')} - {data.get('errmsg', 'Unknown error')}"
                        logger.error(error_msg)
                        self.result['status'] = 'failed'
                        self.result['error'] = error_msg
                else:
                    error_msg = "No verification code received"
                    logger.error(error_msg)
                    self.result['status'] = 'failed'
                    self.result['error'] = error_msg
            else:
                error_msg = f"API Error: {data.get('errno')} - {data.get('errmsg', 'Unknown error')}"
                logger.error(error_msg)
                self.result['status'] = 'failed'
                self.result['error'] = error_msg
                
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