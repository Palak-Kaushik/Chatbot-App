import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; 

function App() {
  const [inputText, setInputText] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Add user input to chat history
    const updatedChatHistory = [
      ...chatHistory,
      { text: inputText, sender: 'user' }
    ];
    setChatHistory(updatedChatHistory);
    setInputText('');

    // Send user input to backend
    try {
      const response = await axios.post('http://localhost:5000/chat', { message: inputText });
      const responseData = response.data;
      
      // Add AI response to chat history
      const updatedChatHistoryWithResponse = [
        ...updatedChatHistory,
        { text: responseData.message, sender: 'bot' }
      ];
      setChatHistory(updatedChatHistoryWithResponse);
    } catch (error) {
      if (error.response) {
        
        console.log('Status:', error.response.status);
        console.log('Data:', error.response.data);
      } else if (error.request) {
        
        console.log('Request:', error.request);
      } else {
        
        console.error('Error:', error.message);
      }
    }
  };

  return (
    <div>
      <h1>AI Chatbot</h1>
      <div className="chat-container">
        {chatHistory.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.sender === 'user' ? (
              <div className="user-message">User: {message.text}</div>
            ) : (
              <div className="bot-message">Bot: {message.text}</div>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input type="text" value={inputText} onChange={(e) => setInputText(e.target.value)} />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;

