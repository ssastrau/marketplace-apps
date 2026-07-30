import time


class WeaviateService:
    """
    Container and REST/GraphQL API actions for Weaviate.
    """

    WEAVIATE_CONTAINER = "weaviate-weaviate-1"
    TRANSFORMERS_CONTAINER = "weaviate-text2vec-transformers-1"
    HTTP_PORT = 8080
    GRPC_PORT = 50051

    def __init__(self, remote_exec, session, base_url):
        self._run = remote_exec
        self._session = session
        self._base_url = base_url.rstrip("/")

    def container_status(self, name):
        out, _, _ = self._run(f"docker inspect -f '{{{{.State.Status}}}}' {name}")
        return out

    def ready_status(self, attempts=3, delay=5):
        for attempt in range(attempts):
            try:
                return self._session.get(
                    f"{self._base_url}/v1/.well-known/ready", timeout=30
                ).status_code
            except Exception:
                if attempt == attempts - 1:
                    raise
                time.sleep(delay)

    def meta(self, api_key=None):
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        return self._session.get(f"{self._base_url}/v1/meta", headers=headers, timeout=30)

    def create_collection(self, api_key, name):
        return self._session.post(
            f"{self._base_url}/v1/schema",
            headers=self._auth(api_key),
            json={
                "class": name,
                "vectorizer": "none",
                "properties": [{"name": "title", "dataType": ["text"]}],
            },
            timeout=60,
        )

    def add_object(self, api_key, collection, title, vector):
        return self._session.post(
            f"{self._base_url}/v1/objects",
            headers=self._auth(api_key),
            json={"class": collection, "properties": {"title": title}, "vector": vector},
            timeout=60,
        )

    def nearest_title(self, api_key, collection, vector):
        query = (
            f"{{ Get {{ {collection}"
            f"(nearVector: {{vector: {vector}}}, limit: 1) {{ title }} }} }}"
        )
        response = self._session.post(
            f"{self._base_url}/v1/graphql",
            headers=self._auth(api_key),
            json={"query": query},
            timeout=60,
        )
        results = response.json()["data"]["Get"][collection]
        return results[0]["title"] if results else None

    @staticmethod
    def _auth(api_key):
        return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
