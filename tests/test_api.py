from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_reject_unsupported_extension(tmp_path):
    bad_file = tmp_path / 'bad.exe'
    bad_file.write_bytes(b'not a valid document')

    response = client.post('/documents/upload', files={'file': (bad_file.name, bad_file.read_bytes(), 'application/octet-stream')})
    assert response.status_code == 400
