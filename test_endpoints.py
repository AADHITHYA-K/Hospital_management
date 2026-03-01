import asyncio
from fastapi.testclient import TestClient
# ``httpx`` is used internally by the test client; make sure it is
# installed so that developers running the tests locally don't hit an
# import error.
import httpx
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.dependencies import get_current_user
import httpx

client = TestClient(app)

def override_get_current_user():
    user = User(id=1, email="test@test.com", role="Doctor")
    return user

app.dependency_overrides[get_current_user] = override_get_current_user

# Setup DB - start with a clean schema so that stale columns don't
# cause errors during repeated test runs.  ``create_all`` alone won't
# modify existing tables, so we drop everything first in our lightweight
# test harness.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def main():
    print("Testing /requests/")
    try:
        response = client.get("/requests/")
        print("Status Code:", response.status_code)
        if response.status_code == 500:
            print("Content:", response.text)
    except Exception as e:
        print("Exception on /requests/:", e)

    print("\nTesting /tasks/my-tasks")
    try:
        response = client.get("/tasks/my-tasks")
        print("Status Code:", response.status_code)
        if response.status_code == 500:
            print("Content:", response.text)
    except Exception as e:
        print("Exception on /tasks/my-tasks:", e)

if __name__ == "__main__":
    main()
