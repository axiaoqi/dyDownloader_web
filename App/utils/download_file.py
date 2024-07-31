import os
import requests
from tqdm.auto import tqdm


def download_video(url, name):
    response = requests.get(url, stream=True)
    if not os.path.exists(name):
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
            with open(name, 'wb') as file:
                for chunk in response.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    file.write(chunk)
            progress_bar.close()
            return True
        else:
            return False
