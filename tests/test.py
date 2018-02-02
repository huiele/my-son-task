# -*- coding:utf-8 -*-

import os
import pytest
from bs4 import BeautifulSoup as BS
from search_app.app import SearchApplication
from requests_toolbelt.multipart.encoder import MultipartEncoder

BASE_URL = "http://localhost:9090"
image_id = None


@pytest.fixture
def app():
    return SearchApplication


@pytest.mark.gen_test
def test_get_index(http_client, base_url=BASE_URL):
    response = yield http_client.fetch(base_url)
    assert response.code == 200


@pytest.mark.gen_test
def test_upload_images(http_client, base_url=BASE_URL):
    """
        上传图片
    :param http_client:
    :param base_url:
    :return:
    """

    filename = "a.jpg"
    file = os.path.dirname(__file__) + "\\mock_data\\%s"
    multipart_data = MultipartEncoder(fields={
        'file': (filename, open(file % filename, 'rb'), 'image/jpeg')
    })
    headers = {'Content-Type': multipart_data.content_type}

    response = yield http_client.fetch(base_url + "/uploads", method="POST", headers=headers,
                                       body=multipart_data.to_string())

    # assert response.buffer.getvalue() == b'Upload error!'  # 返回上传图片的id值
    assert response.code == 200


@pytest.mark.gen_test
def test_search_image(http_client, base_url=BASE_URL):
    """
        搜索图片获取搜索结果
    :param http_client:
    :param base_url:
    :return:
    """
    filename = "b.jpg"
    file = os.path.dirname(__file__) + "\\mock_data\\%s"
    multipart_data = MultipartEncoder(fields={
        'image_file': (filename, open(file % filename, 'rb'), 'image/jpeg')
    })
    headers = {'Content-Type': multipart_data.content_type}

    response = yield http_client.fetch(base_url + "/search", method="POST", headers=headers,
                                       body=multipart_data.to_string())

    soup = BS(response.buffer.getvalue().decode(), "html.parser")

    assert response.code == 200
    assert len(soup.find_all("div", class_="am-gallery-desc")) == 2

    filename = "c.jpg"
    file = os.path.dirname(__file__) + "\\mock_data\\%s"
    multipart_data = MultipartEncoder(fields={
        'image_file': (filename, open(file % filename, 'rb'), 'image/jpeg')
    })
    headers = {'Content-Type': multipart_data.content_type}

    response = yield http_client.fetch(base_url + "/search", method="POST", headers=headers,
                                       body=multipart_data.to_string())
    soup = BS(response.buffer.getvalue().decode(), "html.parser")

    assert response.code == 200
    assert len(soup.find_all("div", class_="am-gallery-desc")) == 1


@pytest.mark.gen_test
def test_upload_page(http_client, base_url=BASE_URL):
    """
        访问上传页面
    :param http_client:
    :param base_url: /uploads(get)
    :return:
    """
    response = yield http_client.fetch(base_url + "/uploads")
    assert response.code == 200


@pytest.mark.gen_test
def test_get_image(http_client, base_url=BASE_URL):
    """
        获取图片
    :param http_client:
    :param base_url:
    :return:
    """
    response = yield http_client.fetch(base_url + "/images/3235dadfaga")
    assert response.headers['Content-Type'] == "application/json"

    multipart_data = MultipartEncoder(
        fields={
            'file': (
                "a.jpg",
                open(os.path.dirname(__file__) + "\\mock_data\\a.jpg", 'rb'),
                'image/jpeg')
        })
    headers = {'Content-Type': multipart_data.content_type}
    response = yield http_client.fetch(
        base_url + "/uploads", method="POST", headers=headers,
        body=multipart_data.to_string())

    url = base_url + "/images/%s" % str(response.buffer.getvalue().decode())
    response = yield http_client.fetch(url)

    assert response.code == 200
    assert response.headers['Content-Type'] == "image/jpeg"
