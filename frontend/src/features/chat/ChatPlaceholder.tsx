import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { api } from '../../services/api';
import type { ChatMessage } from '../../types';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { setFormData, setHCP, addMaterial } from '../interactions/interactionsSlice';

export function ChatPlaceholder() {
  const dispatch = useAppDispatch();
  const formData = useAppSelector((state) => state.interactions.formData);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    const currentFormData = Object.fromEntries(
      Object.entries(formData).filter(([_, v]) => v !== undefined && v !== null && v !== '' && (Array.isArray(v) ? v.length > 0 : true))
    );

    try {
      const response = await api.chat(input, sessionId || undefined, undefined, currentFormData);

      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      if (response.interaction) {
        const interactionData = response.interaction;
        
        if (interactionData.hcp_id) {
          try {
            const hcp = await api.getHcp(interactionData.hcp_id);
            dispatch(setHCP(hcp));
          } catch (e) {
            console.error('Failed to fetch HCP details:', e);
            if (interactionData.hcp_name) {
              dispatch(setHCP({
                id: interactionData.hcp_id,
                name: interactionData.hcp_name,
                specialty: interactionData.hcp_specialty,
                institution: interactionData.hcp_institution,
                createdAt: '',
                updatedAt: '',
              } as import('../../types').HCP));
            }
          }
        }
        
        if (interactionData.materials && Array.isArray(interactionData.materials)) {
          for (const materialId of interactionData.materials) {
            try {
              const material = await api.getMaterial(materialId);
              dispatch(addMaterial(material));
            } catch (e) {
              console.error('Failed to fetch material details:', e);
            }
          }
        }
        
        const { hcp_id, materials, ...formFields } = interactionData;
        dispatch(setFormData({
          ...formFields,
          hcpId: interactionData.hcp_id || interactionData.hcpId,
        }));
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full flex-col bg-muted/30">
      <div className="border-b bg-card px-4 py-3">
        <h3 className="font-medium">AI Assistant</h3>
        <p className="text-xs text-muted-foreground">
          Log interactions via natural language
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="rounded-lg border bg-card p-4 text-sm">
            <p className="mb-2 font-medium text-foreground">Try saying:</p>
            <ul className="list-inside list-disc space-y-1 text-muted-foreground">
              <li>"Met Dr. Smith today, discussed OncoBoost efficacy"</li>
              <li>"Schedule a follow-up with Dr. Patel next week"</li>
              <li>"Show recent interactions with Dr. Kumar"</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t bg-card p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="rounded-md bg-primary px-3 py-2 text-primary-foreground disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}