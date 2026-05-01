import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, ChevronDown, ChevronRight, Code } from 'lucide-react';
import { api } from '../../services/api';
import type { HCP, Material, FollowUp } from '../../types';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { setHCP, setSessionId as setSessionIdAction, loadSessionEntities, updateFormField, addMaterial } from '../interactions/interactionsSlice';
import { addSuggestion } from '../followUps/followUpsSlice';
import { addUserMessage, addAssistantMessage, setLoading, setSessionId as setChatSessionId } from './chatSlice';

export function ChatPlaceholder() {
  const dispatch = useAppDispatch();
  const { messages, loading, sessionId: chatSessionId } = useAppSelector((state) => state.chat);
  const [input, setInput] = useState('');
  const [expandedLogs, setExpandedLogs] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleLog = (idx: number) => {
    setExpandedLogs((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userInput = input;
    dispatch(addUserMessage(userInput));
    setInput('');
    dispatch(setLoading(true));

    try {
      const response = await api.chat(userInput, chatSessionId || undefined);

      if (!chatSessionId && response.session_id) {
        dispatch(setChatSessionId(response.session_id));
        sessionStorage.setItem('sessionId', response.session_id);
        dispatch(setSessionIdAction(response.session_id));
        await dispatch(loadSessionEntities(response.session_id));
      }

      const entitiesSet: { field: string; value: string }[] = [];
      const materialsAdded: string[] = [];
      const suggestionsAdded: string[] = [];

      if (response.interaction) {
        const d = response.interaction;

        if (d.hcpId || d.hcp_id) {
          const hcpObj: HCP = {
            id: d.hcpId || d.hcp_id || '',
            name: d.hcpName || d.hcp_name || '',
            specialty: d.hcpSpecialty || d.hcp_specialty || '',
            institution: d.hcpInstitution || d.hcp_institution || '',
          };
          dispatch(setHCP(hcpObj));
          entitiesSet.push({ field: 'hcp', value: hcpObj.name });
        }

        if (d.dateTime || d.date_time) {
          const val = d.dateTime || d.date_time || '';
          dispatch(updateFormField({ field: 'dateTime', value: val }));
          entitiesSet.push({ field: 'dateTime', value: val });
        }

        if (d.type) {
          dispatch(updateFormField({ field: 'type', value: d.type }));
          entitiesSet.push({ field: 'type', value: d.type });
        }

        if (d.topics) {
          const val = Array.isArray(d.topics)
            ? d.topics.filter(Boolean).join(', ')
            : typeof d.topics === 'string'
              ? d.topics
              : '';
          if (val) {
            dispatch(updateFormField({ field: 'topics', value: val }));
            entitiesSet.push({ field: 'topics', value: val });
          }
        }

        if (d.attendees && Array.isArray(d.attendees)) {
          dispatch(updateFormField({ field: 'attendees', value: d.attendees }));
          entitiesSet.push({ field: 'attendees', value: d.attendees.join(', ') });
        }

        if (d.sentiment) {
          dispatch(updateFormField({ field: 'sentiment', value: d.sentiment }));
          entitiesSet.push({ field: 'sentiment', value: d.sentiment });
        }

        if (d.outcome) {
          dispatch(updateFormField({ field: 'outcome', value: d.outcome }));
          entitiesSet.push({ field: 'outcome', value: d.outcome });
        }

        if (d.notes) {
          dispatch(updateFormField({ field: 'notes', value: d.notes }));
          entitiesSet.push({ field: 'notes', value: d.notes });
        }

        if (d.materials && Array.isArray(d.materials)) {
          for (const mat of d.materials) {
            if (mat && typeof mat === 'string' && mat.trim()) {
              const material: Material = {
                id: `mat-${crypto.randomUUID()}`,
                name: mat,
                type: 'pdf',
                createdAt: new Date().toISOString(),
              };
              dispatch(addMaterial(material));
              materialsAdded.push(mat);
            } else if (mat && typeof mat === 'object' && mat.id) {
              const material: Material = {
                id: mat.id,
                name: mat.name,
                type: (mat.type as Material['type']) || 'pdf',
                description: mat.description,
                createdAt: new Date().toISOString(),
              };
              dispatch(addMaterial(material));
              materialsAdded.push(mat.name);
            }
          }
        }
      }

      if (response.aiSuggestions && Array.isArray(response.aiSuggestions)) {
        for (const suggestion of response.aiSuggestions) {
          if (suggestion && suggestion.description) {
            const dueDate = suggestion.dueDate
              ? suggestion.dueDate
              : suggestion.dueInDays
                ? new Date(Date.now() + suggestion.dueInDays * 86400000).toISOString()
                : undefined;

            const typeMap: Record<string, FollowUp['type']> = {
              call: 'call',
              meeting: 'follow_up_meeting',
              email: 'other',
              sendMaterial: 'send_material',
              send_material: 'send_material',
              sampleRequest: 'sample_request',
              sample_request: 'sample_request',
            };

            const followUp: FollowUp = {
              id: suggestion.id || crypto.randomUUID(),
              interactionId: suggestion.interactionId || suggestion.interaction_id,
              description: suggestion.description,
              type: typeMap[suggestion.type || ''] || 'other',
              status: 'pending',
              aiGenerated: true,
              dueDate,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            };
            dispatch(addSuggestion(followUp));
            suggestionsAdded.push(suggestion.description);
          }
        }
      }

      dispatch(addAssistantMessage({
        role: 'assistant',
        content: response.message,
        responseLog: { intent: response.intent || '', entitiesSet, materialsAdded, suggestionsAdded },
      }));
    } catch (error) {
      dispatch(addAssistantMessage({
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
      }));
    } finally {
      dispatch(setLoading(false));
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
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className="max-w-[80%]">
                <div
                  className={`rounded-lg px-3 py-2 text-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  {msg.content}
                </div>
                {'responseLog' in msg && msg.responseLog && (
                  <button
                    onClick={() => toggleLog(idx)}
                    className="mt-1 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                  >
                    {expandedLogs.has(idx) ? (
                      <ChevronDown className="h-3 w-3" />
                    ) : (
                      <ChevronRight className="h-3 w-3" />
                    )}
                    <Code className="h-3 w-3" />
                    Response log
                  </button>
                )}
                {'responseLog' in msg && msg.responseLog && expandedLogs.has(idx) && (() => {
                  const log = msg.responseLog!;
                  return (
                    <div className="mt-1 rounded-md border bg-background p-2 font-mono text-xs space-y-1">
                      <div><span className="text-muted-foreground">Intent:</span> {log.intent}</div>
                      {log.entitiesSet.length > 0 && (
                        <div>
                          <span className="text-muted-foreground">Entities set:</span>
                          {log.entitiesSet.map((e: { field: string; value: string }, i: number) => (
                            <span key={i}> {e.field}="{e.value}"{i < log.entitiesSet.length - 1 ? ',' : ''}</span>
                          ))}
                        </div>
                      )}
                      {log.materialsAdded.length > 0 && (
                        <div><span className="text-muted-foreground">Materials:</span> [{log.materialsAdded.map((m: string) => `"${m}"`).join(', ')}]</div>
                      )}
                      {log.suggestionsAdded.length > 0 && (
                        <div>
                          <span className="text-muted-foreground">Suggestions:</span>
                          {log.suggestionsAdded.map((s: string, i: number) => (
                            <div key={i} className="ml-2 text-[10px] text-primary">• {s}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })()}
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
