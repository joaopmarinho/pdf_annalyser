from __future__ import annotations


async def test_qa_and_question_history_with_stub(client):
    files = {
        'file': (
            'knowledge.txt',
            b'FastAPI eh um framework web para APIs. PostgreSQL com pgvector permite busca vetorial.',
            'text/plain',
        )
    }
    created = await client.post('/v1/documents', files=files)
    assert created.status_code == 200
    doc_id = created.json()['doc_id']

    qa = await client.post('/v1/qa', json={'doc_id': doc_id, 'question': 'O que eh FastAPI?', 'top_k': 3})
    assert qa.status_code == 200
    payload = qa.json()
    assert 'Best-effort answer' in payload['answer']
    assert len(payload['sources']) >= 1

    history = await client.get(f'/v1/questions?doc_id={doc_id}')
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 1
    assert 'FastAPI' in items[0]['question']
