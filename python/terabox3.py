import re, requests, hashlib, time
from urllib.parse import quote

headers : dict[str, str] = {'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'}

class TeraboxFile():

    #--> Initialization (requests, headers, and result)
    def __init__(self) -> None:

        self.r : object = requests.Session()
        self.headers : dict[str,str] = headers
        self.result : dict[str,any] = {'status':'failed', 'sign':'', 'timestamp':'', 'shareid':'', 'uk':'', 'list':[]}

    #--> Main control (get short_url, init authorization, and get root file)
    def search(self, url:str) -> None:

        req : str = self.r.get(url, allow_redirects=True)
        self.short_url : str = re.search(r'surl=([^ &]+)',str(req.url)).group(1)
        self.getMainFile()
        self.generateSign()

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
        except:
            self.result['status'] = 'failed'

    #--> Get payload (root / top layer / overall data) and init packing file information
    def getMainFile(self) -> None:

        url: str = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{self.short_url}&root=1'
        req : object = self.r.get(url, headers=self.headers).json()
        all_file = self.packData(req, self.short_url)
        if len(all_file):
            self.result['shareid']   = req['shareid']
            self.result['uk']        = req['uk']
            self.result['list']      = all_file

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

        self.r : object = requests.Session()
        self.headers : dict[str,str] = headers
        self.result : dict[str,dict] = {'status':'failed', 'download_link':{}}

        #--> Parameters for direct API call
        self.params : dict[str,any] = {
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

    #--> Generate download link
    def generate(self) -> None:

        try:
            # Direct API call to TeraBox
            url = 'https://www.terabox.com/share/download'
            response = self.r.get(url, params=self.params, headers=self.headers)
            data = response.json()
            
            if data.get('errno') == 0:
                # Get direct download link
                download_url = data.get('dlink')
                self.result['download_link'] = download_url
                self.result['status'] = 'success'
        except Exception as e:
            self.result['status'] = 'failed'
            self.result['message'] = str(e)

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