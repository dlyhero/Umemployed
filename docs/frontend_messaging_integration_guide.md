# Frontend Integration Guide: Messaging System

## Overview
Complete frontend integration guide for the UmEmployed messaging system with enhanced features including reactions, read status, and real-time updates.

---

## 🏗️ TypeScript Interfaces

```typescript
// types/messaging.ts

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface Conversation {
  id: number;
  participant1: number;
  participant2: number;
  participant1_username: string;
  participant2_username: string;
  created_at: string;
  unread_count?: number; // Calculated on frontend
  last_message?: ChatMessage; // Calculated on frontend
}

export interface MessageReaction {
  id: number;
  user: number;
  username: string;
  reaction: 'like' | 'love' | 'laugh' | 'wow' | 'sad' | 'angry';
}

export interface ChatMessage {
  id: number;
  conversation: number;
  sender: number;
  sender_username: string;
  text: string;
  timestamp: string;
  is_read: boolean;
  reactions: MessageReaction[];
}

export interface ConversationState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
}
```

---

## 🔌 API Service Layer

```typescript
// services/messagingService.ts
import { ApiClient } from './apiClient';

export class MessagingService extends ApiClient {
  private baseURL = '/api/messages';

  // Conversation Management
  async getConversations(): Promise<Conversation[]> {
    const response = await this.get(`${this.baseURL}/conversations/`);
    return response.map(this.enhanceConversation);
  }

  async startConversation(userId: number): Promise<{ conversation_id: number }> {
    return this.post(`${this.baseURL}/conversations/start/`, { user_id: userId });
  }

  async deleteConversation(conversationId: number): Promise<void> {
    return this.delete(`${this.baseURL}/conversations/${conversationId}/delete/`);
  }

  async searchConversations(query: string): Promise<Conversation[]> {
    const response = await this.get(`${this.baseURL}/search-inbox/?query=${encodeURIComponent(query)}`);
    return response.map(this.enhanceConversation);
  }

  // Message Management
  async getMessages(conversationId: number): Promise<ChatMessage[]> {
    return this.get(`${this.baseURL}/conversations/${conversationId}/messages/`);
  }

  async sendMessage(conversationId: number, text: string): Promise<ChatMessage> {
    return this.post(`${this.baseURL}/conversations/${conversationId}/messages/`, { text });
  }

  async updateMessage(messageId: number, text: string): Promise<ChatMessage> {
    return this.put(`${this.baseURL}/messages/${messageId}/update/`, { text });
  }

  async deleteMessage(messageId: number): Promise<void> {
    return this.delete(`${this.baseURL}/messages/${messageId}/delete/`);
  }

  async bulkDeleteMessages(conversationId: number, messageIds: number[]): Promise<void> {
    return this.post(`${this.baseURL}/conversations/${conversationId}/bulk-delete/`, { 
      message_ids: messageIds 
    });
  }

  async markMessagesAsRead(conversationId: number): Promise<void> {
    return this.post(`${this.baseURL}/conversations/${conversationId}/mark-read/`);
  }

  // Reactions
  async addReaction(messageId: number, reaction: string): Promise<void> {
    return this.post(`${this.baseURL}/messages/${messageId}/reactions/`, { reaction });
  }

  async removeReaction(messageId: number, reaction: string): Promise<void> {
    return this.delete(`${this.baseURL}/messages/${messageId}/reactions/`, { reaction });
  }

  // Helper method to enhance conversation data
  private enhanceConversation(conversation: any): Conversation {
    return {
      ...conversation,
      unread_count: 0, // Will be calculated
      last_message: null // Will be set from messages
    };
  }
}
```

---

## 🗄️ Redux Store Setup

