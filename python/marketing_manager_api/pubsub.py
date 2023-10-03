import requests
from requests import Response


class ExceptionPubSubAdapter(BaseException):
    pass


class PubSubClient:

    def __init__(self, url: str, client_id: str):
        self.client_id = client_id
        self.__url = url

    def publish(self, topic: str, data: bytes) -> None:
        """Publishes to a topic.

        Args:
            topic: PubSub topic.
            data: Message data.

        Raises:
            ExceptionPubSubAdapter: When publishing error occurs.
        """
        resp: Response = requests.post(f"{self.__url}/publish/{topic}", data=data, headers={"Content-Type": "application/json"})
        if resp.status_code != 200:
            raise ExceptionPubSubAdapter(f"status code {str(resp.status_code)} {resp.text}")

    def consume(self, topic: str, from_start: bool = False) -> bytes | None:
        """Consumes a record from the topic.

        Args:
            topic: PubSub topic.
            from_start: Consume from zero offset.

        Raises:
            ExceptionPubSubAdapter: When publishing error occurs.
        """
        q = ""
        if from_start:
            q = "?from_start=true"

        resp: Response = requests.get(f"{self.__url}/consume/{topic}/{self.client_id}{q}", headers={"Content-Type": "application/json"})
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 204 or resp.status_code == 404:
            return None
        raise ExceptionPubSubAdapter(f"status code {str(resp.status_code)} {resp.text}")
