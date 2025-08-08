'use client';

import React, { useState } from 'react';
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

const Dashboard = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Array<{id: string, text: string, isUser: boolean, timestamp: string}>>([]);

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

  const generateResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    
    // Soil monitoring responses
    if (lowerQuery.includes('soil') || lowerQuery.includes('ph') || lowerQuery.includes('moisture') || lowerQuery.includes('nutrient')) {
      if (lowerQuery.includes('ph')) {
        return "Soil pH monitoring is crucial for crop health. Optimal pH ranges from 6.0-7.0 for most crops. I can help you analyze pH levels, recommend testing methods, and suggest amendments for pH correction.";
      } else if (lowerQuery.includes('moisture')) {
        return "Soil moisture monitoring helps optimize irrigation. Key parameters include volumetric water content, field capacity, and permanent wilting point. I can guide you through sensor placement and data interpretation.";
      } else if (lowerQuery.includes('nutrient')) {
        return "Soil nutrient analysis includes NPK (Nitrogen, Phosphorus, Potassium) testing, organic matter content, and micronutrient levels. I can help interpret results and recommend fertilization strategies.";
      } else {
        return "Soil monitoring encompasses pH, moisture, nutrients, temperature, and organic matter. I can help you establish monitoring protocols, interpret data, and make recommendations for soil health improvement.";
      }
    }
    
    // Water monitoring responses
    else if (lowerQuery.includes('water') || lowerQuery.includes('quality') || lowerQuery.includes('contamination') || lowerQuery.includes('turbidity')) {
      if (lowerQuery.includes('quality')) {
        return "Water quality assessment includes physical, chemical, and biological parameters. Key indicators are pH, dissolved oxygen, turbidity, temperature, and bacterial content. I can help you design monitoring protocols.";
      } else if (lowerQuery.includes('contamination')) {
        return "Water contamination detection involves testing for heavy metals, pesticides, bacteria, and chemical pollutants. I can guide you through sampling procedures and interpretation of contamination levels.";
      } else if (lowerQuery.includes('turbidity')) {
        return "Turbidity measures water clarity and is a key indicator of water quality. High turbidity can indicate pollution or suspended particles. Normal levels are typically <1 NTU for drinking water.";
      } else {
        return "Water monitoring includes quality parameters like pH, dissolved oxygen, temperature, conductivity, and contamination levels. I can help you establish comprehensive water monitoring systems.";
      }
    }
    
    // General monitoring
    else if (lowerQuery.includes('monitor') || lowerQuery.includes('test') || lowerQuery.includes('measure')) {
      return "Environmental monitoring can focus on soil or water parameters. Soil monitoring includes pH, moisture, and nutrients. Water monitoring covers quality, contamination, and physical properties. What specific aspect would you like to explore?";
    }
    
    // Default response
    else {
      return "I'm here to help with soil and water monitoring! You can ask about:\n• Soil pH, moisture, and nutrient analysis\n• Water quality assessment and contamination detection\n• Monitoring protocols and data interpretation\n• Environmental recommendations and best practices\n\nWhat would you like to know?";
    }
  };

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const userMessage = {
        id: Date.now().toString(),
        text: inputMessage,
        isUser: true,
        timestamp: new Date().toLocaleTimeString()
      };
      
      const response = generateResponse(inputMessage);
      const botMessage = {
        id: (Date.now() + 1).toString(),
        text: response,
        isUser: false,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, userMessage, botMessage]);
      setInputMessage('');
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
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center shadow-md">
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

        {/* Chat Area */}
        <div className="flex-1 flex flex-col p-8">
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
                          disabled={!inputMessage.trim()}
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
            // Chat messages display
            <div className="flex-1 flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-3xl px-4 py-3 rounded-xl ${
                      message.isUser 
                        ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg' 
                        : 'bg-white/80 backdrop-blur-sm text-slate-800 border border-slate-200 shadow-md'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.text}</p>
                      <p className={`text-xs mt-1 ${message.isUser ? 'text-emerald-100' : 'text-slate-500'}`}>
                        {message.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Input Area for chat mode */}
              <div className="border-t border-slate-200 pt-4">
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Ask about soil or water monitoring..."
                      className="w-full resize-none border border-slate-300 rounded-xl p-3 bg-white/80 backdrop-blur-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 max-h-32 shadow-sm"
                      rows={1}
                    />
                  </div>
                  <button 
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim()}
                    className="p-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                    aria-label="Send message"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;