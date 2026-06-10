import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Upload, Send, FileText, BookOpen, Loader2, Moon, Sun, 
  Trash2, Plus, ChevronRight, Settings, BrainCircuit, X
} from 'lucide-react';

interface Notebook {
  id: string;
  name: string;
  created_at: string;
  last_model: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

const API_BASE_URL = 'http://localhost:8000';
const AVAILABLE_MODELS = ['llama3.2:1b', 'llama3.2:3b', 'qwen2.5:1.5b', 'mistral'];

function App() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [activeNotebook, setActiveNotebook] = useState<Notebook | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('llama3.2:1b');
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(() => localStorage.getItem('study_theme') === 'dark');
  const [showNewNotebookModal, setShowNewNotebookModal] = useState(false);
  const [newNotebookName, setNewNotebookName] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Appearance
  useEffect(() => {
    localStorage.setItem('study_theme', isDarkMode ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  // Initial Data
  useEffect(() => {
    fetchNotebooks();
  }, []);

  // Sync Messages and Files when active notebook changes
  useEffect(() => {
    if (activeNotebook) {
      fetchNotebookData(activeNotebook.id);
      setSelectedModel(activeNotebook.last_model || 'llama3.2:1b');
      setMessages([]); // Reset messages for now (history is not per notebook yet in backend, but will be contextually isolated by vectors)
    }
  }, [activeNotebook]);

  // Scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isQuerying]);

  const fetchNotebooks = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/notebooks`);
      setNotebooks(res.data);
      if (res.data.length > 0 && !activeNotebook) {
        setActiveNotebook(res.data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch notebooks:', error);
    }
  };

  const fetchNotebookData = async (id: string) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/notebooks/${id}/files`);
      setUploadedFiles(res.data.files);
    } catch (error) {
      console.error('Failed to fetch notebook data:', error);
    }
  };

  const createNotebook = async () => {
    if (!newNotebookName.trim()) return;
    try {
      const res = await axios.post(`${API_BASE_URL}/notebooks`, { name: newNotebookName });
      setNotebooks([...notebooks, res.data]);
      setActiveNotebook(res.data);
      setNewNotebookName('');
      setShowNewNotebookModal(false);
    } catch (error) {
      console.error('Failed to create notebook:', error);
    }
  };

