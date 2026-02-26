import { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Trash2,
  RefreshCw,
  Command
} from 'lucide-react';
import { fetchApi, cn } from '../lib/utils';
import { useWebSocket } from '../hooks/useWebSocket';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { lastMessage, sendMessage: sendWsMessage } = useWebSocket();

  useEffect(() => {
    loadMessages();
  }, []);

  useEffect(() => {
    if (lastMessage?.type === 'message') {
      setMessages(prev => [...prev, lastMessage.data]);
    }
  }, [lastMessage]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const data = await fetchApi('/messages');
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const content = input.trim();
    setInput('');
    setLoading(true);

    try {
      // Send via API
      await fetchApi('/message', {
        method: 'POST',
        body: JSON.stringify({ content, role: 'user' }),
      });

      // Also send via WebSocket for real-time updates
      sendWsMessage({
        type: 'message',
        data: { content, role: 'user' }
      });

      // Simulate assistant response (in real implementation, this would come from OpenClaw)
      setTimeout(async () => {
        await fetchApi('/message', {
          method: 'POST',
          body: JSON.stringify({
            content: `Received: "${content}"\n\nThis is a simulated response. In a real implementation, this would be processed by OpenClaw.`,
            role: 'assistant',
          }),
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to send message:', error);
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!confirm('Clear all messages?')) return;
    
    try {
      // Clear messages on server (this would need a dedicated endpoint)
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear messages:', error);
    }
  };

  const quickCommands = [
    { label: 'Status', command: '/status' },
    { label: 'Tasks', command: '/tasks' },
    { label: 'Help', command: '/help' },
  ];

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-3xl font-bold">Chat</h1>
          <p className="text-muted-foreground mt-1">
            Real-time conversation with OpenClaw
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadMessages}
            className="flex items-center gap-2 px-3 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleClear}
            className="flex items-center gap-2 px-3 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 bg-card rounded-xl border border-border flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
              <Bot className="w-12 h-12 mb-4 opacity-50" />
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm">Send a message to interact with OpenClaw</p>
              
              <div className="flex gap-2 mt-4">
                {quickCommands.map((cmd) => (
                  <button
                    key={cmd.command}
                    onClick={() => setInput(cmd.command)}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm bg-muted rounded-full hover:bg-muted/80"
                  >
                    <Command className="w-3 h-3" />
                    {cmd.label}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  message.role === 'user' ? 'flex-row-reverse' : ''
                )}
              >
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                  message.role === 'user' 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-secondary'
                )}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                
                <div className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-2",
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-sm'
                    : 'bg-muted rounded-tl-sm'
                )}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <span className={cn(
                    "text-xs mt-1 block",
                    message.role === 'user' 
                      ? 'text-primary-foreground/70' 
                      : 'text-muted-foreground'
                  )}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              disabled={loading}
              className="flex-1 px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Send
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
