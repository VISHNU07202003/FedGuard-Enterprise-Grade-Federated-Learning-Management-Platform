import { Bot, Send } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { copilotService, CopilotResponse, CopilotContext } from '../services/copilotService';

export function Copilot() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string; response?: CopilotResponse; error?: boolean }[]>([]);
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
    messagesEndRef.current?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (message: string) => {
    if (loading || !message.trim()) return;

    const newMessages = [...messages, { role: 'user' as const, content: message }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await copilotService.chat(message, activeContext);
      setMessages([...newMessages, { role: 'assistant', content: res.answer, response: res }]);
    } catch (error: unknown) {
      console.error('Copilot request failed', error instanceof Error ? error.message : 'Unexpected error');
      const errorMsg = 'Copilot could not respond. Check your connection and try sending your question again.';
      setMessages([...newMessages, { role: 'assistant', content: errorMsg, error: true }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-[640px] h-[calc(100dvh-136px)]">
      <div className="flex flex-wrap gap-4 items-center justify-between mb-6">
        <div><p className="eyebrow mb-2 text-primary">Intelligence / Assistant</p><h1 className="text-3xl font-semibold text-foreground">FedGuard AI Copilot</h1><p className="mt-2 text-sm text-muted-foreground">Powered by UF NaviGator</p></div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Context:</span>
          <input
            type="text"
            aria-label="Run context (optional run ID)" placeholder="Run ID (optional)"
            className="text-sm border border-border rounded-md px-3 py-1 focus:ring-2 focus:ring-blue-500 outline-none w-48"
            onChange={(e) => setActiveContext({ ...activeContext, run_id: e.target.value })}
          />
        </div>
      </div>

      <div className="flex-1 bg-card border border-border rounded-2xl shadow-sm flex flex-col overflow-hidden">
        {/* Chat History */}
        <div role="log" aria-label="Copilot conversation" aria-live="polite" className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 && (
            <div className="min-h-full flex flex-col items-center justify-center py-4 text-center space-y-6">
              <div className="bg-blue-500/10 text-blue-300 p-4 rounded-full">
                <Bot size={32} />
              </div>
              <div className="space-y-2 max-w-md">
                <h2 className="text-xl font-medium text-foreground">How can I help with your federated runs?</h2>
                <p className="text-sm text-muted-foreground">Explore reported metrics, privacy configurations, and client participation. Add a run ID to focus your question.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl mt-4">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(s)}
                    className="text-left p-4 bg-muted hover:bg-muted border border-border rounded-xl transition-colors text-sm text-foreground"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, idx) => (
            <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`min-w-0 max-w-[95%] sm:max-w-[80%] break-words rounded-2xl p-4 ${
                m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-muted border border-border text-foreground'
              }`}>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider opacity-80">{m.error ? 'Request failed' : m.role === 'user' ? 'You' : 'FedGuard Copilot'}</p><div role={m.error ? 'alert' : undefined} className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</div>
                {m.response && (
                  <div className="mt-4 pt-3 border-t border-border flex flex-wrap gap-2 items-center">
                    <span className={`text-xs px-2 py-1 rounded-md font-medium ${m.response.mode === 'bedrock' ? 'bg-purple-500/10 text-purple-300' : 'bg-orange-500/10 text-orange-300'}`}>
                      {m.response.mode.toUpperCase()}
                    </span>
                    {m.response.sources.map((src, i) => (
                      <span key={i} className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded-md">
                        {src.type}: {src.id}
                      </span>
                    ))}
                    {m.response.warnings.map((warn, i) => (
                      <span key={`w-${i}`} className="text-xs bg-red-500/10 text-red-300 px-2 py-1 rounded-md">
                        {warn}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div role="status" aria-label="Copilot is preparing a response" className="flex justify-start">
              <div className="bg-muted border border-border rounded-2xl p-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-card border-t border-border">
          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.nativeEvent.isComposing && handleSend(input)}
              aria-label="Message FedGuard Copilot" placeholder="Ask Copilot about a run, metric, or privacy setting..."
              className="w-full bg-muted border border-border text-foreground text-sm rounded-full focus:ring-2 focus:ring-blue-500 outline-none pl-6 pr-14 py-4 shadow-sm"
              disabled={loading}
            />
            <button
              aria-label="Send message" onClick={() => handleSend(input)}
              disabled={loading || !input.trim()}
              className="absolute right-3 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
