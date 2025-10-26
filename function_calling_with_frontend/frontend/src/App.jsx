import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [user_query, setUser_query] = useState('');
  const [data, setData] = useState('')
  const submitHandler = async (e) => {
    e.preventDefault();
    setUser_query('')
    const url = "http://localhost:8000/api/v1/ai/chat"
    const res = await fetch(url, {
      method : "POST",
      headers : {"Content-Type" : "application/json"},
      body : JSON.stringify({"user_query" : user_query})
    })
    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });

      // Append chunk to existing text
      setData(prev => prev + text);
  }
  }
  return (
    <>
      <div>Hare Krsna</div>
      <form onSubmit={submitHandler}>
        <input
          type='text'
          onChange={(e) => setUser_query(e.target.value)}
          value={user_query}
        />
        <button
          type='submit'
        >Send</button>
      </form>
      {data && <div>{data}</div>}
    </>
  )
}

export default App
