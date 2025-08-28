import React, { useState } from 'react';
import './Documents.css';

function Documents() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = (e) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    fetch('/api/documents/upload', {
      method: 'POST',
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message || data.error);
      })
      .catch((error) => {
        console.error('Error uploading file:', error);
        alert('Error uploading file.');
      });
  };

  return (
    <div className="documents">
      <h2>Upload Documents</h2>
      <form onSubmit={handleUpload}>
        <div className="form-group">
          <label htmlFor="file-upload">Select a file (.txt, .md, .pdf)</label>
          <input
            type="file"
            id="file-upload"
            accept=".txt,.md,.pdf"
            onChange={handleFileChange}
          />
        </div>
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default Documents;
