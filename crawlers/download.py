import json
import os
import re

import aiofiles
import httpx
import yaml
from fastapi import APIRouter

from crawlers.utils.logger import logger

from crawlers.douyin.web.web_crawler import DouyinWebCrawler
from .hybrid.hybrid_crawler import HybridCrawler  # 导入混合数据爬虫

router = APIRouter()
HybridCrawler = HybridCrawler()


async def fetch_data(url: str, headers: dict = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36 '
    } if headers is None else headers.get('headers')
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # 确保响应是成功的
        return response


# 下载视频专用
async def fetch_data_stream(url: str, headers: dict = None, file_path: str = None):
    logger.info(f"开始下载文件: {file_path}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36 '
    } if headers is None else headers.get('headers')
    try:
        async with httpx.AsyncClient() as client:
            # 启用流式请求
            async with client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()
                # 流式保存文件
                async with aiofiles.open(file_path, 'wb') as out_file:
                    async for chunk in response.aiter_bytes():
                        await out_file.write(chunk)
                logger.info(f"文件下载完成: {file_path}")
                return True
    except Exception as e:
        logger.error(f"文件下载失败: {file_path}, 错误: {e}")
        return False


async def download_file(base_path, product, url: str):
    """
    url: https://www.douyin.com/video/7372484719365098803
    """
    logger.info(f"开始下载: {url}")
    # DouyinWebCrawler.GlobalCookies = config_service.get('douyin.cookies')
    # 解析
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)[0]
    # 开始解析数据/Start parsing data
    try:
        data = await HybridCrawler.hybrid_parsing_single_video(url, minimal=True)
    except Exception as e:
        logger.error(f"解析失败: {e}")
        return {
            "code": -100,
            "msg": f"{e}",
        }
    prefix = True
    # 开始下载文件/Start downloading files
    try:
        data_type = data.get('type')
        platform = data.get('platform')
        aweme_id = data.get('aweme_id')
        download_path = os.path.join(base_path, f"{product}")

        # 确保目录存在/Ensure the directory exists
        os.makedirs(download_path, exist_ok=True)

        with_watermark = False
        # 下载视频文件/Download video file
        video_file_name = f"{aweme_id}.mp4"
        json_file_name = f"{aweme_id}.json"
        url = data.get('video_data').get('nwm_video_url_HQ') if not with_watermark else data.get('video_data').get(
            'wm_video_url_HQ')
        video_file_path = os.path.join(download_path, video_file_name)
        json_file_path = os.path.join(download_path, json_file_name)

        # 判断文件是否存在，存在就直接返回
        if os.path.exists(video_file_path):
            logger.info(f"文件已存在: {video_file_path}")
            return {
                "code": 200,
                "msg": "",
                "video_file_path": video_file_path,
                "json_file_path": json_file_path,
                "aweme_id": aweme_id,
            }

        # 获取视频文件
        __headers = await HybridCrawler.DouyinWebCrawler.get_douyin_headers()
        success = await fetch_data_stream(url, headers=__headers, file_path=video_file_path)
        if not success:
            logger.error(f"下载失败: {url}")
            return {
                "code": -100,
                "msg": f"下载失败",
            }
        # 写入json
        open(json_file_path, 'w', encoding='utf8', newline='').write(json.dumps(data, ensure_ascii=False))
        logger.info(f"下载成功: {video_file_path}")
        # 返回文件内容
        return {
            "code": 200,
            "msg": "",
            "video_file_path": video_file_path,
            "json_file_path": json_file_path,
            "aweme_id": aweme_id,
        }

    # 异常处理/Exception handling
    except Exception as e:
        logger.error(f"下载异常: {e}")
        return {
            "code": -100,
            "msg": f"{e}",
        }

