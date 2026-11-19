import os
import io

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_document_upload_and_lifecycle(client):
    content = b"DocuMind Test Document Content. Testing text extraction and indexing."
    file = io.BytesIO(content)

    # 1. Upload
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_doc.txt", file, "text/plain")}
    )
    assert response.status_code == 201
    data = response.json()
    assert "document" in data
    doc_id = data["document"]["id"]
    assert data["document"]["original_name"] == "test_doc.txt"
    assert data["is_duplicate"] is False

    # 2. List documents
    res_list = client.get("/api/v1/documents")
    assert res_list.status_code == 200
    docs = res_list.json()
    assert any(d["id"] == doc_id for d in docs)

    # 3. Duplicate detection
    file2 = io.BytesIO(content)
    # If the document is still pending or processing, test duplicate behavior once indexed
    # 4. Get document detail
    res_detail = client.get(f"/api/v1/documents/{doc_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == doc_id

    # 5. Delete document
    res_del = client.get(f"/api/v1/documents/{doc_id}/status")
    assert res_del.status_code == 200

    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200

    # 6. Verify 404 after deletion
    res_not_found = client.get(f"/api/v1/documents/{doc_id}")
    assert res_not_found.status_code == 404

