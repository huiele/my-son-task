# -*- coding:utf-8 -*-

import hashlib
import io
import os.path
import uuid
import json

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, RequestHandler, asynchronous

from search_app.model import ImageDatabase
from elasticsearch import Elasticsearch
from bson import ObjectId, errors

# 数据库相关设置
MONGODB_DB_URL = os.environ.get("MONGODB_DB_URL") if os.environ.get("MONGODB_DB_URL") else "mongodb://localhost:27017/"
MONGODB_DB_NAME = os.environ.get("APP_NAME") if os.environ.get("APP_NAME") else "images"
MONGODB_DB_COLLECTION = os.environ.get('MONGODB_DB_COLLECTION') if os.environ.get("MONGODB_DB_COLLECTION") else "data"
SERVER_HOST = "http://localhost:9090"

define("port", default=9090, help="run on the given port", type=int)



class SearchApplication(Application):
    def __init__(self):
        handlers = [
            (r"/", DashboardHandler),
            (r"/search", SearchHandler),
            # (r"/images/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__)) + "/images/"})
            (r"/images/(.*)", ImageHandler),
            (r"/uploads", FileUploaderHandler),
        ]

        setting = dict(
            website_title=u"相似图片搜索",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "assets"),
            cookie_secret="todo_add_secret",
            debug=True,
            autoreload=True,
            xsrf_cookies=False,
            default_handler_class=MyErrorHandler,
            env=os.environ.get("ENV", "dev"),
        )
        super(SearchApplication, self).__init__(handlers, **setting)

        # 初始化数据库
        self.conn = ImageDatabase(url=MONGODB_DB_URL, database=MONGODB_DB_NAME, collection=MONGODB_DB_COLLECTION,
                                  index="images")


class DashboardHandler(RequestHandler):
    def data_received(self, chunk):
        """Defined to avoid abstract-method lint issue."""
        pass

    def get(self):
        self.render("dashboard.html")


class FileUploaderHandler(RequestHandler):
    _id = None

    def data_received(self, chunk):
        """Defined to avoid abstract-method lint issue."""
        pass

    def get(self):
        self.render("upload.html")

    def post(self):
        db = self.application.conn
        file = self.request.files["file"][0]
        md5 = hashlib.md5(file['body']).hexdigest()
        image = db.get_image({"md5": md5})
        if image:
            self._id = image.get("_id")
        else:
            # filename = str(uuid.uuid4()) + os.path.splitext(file['filename'])[1].lower()
            filename = file['filename']
            dd = {
                "filename": filename,
                "md5": md5,
                "content_type": file.get('content_type'),
            }
            self._id = db.set_image(io.BytesIO(file.get('body')), dd)
            dd = {
                '_id': str(self._id),
                'metadata': {"flag": str(self._id)},
            }
            db.set_index(file.get('body'), dd)

        self.write(str(self._id))
        self.finish()


class SearchHandler(RequestHandler):
    _id = None

    def data_received(self, chunk):
        """Defined to avoid abstract-method lint issue."""
        pass

    def get(self):
        self.redirect(r"/")

    def post(self):
        """
        image_data:
        {
            filename: str;
            raw_data: base64;
            content_type: str("image/png");
            md5: str;
        }
        """
        db = self.application.conn
        file = self.request.files["image_file"][0]
        md5 = hashlib.md5(file['body']).hexdigest()
        image = db.get_image({"md5": md5})
        if not image:
            # filename = str(uuid.uuid4()) + os.path.splitext(file['filename'])[1].lower()
            filename = file['filename']
            dd = {
                "filename": filename,
                "md5": md5,
                "content_type": file.get('content_type'),
            }
            self._id = db.set_image(io.BytesIO(file.get('body')), dd)
            db.set_index(file.get('body'), {"_id": str(self._id), "metadata": {"flag": str(self._id)}})
        else:
            self._id = image.get("_id")
        image = db.get_image({"_id": self._id})
        image_data = {
            'filename': image.get('filename'),
            'content_type': image.get("content_type"),
        }
        results = db.get_index(file['body'])
        num = 0
        images_list = []
        for result in results:
            result_name = db.get_image({"_id": ObjectId(result.get("path"))})
            if not result_name:
                continue
            else:
                if float(result['dist']) < 0.150:
                    num += 1
                images_list.append({
                    '_id': result['path'],
                    'dist': result['dist'],
                    # 'filename': db.get_image({"_id": ObjectId(result['path'])}).get('filename'),
                    'filename': result_name.get('filename'),
                })
        image_data.update({"num": len(images_list),
                           "num_1": num,
                           "num_2": len(images_list) - num})
        self.render("results.html", image=str(self._id), image_data=image_data, images_list=images_list)


class ImageHandler(RequestHandler):
    @asynchronous
    def get(self, _id):
        """retrieve an image from MongoDB GridFS"""
        db = self.application.conn
        image = None
        try:
            image = db.get_image({"_id": ObjectId(_id)})
        except errors.InvalidId:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"error": "invalidId for image file."}))
        if image:
            im_stream = db.get_data({"file_id": ObjectId(image.get("file_id"))})
            self.set_header("Content-Type", im_stream.content_type)
            self.write(im_stream.read())
        self.finish()

    def data_received(self, chunk):
        """Defined to avoid abstract-method lint issue."""
        pass


class MyErrorHandler(RequestHandler):
    def prepare(self):
        self.set_status(404)
        self.write("Error! 404 Not Found!")

    def get(self):
        pass

    def post(self):
        pass

    def data_received(self, chunk):
        pass


def run():
    options.parse_command_line()
    http_server = HTTPServer(SearchApplication())
    http_server.listen(options.port)
    IOLoop.instance().start()


if __name__ == "__main__":
    # execute only if run as a script
    run()
