import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Upload, Send, FileText, BookOpen, Loader2, Moon, Sun, Trash2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('study_theme') === 'dark';
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isQuerying]);

  useEffect(() => {
    localStorage.setItem('study_theme', isDarkMode ? 'dark' : 'light');
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const fetchInitialData = async () => {
    try {
      const [filesRes, historyRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/files`),
        axios.get(`${API_BASE_URL}/history`)
      ]);
      setUploadedFiles(filesRes.data.files);
      setMessages(historyRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData);
      const filesRes = await axios.get(`${API_BASE_URL}/files`);
      setUploadedFiles(filesRes.data.files);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Check backend connection.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isQuerying) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsQuerying(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, { question: userMsg });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      }]);
    } catch (error) {
      console.error('Query failed:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Error communicating with the brain. Ensure Ollama is running.' 
      }]);
    } finally {
      setIsQuerying(false);
    }
  };

  const clearHistory = async () => {
    if (window.confirm('Clear all study conversations?')) {
      try {
        await axios.delete(`${API_BASE_URL}/history`);
        setMessages([]);
      } catch (error) {
        console.error('Failed to clear history:', error);
      }
    }
  };

  return (
    <div className={`flex h-screen w-full transition-colors duration-200 ${isDarkMode ? 'bg-slate-900 text-slate-100' : 'bg-white text-slate-900'}`}>
      {/* Sidebar */}
      <aside className={`w-80 flex-shrink-0 border-r flex flex-col ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50/50 border-slate-200'}`}>
        <div className={`p-6 flex items-center justify-between border-b ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center gap-3">
            <BookOpen className="text-blue-500" size={24} />
            <h1 className="text-xl font-bold tracking-tight">BookSelfStudy</h1>
          </div>
          <button 
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-slate-700 text-yellow-400' : 'hover:bg-slate-100 text-slate-600'}`}
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
        
        <div className="p-6 space-y-8 flex-1 overflow-y-auto">
          {/* Upload Section */}
          <div className="space-y-4">
            <input type="file" ref={fileInputRef} onChange={handleUpload} className="hidden" accept=".pdf,.md" />
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className={`w-full py-4 px-4 border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-2 transition-all group ${
                isDarkMode 
                ? 'border-slate-600 text-slate-400 hover:border-blue-500 hover:bg-blue-500/10' 
                : 'border-slate-300 text-slate-500 hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              {isUploading ? <Loader2 className="animate-spin text-blue-500" /> : <Upload className="group-hover:scale-110 transition-transform" size={24} />}
              <span className="text-sm font-semibold">{isUploading ? 'Ingesting...' : 'Import Documents'}</span>
            </button>
          </div>

          {/* Sources Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between px-1">
              <h3 className={`text-xs font-bold uppercase tracking-widest ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>Library</h3>
              {messages.length > 0 && (
                <button onClick={clearHistory} className="text-red-500 hover:text-red-400 transition-colors p-1" title="Clear Chat">
                  <Trash2 size={16} />
                </button>
              )}
            </div>
            <div className="space-y-2">
              {uploadedFiles.length === 0 ? (
                <div className={`text-sm italic px-2 py-4 border rounded-lg border-dashed ${isDarkMode ? 'border-slate-700 text-slate-600' : 'border-slate-200 text-slate-400'}`}>
                  No sources active.
                </div>
              ) : (
                uploadedFiles.map((file, idx) => (
                  <div key={idx} className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isDarkMode 
                    ? 'bg-slate-800/50 border-slate-700 hover:border-emerald-500/50' 
                    : 'bg-white border-slate-200 hover:border-emerald-300'
                  }`}>
                    <FileText className="text-emerald-500 flex-shrink-0" size={18} />
                    <span className="text-sm font-medium truncate">{file}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col min-w-0">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 py-10">
          <div className="max-w-4xl mx-auto space-y-10">
            {messages.length === 0 && !isQuerying && (
              <div className="text-center py-32 space-y-6">
                <div className={`w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-xl ${isDarkMode ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>
                  <BookOpen size={48} />
                </div>
                <h2 className="text-4xl font-black tracking-tight">Master your material.</h2>
                <p className={`text-lg max-w-lg mx-auto ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  Upload your study guides, papers, or notes and start asking questions grounded in your content.
                </p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                <div className={`max-w-[90%] md:max-w-[75%] rounded-2xl px-6 py-4 shadow-sm ${
                  msg.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : isDarkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-slate-200'
                }`}>
                  <p className="leading-relaxed text-base whitespace-pre-wrap">{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className={`mt-4 pt-3 border-t ${isDarkMode ? 'border-slate-700' : 'border-slate-100'}`}>
                      <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-50 mb-2">Validated Sources</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((s, i) => (
                          <span key={i} className={`text-[11px] px-2.5 py-1 rounded-md font-bold italic ${isDarkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isQuerying && (
              <div className="flex justify-start animate-pulse">
                <div className={`rounded-2xl px-6 py-4 flex items-center gap-3 border ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-50 border-slate-200'}`}>
                  <Loader2 className="animate-spin text-blue-500" size={20} />
                  <span className="text-sm font-bold tracking-wide opacity-70 italic text-blue-500">Synthesizing Answer...</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input Dock */}
        <div className={`px-4 md:px-8 py-8 border-t backdrop-blur-xl sticky bottom-0 z-10 ${isDarkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white/80 border-slate-200'}`}>
          <div className="max-w-4xl mx-auto">
            <form onSubmit={handleQuery} className="relative group">
              <input 
                type="text" 
                autoFocus
                className={`w-full border-2 rounded-2xl py-5 pl-7 pr-20 text-lg transition-all shadow-xl outline-none ${
                  isDarkMode 
                  ? 'bg-slate-800 border-slate-700 focus:border-blue-500 focus:bg-slate-700 placeholder-slate-500' 
                  : 'bg-white border-slate-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-50 placeholder-slate-400'
                }`} 
                placeholder="Ask about your library..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isQuerying}
              />
              <button 
                type="submit" 
                disabled={isQuerying || !input.trim()}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-slate-300 disabled:scale-95 transition-all shadow-lg active:scale-95"
              >
                <Send size={24} />
              </button>
            </form>
            <div className="mt-4 flex items-center justify-center gap-4 text-[11px] font-bold uppercase tracking-widest opacity-40">
              <span>RAG Engine Active</span>
              <span className="w-1 h-1 rounded-full bg-current"></span>
              <span>Local Model Execution</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
