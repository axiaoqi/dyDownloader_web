import os


# 删除缓存
for file in os.listdir():
    if file.endswith('.mp4'):
        os.remove(file)


# crontab -e
# 0 3 * * * python /path/to/cleanMP4.py  # 每天三点清理文件
