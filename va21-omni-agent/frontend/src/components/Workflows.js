import React, { useState } from 'react';
import './Workflows.css';

function Workflows() {
  const [workflowDescription, setWorkflowDescription] = useState('');

  const handleCreateWorkflow = (e) => {
    e.preventDefault();
    if (!workflowDescription.trim()) {
      alert('Please describe the workflow you want to create.');
      return;
    }

    fetch('/api/workflows/plan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description: workflowDescription }),
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message || data.error);
        if (data.message) {
          setWorkflowDescription('');
        }
      })
      .catch((error) => {
        console.error('Error creating workflow:', error);
        alert('Error creating workflow.');
      });
  };

  return (
    <div className="workflows">
      <h2>Create a New Workflow</h2>
      <p>Describe the workflow you want to create in natural language.</p>
      <form onSubmit={handleCreateWorkflow}>
        <div className="form-group">
          <textarea
            value={workflowDescription}
            onChange={(e) => setWorkflowDescription(e.target.value)}
            placeholder="e.g., Every morning at 9 AM, check my email for any messages from my boss, summarize them, and save the summary to Google Drive."
            rows="5"
          />
        </div>
        <button type="submit">Create Workflow</button>
      </form>
    </div>
  );
}

export default Workflows;