```typescript
// store/messagingSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { MessagingService } from '../services/messagingService';

const messagingService = new MessagingService();

// Async Thunks
export const fetchConversations = createAsyncThunk(
  'messaging/fetchConversations',
  async () => {
    return await messagingService.getConversations();
  }
);

export const fetchMessages = createAsyncThunk(
  'messaging/fetchMessages',
  async (conversationId: number) => {
    return await messagingService.getMessages(conversationId);
  }
);

export const sendMessage = createAsyncThunk(
  'messaging/sendMessage',
  async ({ conversationId, text }: { conversationId: number; text: string }) => {
    return await messagingService.sendMessage(conversationId, text);
  }
);

export const startConversation = createAsyncThunk(
  'messaging/startConversation',
  async (userId: number) => {
    const result = await messagingService.startConversation(userId);
    // Fetch the conversation details
    const conversations = await messagingService.getConversations();
    return conversations.find(c => c.id === result.conversation_id);
  }
);

// Slice
const messagingSlice = createSlice({
  name: 'messaging',
  initialState: {
    conversations: [],
    currentConversation: null,
    messages: [],
    loading: false,
    error: null,
    selectedMessages: [], // For bulk operations
  } as ConversationState & { selectedMessages: number[] },
  reducers: {
    setCurrentConversation: (state, action: PayloadAction<Conversation | null>) => {
      state.currentConversation = action.payload;
      if (action.payload) {
        // Mark as read when opening conversation
        messagingService.markMessagesAsRead(action.payload.id);
      }
    },
    addMessageReaction: (state, action: PayloadAction<{ messageId: number; reaction: MessageReaction }>) => {
      const message = state.messages.find(m => m.id === action.payload.messageId);
      if (message) {
        // Remove existing reaction from same user first
        message.reactions = message.reactions.filter(r => r.user !== action.payload.reaction.user);
        message.reactions.push(action.payload.reaction);
      }
    },
    removeMessageReaction: (state, action: PayloadAction<{ messageId: number; userId: number; reaction: string }>) => {
      const message = state.messages.find(m => m.id === action.payload.messageId);
      if (message) {
        message.reactions = message.reactions.filter(
          r => !(r.user === action.payload.userId && r.reaction === action.payload.reaction)
        );
      }
    },
    toggleMessageSelection: (state, action: PayloadAction<number>) => {
      const messageId = action.payload;
      if (state.selectedMessages.includes(messageId)) {
        state.selectedMessages = state.selectedMessages.filter(id => id !== messageId);
      } else {
        state.selectedMessages.push(messageId);
      }
    },
    clearSelectedMessages: (state) => {
      state.selectedMessages = [];
    },
    updateMessageOptimistic: (state, action: PayloadAction<{ messageId: number; text: string }>) => {
      const message = state.messages.find(m => m.id === action.payload.messageId);
      if (message) {
        message.text = action.payload.text;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.conversations = action.payload;
        state.loading = false;
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        state.messages = action.payload;
        state.loading = false;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.messages.push(action.payload);
      });
  }
});

export const { 
  setCurrentConversation, 
  addMessageReaction, 
  removeMessageReaction,
  toggleMessageSelection,
  clearSelectedMessages,
  updateMessageOptimistic
} = messagingSlice.actions;

export default messagingSlice.reducer;
```

---

## 🎨 React Components

### Main Messaging Component

```typescript
// components/Messaging/MessagingContainer.tsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { ConversationList } from './ConversationList';
import { ChatWindow } from './ChatWindow';
import { fetchConversations } from '../../store/messagingSlice';

export const MessagingContainer: React.FC = () => {
  const dispatch = useDispatch();
  const { conversations, currentConversation } = useSelector(state => state.messaging);

  useEffect(() => {
    dispatch(fetchConversations());
  }, [dispatch]);

  return (
    <div className="messaging-container flex h-full">
      <div className="w-1/3 border-r">
        <ConversationList conversations={conversations} />
      </div>
      <div className="w-2/3">
        {currentConversation ? (
          <ChatWindow conversation={currentConversation} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select a conversation to start messaging
          </div>
        )}
      </div>
    </div>
  );
};
```

### Conversation List Component

