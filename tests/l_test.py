# -*- coding:utf-8 -*-

from locust import Locust, TaskSet, task


class SearchTaskSet(TaskSet):
    min_wait = 5000
    max_wait = 15000

    @task
    def task_get_dashboard(self):
        self.client.get("/")

    @task
    def task_get_upload(self):
        self.client.get("/uploads")


class MyLocust(Locust):
    task_set = SearchTaskSet