  const deleteNotebook = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Tem certeza que deseja apagar este notebook e todas as suas referências?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/notebooks/${id}`);
      const updated = notebooks.filter(n => n.id !== id);
      setNotebooks(updated);
      if (activeNotebook?.id === id) {
        setActiveNotebook(updated.length > 0 ? updated[0] : null);
      }
    } catch (error) {
      console.error('Failed to delete notebook:', error);
    }
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!activeNotebook) return;
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE_URL}/notebooks/${activeNotebook.id}/upload`, formData);
      fetchNotebookData(activeNotebook.id);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload falhou. Verifique se o backend está rodando.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const deleteFile = async (filename: string) => {
    if (!activeNotebook) return;
    if (!window.confirm(`Apagar referência "${filename}"?`)) return;
    try {
      await axios.delete(`${API_BASE_URL}/notebooks/${activeNotebook.id}/files/${filename}`);
      fetchNotebookData(activeNotebook.id);
    } catch (error) {
      console.error('Delete file failed:', error);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isQuerying || !activeNotebook) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsQuerying(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, { 
        notebook_id: activeNotebook.id,
        question: userMsg,
        model: selectedModel
      });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      }]);
    } catch (error) {
      console.error('Query failed:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Erro ao processar sua pergunta. Verifique se o Ollama está rodando e o modelo baixado.' 
      }]);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className={`flex h-screen w-full transition-colors duration-200 ${isDarkMode ? 'bg-slate-900 text-slate-100' : 'bg-white text-slate-900'}`}>
      
      {/* Sidebar: Notebooks */}
      <aside className={`w-72 flex-shrink-0 border-r flex flex-col ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-200'}`}>
        <div className={`p-5 flex items-center justify-between border-b ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center gap-2">
            <BookOpen className="text-blue-500" size={20} />
            <h1 className="text-lg font-bold tracking-tight">Estudo</h1>
          </div>
          <button 
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-slate-700 text-yellow-400' : 'hover:bg-slate-200 text-slate-600'}`}
          >
            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <div className="flex items-center justify-between mb-4 px-1">
            <h3 className={`text-[10px] font-black uppercase tracking-[0.2em] ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>Notebooks</h3>
            <button onClick={() => setShowNewNotebookModal(true)} className="p-1 hover:bg-blue-500/10 text-blue-500 rounded-md transition-all">
              <Plus size={18} />
            </button>
          </div>

          {notebooks.map((nb) => (
            <div 
              key={nb.id}
              onClick={() => setActiveNotebook(nb)}
              className={`group flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all border ${
                activeNotebook?.id === nb.id 
                ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20' 
                : isDarkMode ? 'bg-transparent border-transparent hover:bg-slate-700/50' : 'bg-transparent border-transparent hover:bg-slate-200/50'
              }`}
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${activeNotebook?.id === nb.id ? 'bg-white' : 'bg-blue-400'}`} />
                <span className="text-sm font-semibold truncate">{nb.name}</span>
              </div>
              <button 
                onClick={(e) => deleteNotebook(nb.id, e)}
                className={`p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity ${activeNotebook?.id === nb.id ? 'hover:bg-blue-700 text-white/70' : 'hover:bg-red-500/10 text-red-500'}`}
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Area */}
      <main className="flex-1 flex min-w-0">
        
        {/* Chat Section */}
        <section className="flex-1 flex flex-col min-w-0 relative">
          {/* Header */}
          <header className={`h-16 flex items-center justify-between px-8 border-b backdrop-blur-md sticky top-0 z-20 ${isDarkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white/80 border-slate-200'}`}>
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-black tracking-tight">{activeNotebook?.name || 'Selecione um Notebook'}</h2>
              {activeNotebook && (
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${isDarkMode ? 'bg-slate-800 text-slate-400' : 'bg-slate-100 text-slate-500'}`}>
                  <BrainCircuit size={12} />
                  {selectedModel}
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-3">
              <select 
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className={`text-xs font-bold bg-transparent border rounded-lg px-3 py-1.5 outline-none transition-all ${
                  isDarkMode ? 'border-slate-700 hover:border-blue-500' : 'border-slate-300 hover:border-blue-400'
                }`}
              >
                {AVAILABLE_MODELS.map(m => <option key={m} value={m} className={isDarkMode ? 'bg-slate-800' : 'bg-white'}>{m}</option>)}
              </select>
            </div>
          </header>

          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 py-10">
            <div className="max-w-3xl mx-auto space-y-10">
              {!activeNotebook ? (
                <div className="text-center py-32 space-y-6">
                  <div className="w-20 h-20 rounded-3xl bg-blue-500/10 text-blue-500 flex items-center justify-center mx-auto mb-6">
                    <Plus size={40} />
                  </div>
                  <h2 className="text-2xl font-black">Crie um novo notebook para começar</h2>
                  <p className="opacity-50 max-w-sm mx-auto">Organize seus estudos separando conteúdos por notebooks dedicados.</p>
                </div>
              ) : messages.length === 0 && !isQuerying && (
                <div className="text-center py-32 space-y-6">
                  <h2 className="text-3xl font-black tracking-tight">O que vamos aprender hoje?</h2>
                  <p className={`text-lg max-w-lg mx-auto ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                    Pergunte qualquer coisa sobre as referências que você adicionou ao notebook <strong>{activeNotebook.name}</strong>.
                  </p>
                </div>
              )}

              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-6 py-4 shadow-sm leading-relaxed ${
                    msg.role === 'user' 
                    ? 'bg-blue-600 text-white font-medium' 
                    : isDarkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-slate-200'
                  }`}>
                    {msg.content}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className={`mt-4 pt-3 border-t flex flex-wrap gap-2 ${isDarkMode ? 'border-slate-700' : 'border-slate-100'}`}>
                        {msg.sources.map((s, i) => (
                          <span key={i} className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${isDarkMode ? 'bg-slate-700 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isQuerying && (
                <div className="flex justify-start">
                  <div className={`rounded-2xl px-6 py-4 flex items-center gap-3 border ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-50 border-slate-200'}`}>
                    <Loader2 className="animate-spin text-blue-500" size={18} />
                    <span className="text-sm font-bold opacity-60 italic">Analisando referências...</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Input Dock */}
          <div className="p-8">
            <div className="max-w-3xl mx-auto">
              <form onSubmit={handleQuery} className="relative">
                <input 
                  type="text" 
                  disabled={!activeNotebook || isQuerying}
                  className={`w-full border-2 rounded-2xl py-4 pl-6 pr-16 text-lg transition-all outline-none ${
                    isDarkMode 
                    ? 'bg-slate-800 border-slate-700 focus:border-blue-500 placeholder-slate-600' 
                    : 'bg-white border-slate-200 focus:border-blue-400 placeholder-slate-400'
                  }`} 
                  placeholder={activeNotebook ? "Sua pergunta..." : "Crie um notebook para começar"}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <button 
                  type="submit" 
                  disabled={isQuerying || !input.trim() || !activeNotebook}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-30 transition-all"
                >
                  <Send size={20} />
                </button>
              </form>
            </div>
          </div>
        </section>

        {/* References Drawer */}
        <aside className={`w-80 flex-shrink-0 border-l flex flex-col ${isDarkMode ? 'bg-slate-900 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
          <div className="p-5 border-b flex items-center gap-2">
            <Settings className="text-slate-400" size={18} />
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-slate-500">Referências</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Upload Area */}
            <input type="file" ref={fileInputRef} onChange={handleUpload} className="hidden" accept=".pdf,.md" />
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading || !activeNotebook}
              className={`w-full py-8 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center gap-3 transition-all ${
                !activeNotebook ? 'opacity-30 cursor-not-allowed' :
                isDarkMode ? 'border-slate-700 hover:border-blue-500 hover:bg-blue-500/5' : 'border-slate-300 hover:border-blue-400 hover:bg-white'
              }`}
            >
              {isUploading ? <Loader2 className="animate-spin text-blue-500" /> : <Upload className="text-slate-400" size={28} />}
              <div className="text-center px-4">
                <p className="text-sm font-bold">Adicionar Arquivo</p>
                <p className="text-[10px] opacity-50 uppercase mt-1">PDF ou Markdown</p>
              </div>
            </button>

            {/* File List */}
            <div className="space-y-3">
              {uploadedFiles.map((file, idx) => (
                <div key={idx} className={`group flex items-center justify-between p-3 rounded-xl border ${
                  isDarkMode ? 'bg-slate-800/40 border-slate-700' : 'bg-white border-slate-200 shadow-sm'
                }`}>
                  <div className="flex items-center gap-3 overflow-hidden">
                    <FileText className="text-blue-500 flex-shrink-0" size={16} />
                    <span className="text-xs font-semibold truncate">{file}</span>
                  </div>
                  <button onClick={() => deleteFile(file)} className="p-1 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
              {activeNotebook && uploadedFiles.length === 0 && (
                <p className="text-center py-10 text-xs italic opacity-30">Nenhuma referência adicionada.</p>
              )}
            </div>
          </div>
        </aside>
      </main>

      {/* New Notebook Modal */}
      {showNewNotebookModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className={`w-full max-w-md p-8 rounded-3xl shadow-2xl animate-in zoom-in-95 duration-200 ${isDarkMode ? 'bg-slate-800 text-white' : 'bg-white text-slate-900'}`}>
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-black">Novo Notebook</h2>
              <button onClick={() => setShowNewNotebookModal(false)} className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <X size={20} />
              </button>
            </div>
            <div className="space-y-6">
              <div>
                <label className="text-xs font-black uppercase tracking-widest opacity-40 block mb-3">Nome do Notebook</label>
                <input 
                  autoFocus
                  type="text" 
                  value={newNotebookName}
                  onChange={(e) => setNewNotebookName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && createNotebook()}
                  placeholder="Ex: Física Quântica, Concurso BB..."
                  className={`w-full px-5 py-4 rounded-xl border-2 outline-none transition-all ${
                    isDarkMode ? 'bg-slate-900 border-slate-700 focus:border-blue-500' : 'bg-slate-50 border-slate-200 focus:border-blue-400'
                  }`}
                />
              </div>
              <button 
                onClick={createNotebook}
                disabled={!newNotebookName.trim()}
                className="w-full py-4 bg-blue-600 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 hover:bg-blue-700 disabled:opacity-30 transition-all"
              >
                Criar Notebook
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
