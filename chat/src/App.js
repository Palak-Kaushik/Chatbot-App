import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/register', { username, password });
      alert('Registration successful');
    } catch (error) {
      alert('Registration failed');
      console.error(error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/login', { username, password });
      setToken(response.data.access_token);
      setIsAuthenticated(true);
    } catch (error) {
      alert('Login failed');
      console.error(error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const updatedChatHistory = [...chatHistory, { text: inputText, sender: 'user' }];
    setChatHistory(updatedChatHistory);
    setInputText('');

    try {
      const response = await axios.post('http://localhost:5000/chat', { message: inputText }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const responseData = response.data;

      const updatedChatHistoryWithResponse = [
        ...updatedChatHistory,
        { text: responseData.message, sender: 'bot' }
      ];
      setChatHistory(updatedChatHistoryWithResponse);
    } catch (error) {
      console.error(error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div>
        <h1>Login</h1>
        <form onSubmit={handleLogin}>
          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button type="submit">Login</button>
        </form>
        <h1>Register</h1>
        <form onSubmit={handleRegister}>
          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button type="submit">Register</button>
        </form>
      </div>
    );
  }

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