```typescript
// components/Messaging/ConversationList.tsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { setCurrentConversation, fetchMessages } from '../../store/messagingSlice';
import { Conversation } from '../../types/messaging';

interface Props {
  conversations: Conversation[];
}

export const ConversationList: React.FC<Props> = ({ conversations }) => {
  const dispatch = useDispatch();
  const [searchQuery, setSearchQuery] = useState('');

  const handleConversationClick = async (conversation: Conversation) => {
    dispatch(setCurrentConversation(conversation));
    dispatch(fetchMessages(conversation.id));
  };

  const filteredConversations = conversations.filter(conv =>
    conv.participant1_username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.participant2_username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {filteredConversations.map(conversation => (
          <div
            key={conversation.id}
            onClick={() => handleConversationClick(conversation)}
            className="p-4 border-b hover:bg-gray-50 cursor-pointer"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium">
                  {conversation.participant1_username} ↔ {conversation.participant2_username}
                </h3>
                {conversation.last_message && (
                  <p className="text-sm text-gray-600 truncate">
                    {conversation.last_message.text}
                  </p>
                )}
              </div>
              {conversation.unread_count > 0 && (
                <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-1">
                  {conversation.unread_count}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Chat Window Component

```typescript
// components/Messaging/ChatWindow.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage } from '../../store/messagingSlice';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { BulkActionBar } from './BulkActionBar';

interface Props {
  conversation: Conversation;
}

