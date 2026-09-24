import { useState, useRef, useEffect } from 'react';
import { copilotService, CopilotResponse, CopilotContext } from '../services/copilotService';

export function Copilot() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string; response?: CopilotResponse }[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [activeContext, setActiveContext] = useState<CopilotContext>({ page: 'copilot' });

  const suggestions = [
    "Explain the latest FedAvg run.",
    "Why was round 2 marked partial success?",
    "Which clients were rejected in the last run?",
    "Explain the privacy trade-off in this run.",
    "Compare the latest baseline run and DP run.",
    "What does epsilon mean in this FedGuard experiment?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (message: string) => {
    if (!message.trim()) return;
    
    const newMessages = [...messages, { role: 'user' as const, content: message }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await copilotService.chat(message, activeContext);
      setMessages([...newMessages, { role: 'assistant', content: res.answer, response: res }]);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "An error occurred connecting to the Copilot.";
      setMessages([...newMessages, { role: 'assistant', content: `Error: ${errorMsg}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] bg-gray-50 p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">FedGuard Copilot</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Context:</span>
          <input 
            type="text" 
            placeholder="Run ID (optional)"
            className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:ring-2 focus:ring-blue-500 outline-none w-48"
            onChange={(e) => setActiveContext({ ...activeContext, run_id: e.target.value })}
          />
        </div>
      </div>

      <div className="flex-1 bg-white border border-gray-200 rounded-2xl shadow-sm flex flex-col overflow-hidden">
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-6">
              <div className="bg-blue-50 text-blue-600 p-4 rounded-full">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="space-y-2 max-w-md">
                <h2 className="text-xl font-medium text-gray-900">How can I help with your federated runs?</h2>
                <p className="text-sm text-gray-500">I can analyze metrics, explain privacy configurations, and audit reliable client participation.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 w-full max-w-2xl mt-4">
                {suggestions.map((s, i) => (
                  <button 
                    key={i} 
                    onClick={() => handleSend(s)}
                    className="text-left p-4 bg-gray-50 hover:bg-gray-100 border border-gray-100 rounded-xl transition-colors text-sm text-gray-700"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, idx) => (
            <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] rounded-2xl p-4 ${
                m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-50 border border-gray-100 text-gray-800'
              }`}>
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</div>
                {m.response && (
                  <div className="mt-4 pt-3 border-t border-gray-200 flex flex-wrap gap-2 items-center">
                    <span className={`text-xs px-2 py-1 rounded-md font-medium ${m.response.mode === 'bedrock' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'}`}>
                      {m.response.mode.toUpperCase()}
                    </span>
                    {m.response.sources.map((src, i) => (
                      <span key={i} className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-md">
                        {src.type}: {src.id}
                      </span>
                    ))}
                    {m.response.warnings.map((warn, i) => (
                      <span key={`w-${i}`} className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-md">
                        {warn}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 border border-gray-100 rounded-2xl p-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
              placeholder="Ask Copilot about a run, metric, or privacy setting..."
              className="w-full bg-gray-50 border border-gray-200 text-gray-900 text-sm rounded-full focus:ring-2 focus:ring-blue-500 outline-none pl-6 pr-14 py-4 shadow-sm"
              disabled={loading}
            />
            <button
              onClick={() => handleSend(input)}
              disabled={loading || !input.trim()}
              className="absolute right-3 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}