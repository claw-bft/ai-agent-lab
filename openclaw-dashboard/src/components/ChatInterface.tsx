import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Command, Sparkles, Trash, Copy } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '👋 欢迎使用 OpenClaw 控制面板！\n\n我可以帮助你：\n• 查看和管理任务\n• 浏览和配置技能\n• 执行系统命令\n• 获取系统状态\n\n输入 /help 查看所有可用命令。',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateResponse(input),
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsTyping(false)
    }, 1000)
  }

  const generateResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase()
    
    if (lowerQuery.includes('/help') || lowerQuery.includes('帮助')) {
      return `📋 可用命令列表：\n\n**任务管理**\n• /tasks - 查看所有任务\n• /task create <名称> - 创建新任务\n• /task complete <ID> - 完成任务\n\n**技能管理**\n• /skills - 列出所有技能\n• /skill info <名称> - 查看技能详情\n\n**系统**\n• /status - 系统状态\n• /clear - 清空对话`
    }
    
    if (lowerQuery.includes('任务') || lowerQuery.includes('task')) {
      return '📊 当前有 1 个进行中任务和 0 个待处理任务。\n\n最新任务：\n• Task-001: LLM Coding能力对比网站 (已完成)'
    }
    
    if (lowerQuery.includes('技能') || lowerQuery.includes('skill')) {
      return '⚡ 系统已加载 50+ 个技能，包括：\n\n• Discord / Slack 集成\n• GitHub 操作\n• 飞书文档\n• 天气查询\n• 图像生成\n\n使用 /skills 查看完整列表。'
    }
    
    if (lowerQuery.includes('状态') || lowerQuery.includes('status')) {
      return '✅ 系统运行正常\n\n• OpenClaw Gateway: 在线\n• 内存使用: 45%\n• 磁盘空间: 72%\n• 活跃会话: 1'
    }
    
    return `收到："${query}"\n\n我是一个模拟的 AI 助手。在实际部署中，这里将连接到 OpenClaw 的核心系统，可以执行真实的命令和任务。`
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '对话已清空。有什么可以帮助你的吗？',
        timestamp: new Date(),
      },
    ])
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-surface border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-surface/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <Command className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-text-primary">OpenClaw 终端</h3>
            <p className="text-xs text-muted">AI 驱动的命令界面</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={clearChat}
            className="p-2 rounded-lg text-muted hover:text-error hover:bg-error/10 transition-colors"
            title="清空对话"
          >
            <Trash className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-primary to-secondary'
                  : 'bg-surface-hover border border-border'
              }`}
            >
              {message.role === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-primary" />
              )}
            </div>
            
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary text-white rounded-br-md'
                  : 'bg-surface-hover border border-border rounded-bl-md'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              <div
                className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-white/60' : 'text-muted'
                }`}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-surface-hover border border-border flex items-center justify-center">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-surface-hover border border-border rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border bg-surface/50">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入命令或消息... (Enter 发送, Shift+Enter 换行)"
            className="w-full bg-background border border-border rounded-xl px-4 py-3 pr-12 text-text-primary placeholder-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary resize-none"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="absolute right-3 bottom-3 p-2 rounded-lg bg-primary text-white hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center justify-between mt-2 text-xs text-muted">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Command className="w-3 h-3" />
              /help 查看命令
            </span>
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI 驱动
            </span>
          </div>
          <span>{input.length} 字符</span>
        </div>
      </div>
    </div>
  )
}