export const ChatWindow: React.FC<Props> = ({ conversation }) => {
  const dispatch = useDispatch();
  const { messages, selectedMessages } = useSelector(state => state.messaging);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    if (text.trim()) {
      dispatch(sendMessage({ conversationId: conversation.id, text }));
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-white">
        <h2 className="font-semibold">
          {conversation.participant1_username} ↔ {conversation.participant2_username}
        </h2>
      </div>

      {/* Bulk Action Bar */}
      {selectedMessages.length > 0 && (
        <BulkActionBar 
          selectedCount={selectedMessages.length}
          conversationId={conversation.id}
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map(message => (
          <MessageBubble
            key={message.id}
            message={message}
            isSelected={selectedMessages.includes(message.id)}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};
```

### Message Bubble Component

```typescript
// components/Messaging/MessageBubble.tsx
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { toggleMessageSelection, addMessageReaction, removeMessageReaction } from '../../store/messagingSlice';
import { ChatMessage } from '../../types/messaging';
import { ReactionPicker } from './ReactionPicker';
import { MessageReactions } from './MessageReactions';

interface Props {
  message: ChatMessage;
  isSelected: boolean;
}

export const MessageBubble: React.FC<Props> = ({ message, isSelected }) => {
  const dispatch = useDispatch();
  const { user } = useSelector(state => state.auth);
  const [showReactionPicker, setShowReactionPicker] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const isOwnMessage = message.sender === user?.id;

  const handleReaction = async (reaction: string) => {
    // Check if user already has this reaction
    const existingReaction = message.reactions.find(r => r.user === user?.id && r.reaction === reaction);
    
    if (existingReaction) {
      dispatch(removeMessageReaction({ messageId: message.id, userId: user.id, reaction }));
      await messagingService.removeReaction(message.id, reaction);
    } else {
      const newReaction = { id: Date.now(), user: user.id, username: user.username, reaction };
      dispatch(addMessageReaction({ messageId: message.id, reaction: newReaction }));
      await messagingService.addReaction(message.id, reaction);
    }
    setShowReactionPicker(false);
  };

  return (
    <div className={`mb-4 flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg relative ${
        isOwnMessage ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'
      } ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
      onClick={() => dispatch(toggleMessageSelection(message.id))}
      >
        {/* Message Content */}
        <div className="flex justify-between items-start mb-1">
          <span className="text-xs opacity-75">{message.sender_username}</span>
          <span className="text-xs opacity-75 ml-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        
        <p className="text-sm">{message.text}</p>

        {/* Read Status */}
        {isOwnMessage && (
          <div className="text-xs opacity-75 mt-1">
            {message.is_read ? '✓✓' : '✓'}
          </div>
        )}

        {/* Reactions */}
        <MessageReactions reactions={message.reactions} />

        {/* Action Buttons */}
        <div className="absolute -bottom-8 right-0 flex space-x-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowReactionPicker(!showReactionPicker);
            }}
            className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded"
          >
            😊
          </button>
          {isOwnMessage && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
              className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded"
            >
              ✏️
            </button>
          )}
        </div>

        {/* Reaction Picker */}
        {showReactionPicker && (
          <ReactionPicker
            onSelectReaction={handleReaction}
            onClose={() => setShowReactionPicker(false)}
          />
        )}
      </div>
    </div>
  );
};
```

---

## 🔄 Real-time Updates with WebSocket

```typescript
// hooks/useWebSocketMessaging.ts
import { useEffect, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { addMessage, updateMessageReaction } from '../store/messagingSlice';

export const useWebSocketMessaging = (conversationId: number | null) => {
  const dispatch = useDispatch();

  useEffect(() => {
    if (!conversationId) return;

    const wsUrl = `ws://localhost:8000/ws/chat/${conversationId}/`;
    const websocket = new WebSocket(wsUrl);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'chat_message':
          dispatch(addMessage(data.message));
          break;
        case 'message_reaction':
          dispatch(updateMessageReaction(data));
          break;
        case 'message_read':
          // Update read status for messages
          break;
      }
    };

    return () => {
      websocket.close();
    };
  }, [conversationId, dispatch]);
};
```

---

## 📱 Mobile-Responsive Design

```css
/* styles/messaging.css */

.messaging-container {
  height: 100vh;
  display: flex;
}

@media (max-width: 768px) {
  .messaging-container {
    flex-direction: column;
  }
  
  .conversation-list {
    height: 40vh;
  }
  
  .chat-window {
    height: 60vh;
  }
}

.message-bubble {
  max-width: 70%;
  word-wrap: break-word;
}

.reaction-picker {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.bulk-action-bar {
  background: #f3f4f6;
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}
```

---

## 🚀 Performance Optimizations

### 1. Message Virtualization
```typescript
// For large message lists, use react-window
import { FixedSizeList as List } from 'react-window';

const VirtualizedMessageList: React.FC = ({ messages }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <MessageBubble message={messages[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={messages.length}
      itemSize={100}
    >
      {Row}
    </List>
  );
};
```

### 2. Optimistic Updates
```typescript
const handleSendMessage = async (text: string) => {
  // Add message optimistically
  const tempMessage = {
    id: Date.now(), // Temporary ID
    text,
    sender: user.id,
    timestamp: new Date().toISOString(),
    // ... other fields
  };
  
  dispatch(addMessage(tempMessage));
  
  try {
    const realMessage = await messagingService.sendMessage(conversationId, text);
    dispatch(updateMessage({ tempId: tempMessage.id, message: realMessage }));
  } catch (error) {
    dispatch(removeMessage(tempMessage.id));
    // Show error message
  }
};
```

### 3. Caching Strategy
```typescript
// Use React Query for intelligent caching
import { useQuery, useMutation, useQueryClient } from 'react-query';

const useMessages = (conversationId: number) => {
  return useQuery(
    ['messages', conversationId],
    () => messagingService.getMessages(conversationId),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );
};
```

---

## 🔧 Error Handling & UX

```typescript
// Error boundary for messaging components
class MessagingErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 text-center">
          <h3>Something went wrong with the messaging system.</h3>
          <button 
            onClick={() => this.setState({ hasError: false })}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Network status indicator
const NetworkStatus: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOnline) {
    return (
      <div className="bg-red-500 text-white p-2 text-center text-sm">
        You're offline. Messages will be sent when connection is restored.
      </div>
    );
  }

  return null;
};
```

This comprehensive frontend guide provides everything needed to integrate the enhanced messaging system with proper error handling, real-time updates, and a great user experience!
