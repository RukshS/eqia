'use client';

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  BookOpenIcon,
  UserIcon,
  CpuChipIcon,
  ChartBarIcon,
  PresentationChartLineIcon,
  AcademicCapIcon,
  LightBulbIcon,
  BeakerIcon,
  ArrowPathIcon,
  MicrophoneIcon,
  PaperAirplaneIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

interface ChatHistoryItem {
  id: string;
  title: string;
  timestamp: string;
}

interface SidebarItem {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  href?: string;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

// Component to render message content with markdown support
const MessageContent: React.FC<{ message: Message }> = ({ message }) => {
  if (message.isUser) {
    // User messages as plain text
    return (
      <div className="user-message">
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.text}</p>
      </div>
    );
  }

  // Bot messages with markdown rendering
  return (
    <div className="markdown-content">{" "}
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={{
          // Custom styling for markdown elements
          h1: ({ children }) => <h1 className="text-lg font-bold text-slate-800 mb-3 mt-4 first:mt-0">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold text-slate-800 mb-2 mt-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-medium text-slate-800 mb-2 mt-2">{children}</h3>,
          p: ({ children }) => <p className="text-sm leading-relaxed mb-3 last:mb-0 text-slate-700">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3 ml-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-3 ml-2">{children}</ol>,
          li: ({ children }) => <li className="text-sm text-slate-700">{children}</li>,
          code: ({ children, className }) => {
            const isInline = !className;
            return isInline ? (
              <code className="bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded text-xs font-mono font-medium">
                {children}
              </code>
            ) : (
              <code className={`block bg-slate-900 text-slate-100 p-4 rounded-lg text-xs font-mono overflow-x-auto leading-relaxed ${className || ''}`}>
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto mb-3 border border-slate-700">
              {children}
            </pre>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-emerald-500 pl-4 py-2 bg-emerald-50 rounded-r text-sm mb-3">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto mb-3 rounded-lg border border-slate-200">
              <table className="min-w-full table-auto border-collapse">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-slate-50">{children}</thead>,
          tbody: ({ children }) => <tbody className="bg-white">{children}</tbody>,
          th: ({ children }) => (
            <th className="border-b border-slate-200 px-4 py-2 text-left text-xs font-semibold text-slate-700 bg-slate-50">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-b border-slate-100 px-4 py-2 text-xs text-slate-600">
              {children}
            </td>
          ),
          tr: ({ children }) => <tr className="hover:bg-slate-25">{children}</tr>,
          strong: ({ children }) => <strong className="font-semibold text-slate-900">{children}</strong>,
          em: ({ children }) => <em className="italic text-slate-700">{children}</em>,
          a: ({ children, href }) => (
            <a 
              href={href} 
              className="text-emerald-600 hover:text-emerald-700 underline decoration-emerald-300 hover:decoration-emerald-500 transition-colors font-medium" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          hr: () => <hr className="border-slate-200 my-4" />,
        }}
      >
        {message.text}
      </ReactMarkdown>
    </div>
  );
};

const Dashboard = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  // Sample chat history data
  const chatHistory: ChatHistoryItem[] = [
    { id: '1', title: 'Soil pH monitoring in agricultural fields', timestamp: '2 hours ago' },
    { id: '2', title: 'Water quality assessment parameters', timestamp: '1 day ago' },
    { id: '3', title: 'Soil moisture sensor calibration', timestamp: '2 days ago' },
    { id: '4', title: 'Water contamination detection methods', timestamp: '3 days ago' },
    { id: '5', title: 'Nutrient analysis in soil samples', timestamp: '1 week ago' },
    { id: '6', title: 'Water turbidity measurement techniques', timestamp: '1 week ago' },
  ];

  // Sidebar navigation items
  const sidebarItems: SidebarItem[] = [
    { icon: PlusIcon, label: 'New monitoring session' },
    { icon: MagnifyingGlassIcon, label: 'Search monitoring data' },
    { icon: BookOpenIcon, label: 'Documentation' },
    { icon: GlobeAltIcon, label: 'Soil Monitoring' },
    { icon: BeakerIcon, label: 'Water Quality Analysis' },
    { icon: ChartBarIcon, label: 'Environmental Reports' },
    { icon: PresentationChartLineIcon, label: 'Data Visualization' },
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      text: inputMessage,
      isUser: true,
      timestamp: new Date().toLocaleTimeString()
    };

    // Optimistically add a placeholder bot message while fetching
    const placeholderId = (Date.now() + 1).toString();
    const botPlaceholder = {
      id: placeholderId,
      text: 'Thinking...',
      isUser: false,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage, botPlaceholder]);
    const query = inputMessage;
    setInputMessage('');
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const answer = data.response || 'No response';
      setMessages(prev => prev.map(m => m.id === placeholderId ? { ...m, text: answer } : m));
    } catch (e: any) {
      setMessages(prev => prev.map(m => m.id === placeholderId ? { ...m, text: `Error: ${e.message}` } : m));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Sidebar */}
      <div className="w-80 bg-white/80 backdrop-blur-sm border-r border-slate-200 flex flex-col shadow-lg">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-emarald-500 to-teal-600 rounded-lg flex items-center justify-center shadow-md">
              <span className="text-white font-bold text-sm">EQ</span>
            </div>
            <span className="font-semibold text-slate-800">EQIA Monitoring</span>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto">
          {/* Top Navigation */}
          <div className="p-3 space-y-1">
            {sidebarItems.slice(0, 2).map((item, index) => (
              <button
                key={index}
                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 hover:text-emerald-700 rounded-lg transition-all duration-200"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}
          </div>

          {/* Section Divider */}
          <div className="px-6 py-2">
            <div className="border-t border-slate-200"></div>
          </div>

          {/* Other Navigation Items */}
          <div className="p-3 space-y-1">
            {sidebarItems.slice(2).map((item, index) => (
              <button
                key={index + 2}
                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 hover:text-emerald-700 rounded-lg transition-all duration-200"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}
          </div>

          {/* Section Divider */}
          <div className="px-6 py-2">
            <div className="border-t border-slate-200"></div>
          </div>

          {/* Monitoring History Section */}
          <div className="p-3">
            <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-3">
              Recent Monitoring Sessions
            </h3>
            <div className="space-y-1">
              {chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  className="w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 hover:text-emerald-700 rounded-lg transition-all duration-200 group"
                >
                  <div className="truncate font-medium">{chat.title}</div>
                  <div className="text-xs text-slate-500 mt-1">
                    {chat.timestamp}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 text-sm text-slate-700">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center shadow-md">
              <span className="text-white font-semibold text-xs">K</span>
            </div>
            <div>
              <div className="font-medium">Koneswaran Kapeilaash</div>
              <div className="text-xs text-slate-500">Free Plan</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white/90 backdrop-blur-sm border-b border-slate-200 px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-slate-800">
              Environmental Quality Monitoring
            </h1>
            <button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white px-6 py-2 rounded-xl text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-xl">
              Start Monitoring
            </button>
          </div>
        </div>

        {/* Chat Area - Full height container */}
        <div className="flex-1 flex flex-col min-h-0 p-6">
          {messages.length === 0 ? (
            // Welcome screen when no messages
            <div className="flex-1 flex flex-col justify-center items-center">
              <div className="max-w-3xl w-full text-center">
                <h2 className="text-4xl font-bold bg-gradient-to-r from-slate-800 to-emerald-700 bg-clip-text text-transparent mb-8">
                  How can I help with environmental monitoring?
                </h2>
                
                {/* Input Area */}
                <div className="relative max-w-2xl mx-auto">
                  <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200 shadow-xl">
                    <div className="flex items-end p-4">
                      <button 
                        className="p-2 hover:bg-emerald-50 rounded-lg transition-colors mr-2"
                        aria-label="Add attachment"
                      >
                        <PlusIcon className="w-5 h-5 text-emerald-600" />
                      </button>
                      
                      <div className="flex-1 relative">
                        <textarea
                          value={inputMessage}
                          onChange={(e) => setInputMessage(e.target.value)}
                          onKeyDown={handleKeyPress}
                          placeholder="Ask about soil or water monitoring..."
                          className="w-full resize-none border-0 bg-transparent text-slate-800 placeholder-slate-400 focus:outline-none max-h-48"
                          rows={1}
                        />
                      </div>

                      <div className="flex items-center gap-2 ml-2">
                        <button 
                          className="p-2 hover:bg-emerald-50 rounded-lg transition-colors"
                          aria-label="Voice input"
                        >
                          <MicrophoneIcon className="w-5 h-5 text-emerald-600" />
                        </button>
                        <button 
                          onClick={handleSendMessage}
                          disabled={!inputMessage.trim() || isLoading}
                          className="p-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                          aria-label="Send message"
                        >
                          <PaperAirplaneIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="px-4 pb-3">
                      <button className="flex items-center gap-2 text-sm text-emerald-600 hover:text-emerald-700 transition-colors">
                        <span>🌱</span>
                        <span>Environmental Tools</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Suggestions */}
                <div className="grid grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-slate-200 hover:border-emerald-300 hover:shadow-lg cursor-pointer transition-all duration-200 group">
                    <div className="flex items-center gap-3 mb-2">
                      <GlobeAltIcon className="w-5 h-5 text-emerald-600 group-hover:text-emerald-700" />
                      <span className="font-medium text-slate-800 group-hover:text-emerald-700">Soil Monitoring</span>
                    </div>
                    <p className="text-sm text-slate-600">
                      Check soil pH, moisture, nutrients, and health indicators
                    </p>
                  </div>
                  
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-slate-200 hover:border-teal-300 hover:shadow-lg cursor-pointer transition-all duration-200 group">
                    <div className="flex items-center gap-3 mb-2">
                      <BeakerIcon className="w-5 h-5 text-teal-600 group-hover:text-teal-700" />
                      <span className="font-medium text-slate-800 group-hover:text-teal-700">Water Quality</span>
                    </div>
                    <p className="text-sm text-slate-600">
                      Analyze water purity, contamination, and safety parameters
                    </p>
                  </div>
                  
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-lg cursor-pointer transition-all duration-200 group">
                    <div className="flex items-center gap-3 mb-2">
                      <ChartBarIcon className="w-5 h-5 text-indigo-600 group-hover:text-indigo-700" />
                      <span className="font-medium text-slate-800 group-hover:text-indigo-700">Data Analysis</span>
                    </div>
                    <p className="text-sm text-slate-600">
                      Generate reports and visualize monitoring trends
                    </p>
                  </div>
                  
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-slate-200 hover:border-amber-300 hover:shadow-lg cursor-pointer transition-all duration-200 group">
                    <div className="flex items-center gap-3 mb-2">
                      <LightBulbIcon className="w-5 h-5 text-amber-600 group-hover:text-amber-700" />
                      <span className="font-medium text-slate-800 group-hover:text-amber-700">Recommendations</span>
                    </div>
                    <p className="text-sm text-slate-600">
                      Get insights and improvement suggestions
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Chat messages display - Full height with proper scrolling
            <div className="flex-1 flex flex-col h-full min-h-0">
              {/* Messages container with fixed height and scrolling */}
              <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 min-h-0 chat-messages">
                {messages.map((message, index) => (
                  <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-3xl px-5 py-4 rounded-2xl shadow-lg break-words ${
                      message.isUser 
                        ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white' 
                        : 'bg-white/95 backdrop-blur-sm text-slate-800 border border-slate-200'
                    }`}>
                      <MessageContent message={message} />
                      <p className={`text-xs mt-3 opacity-75 ${message.isUser ? 'text-emerald-100' : 'text-slate-500'}`}>
                        {message.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Fixed Input Area at bottom */}
              <div className="flex-shrink-0 border-t border-slate-200 bg-white/90 backdrop-blur-sm px-4 py-4 mt-4">
                <div className="flex items-end gap-3 max-w-4xl mx-auto">
                  <div className="flex-1">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Ask about soil or water monitoring..."
                      className="w-full resize-none border border-slate-300 rounded-xl p-4 bg-white/95 backdrop-blur-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 max-h-32 shadow-sm text-sm leading-relaxed"
                      rows={2}
                    />
                  </div>
                  <button 
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="p-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl flex-shrink-0"
                    aria-label="Send message"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                  </button>
                </div>
                {isLoading && (
                  <p className="mt-2 text-xs text-slate-500">Waiting for backend response...</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;