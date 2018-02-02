# -*- coding:utf-8 -*-

from image_match.elasticsearch_driver import SignatureES
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from gridfs import GridFS, errors
from bson import errors as ee


class ImageDatabase(object):
    __slots__ = ["con", "database", "fs", "ses", "collection"]

    def __init__(self, url="mongodb://localhost:27017/", database="images", collection="data", index="images"):
        self.con = MongoClient(url, connect=False)
        self.database = self.con[database]
        self.fs = GridFS(self.database)
        self.collection = collection
        self.ses = SignatureES(Elasticsearch(), index=index)

    @staticmethod
    def key_check(l, d):
        for key in list(d):
            if key not in l:
                del d[key]
        return d

    def get_images(self, _id):
        """
            使用单张图片搜索，获取多张图片结果
        :param _id:
        :return:
        """
        # if not isinstance(_id, ObjectId):
        #     _id = ObjectId(_id)
        # image = self.get_image(**{"_id": _id})
        pass

    def set_image(self, data, dd):
        """
            存储单张图片
        :param data:
        :param dd:
        :return:
        """
        kwargs = self.key_check(("filename", "content_type", "md5"), dd)
        kwargs.update({"file_id": self.set_data(data, {"filename": dd['filename'], "content_type": dd['content_type']})})
        _id = self.database[self.collection].insert(dd)
        return _id

    def get_image(self, dd):
        """
            获取单张图片
        :param dd:  图片的属性（md5， objectid）
        :return: 图片数据
        """
        dd = self.key_check(("md5", "_id", "filename"), dd)  # 限制dict的keys
        image = self.database[self.collection].find_one(dd)
        return image

    def set_index(self, data, dd):
        """
            插入索引
        :param data:
        :param dd:
        :return:
        """
        dd = self.key_check(("_id", "metadata"), dd)
        # noinspection PyBroadException
        try:
            self.ses.add_image(path=dd.get('_id'), img=data, bytestream=True,
                               metadata=dd.get('metadata'))
        except Exception:
            return False
        return True

    def get_index(self, data):
        """
            获取搜索结果
        :param data:
        :return:
        """
        results = self.ses.search_image(data, bytestream=True)
        return results

    def get_data(self, dd):
        """
            获取文件系统中的数据
        :param dd:
        :return:
        """
        dd = self.key_check(["file_id"], dd)
        try:
            data = self.fs.get(dd.get('file_id'))
        except errors.NoFile:
            return None
        return data

    def set_data(self, data, dd):
        """
            将文件存储到系统中
        :param dd:
        :param data:
        :return:
        """
        dd = self.key_check(("content_type", "filename"), dd)
        file_id = self.fs.put(data, **dd)
        return file_id
