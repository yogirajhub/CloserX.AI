// document.addEventListener("DOMContentLoaded", fetchQuestions);

// async function fetchQuestions() {
//     const response = await fetch('/api/unanswered');
//     const questions = await response.json();
//     const container = document.getElementById('questions-list');
    
//     container.innerHTML = '';
    
//     if (questions.length === 0) {
//         container.innerHTML = '<p>No unanswered questions right now!</p>';
//         return;
//     }

//     questions.forEach(q => {
//         const div = document.createElement('div');
//         div.className = 'question-item';
//         div.innerHTML = `
//             <p><strong>Q:</strong> ${q.question}</p>
//             <textarea id="ans-${q.id}" placeholder="Type answer to teach CloserX..."></textarea>
//             <button onclick="submitAnswer(${q.id})">Save Answer</button>
//         `;
//         container.appendChild(div);
//     });
// }

// async function submitAnswer(id) {
//     const answerInput = document.getElementById(`ans-${id}`).value;
//     if (!answerInput) return alert("Please enter an answer");

//     await fetch('/api/answer', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ id: id, answer: answerInput })
//     });
    
//     fetchQuestions(); // Refresh list to show question was removed
// }

// // Function to make outbound call from dashboard
// async function initiateCall() {
//     const phoneNumber = document.getElementById('target-phone').value;
//     const statusText = document.getElementById('call-status');

//     if (!phoneNumber) {
//         alert("Please enter a phone number first!");
//         return;
//     }

//     statusText.innerText = `Dialing ${phoneNumber}... please wait.`;

//     try {
//         const response = await fetch('/api/make_call', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ phone_number: phoneNumber })
//         });
        
//         const data = await response.json();
        
//         if (data.status === "success") {
//             statusText.innerText = "Call Connected! The AI is talking now.";
//             statusText.style.color = "green";
//         } else {
//             statusText.innerText = "Error: " + data.message;
//             statusText.style.color = "red";
//         }
//     } catch (error) {
//         statusText.innerText = "Failed to connect to server.";
//         statusText.style.color = "red";
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
        
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
        
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
        
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
        
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
        
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
        
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Function to fetch and display call history
// async function fetchCallHistory() {
//     const listDiv = document.getElementById('call-history-list');
    
//     try {
//         const response = await fetch('/api/call_history');
//         const data = await response.json();
        
//         if (data.history.length === 0) {
//             listDiv.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No recent calls found.</p>';
//             return;
//         }
//         // HTML generate karna har call ke liye
//         listDiv.innerHTML = data.history.map(call => `
//             <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🕒 Time:</strong> ${call.time}
//                 </div>
//                 <div style="font-size: 0.85em; color: #7f8c8d; margin-bottom: 5px;">
//                     <strong>🆔 Call SID:</strong> ${call.call_sid || 'N/A'}
//                 </div>
//                 <div style="margin-bottom: 10px; color: #2c3e50;">
//                     <strong>📌 Summary:</strong> ${call.summary}
//                 </div>
//                 <details style="cursor: pointer;">
//                     <summary style="color: #2980b9; font-weight: bold; outline: none;">View Full Transcript</summary>
//                     <pre style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; font-size: 0.9em; white-space: pre-wrap; font-family: inherit;">${call.transcript}</pre>
//                 </details>
//             </div>
//         `).join('');
        
//     } catch (error) {
//         console.error("Failed to fetch call history:", error);
//         listDiv.innerHTML = '<p style="color: red;">Error loading call history.</p>';
//     }
// }

// // Page load hone par automatically history fetch kar lo
// document.addEventListener('DOMContentLoaded', () => {
//     fetchCallHistory();
// });

document.addEventListener("DOMContentLoaded", () => {
    fetchQuestions();
    fetchCallHistory();
});

// --- Upload Document ---
async function uploadDocument() {
    const fileInput = document.getElementById('doc-file');
    const statusText = document.getElementById('upload-status');
    if (fileInput.files.length === 0) return alert("Select a .txt file first!");
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    statusText.innerText = "⏳ Uploading and training AI...";
    statusText.style.color = "blue";
    
    try {
        const res = await fetch('/api/upload_doc', { method: 'POST', body: formData });
        const result = await res.json();
        statusText.innerText = "✅ " + result.message;
        statusText.style.color = "green";
    } catch (err) {
        statusText.innerText = "❌ Upload failed!";
        statusText.style.color = "red";
    }
}

// --- Outbound Call ---
async function initiateCall() {
    const phone = document.getElementById('target-phone').value;
    const statusText = document.getElementById('call-status');
    if (!phone) return alert("Enter phone number!");
    
    statusText.innerText = `Dialing ${phone}...`;
    statusText.style.color = "blue";
    
    try {
        const res = await fetch('/api/make_call', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone })
        });
        const data = await res.json();
        if (data.status === "success") {
            statusText.innerText = "✅ Call Connected! ";
            statusText.style.color = "green";
        } else {
            statusText.innerText = "❌ Error: " + data.message;
            statusText.style.color = "red";
        }
    } catch (err) {
        statusText.innerText = "❌ Connection Failed";
        statusText.style.color = "red";
    }
}

// --- Unanswered Logic ---
async function fetchQuestions() {
    const res = await fetch('/api/unanswered');
    const questions = await res.json();
    const container = document.getElementById('questions-list');
    
    if (questions.length === 0) {
        container.innerHTML = '<p style="color: green;">✅ All good! No pending questions.</p>';
        return;
    }
    container.innerHTML = questions.map(q => `
        <div class="question-item">
            <p style="color: #8a6d3b; margin: 0 0 5px 0;"><strong>Q:</strong> ${q.question}</p>
            <textarea id="ans-${q.id}" placeholder="Type exact answer here..." rows="2"></textarea>
            <button onclick="submitAnswer(${q.id})" style="background: #e67e22; margin-top: 5px;">Save & Update AI</button>
        </div>
    `).join('');
}

async function submitAnswer(id) {
    const answer = document.getElementById(`ans-${id}`).value;
    if (!answer) return alert("Please enter an answer");
    await fetch('/api/answer', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id, answer: answer })
    });
    alert("✅ AI memory updated!");
    fetchQuestions();
}

// --- Call History ---
async function fetchCallHistory() {
    const listDiv = document.getElementById('call-history-list');
    const res = await fetch('/api/call_history');
    const data = await res.json();
    
    if (data.history.length === 0) {
        listDiv.innerHTML = '<p>No recent calls found.</p>';
        return;
    }
    listDiv.innerHTML = data.history.map(c => `
        <div style="border-left: 4px solid #27ae60; background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 4px;">
            <div style="font-size: 0.85em; color: #7f8c8d;"><strong>🕒 Time:</strong> ${c.time} | <strong>🆔 SID:</strong> ${c.call_sid || 'N/A'}</div>
            <div style="margin: 10px 0; color: #2c3e50;"><strong>📌 Summary:</strong> ${c.summary}</div>
            <details><summary>View Transcript</summary><pre>${c.transcript}</pre></details>
        </div>
    `).join('');
}