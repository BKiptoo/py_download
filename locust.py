from locust import HttpUser, task

class MyUser(HttpUser):
    @task
    def test_website(self):
        self.client.get("https://wwwlara.dpower.vip/")
