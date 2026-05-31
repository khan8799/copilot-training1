import pytest
from urllib.parse import quote


def test_get_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity(client):
    email = "test.student@mergington.edu"
    activity_name = quote("Chess Club")
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    email = "duplicate.student@mergington.edu"
    activity_name = quote("Chess Club")
    client.post(f"/activities/{activity_name}/signup?email={quote(email)}")
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant(client):
    email = "remove.student@mergington.edu"
    activity_name = quote("Chess Club")
    client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    response = client.delete(
        f"/activities/{activity_name}/participants?email={quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants?email=missing.student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


@pytest.mark.parametrize("endpoint", [
    "/activities/Unknown%20Club/signup?email=test@mergington.edu",
    "/activities/Unknown%20Club/participants?email=test@mergington.edu",
])
def test_unknown_activity_returns_404(client, endpoint):
    response = client.request("POST" if endpoint.endswith("/signup?email=test@mergington.edu") else "DELETE", endpoint)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
