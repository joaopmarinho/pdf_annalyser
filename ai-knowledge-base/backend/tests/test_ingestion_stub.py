from __future__ import annotations


async def test_upload_and_list_documents(client):
    files = {'file': ('sample.txt', b'Python FastAPI e vetores para busca semantica.', 'text/plain')}
    data = {'title': 'Documento de teste'}
    created = await client.post('/v1/documents', files=files, data=data)
    assert created.status_code == 200
    payload = created.json()
    assert payload['status'] == 'indexed'
    assert payload['chunks'] >= 1

    listed = await client.get('/v1/documents')
    assert listed.status_code == 200
    docs = listed.json()
    assert len(docs) == 1
    assert docs[0]['title'] == 'Documento de teste'

    details = await client.get(f"/v1/documents/{payload['doc_id']}")
    assert details.status_code == 200
    assert details.json()['chunks'] >= 1
