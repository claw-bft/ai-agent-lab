import ChatInterface from '../components/ChatInterface'

export default function Chat() {
  return (
    <div className="h-[calc(100vh-6rem)] animate-fade-in">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-text-primary">交互终端</h1>
        <p className="text-text-secondary mt-1">与 OpenClaw AI 助手对话，执行命令和管理任务</p>
      </div>

      <ChatInterface />
    </div>
  )
}
