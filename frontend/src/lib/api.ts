export interface TopicOverview {
  id: string;
  title: string;
  card_description: string;
  source_url: string;
}

export interface TopicDetail {
  id: string;
  title: string;
  summary: string;
  key_rights: string[];
  penalties: string[];
  card_description: string;
  source_url: string;
}

export interface ChatRequest {
  topic_id: string;
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  topic_id: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchTopics(): Promise<TopicOverview[]> {
  const response = await fetch(`${API_BASE_URL}/api/topics`);
  if (!response.ok) {
    throw new Error(`Failed to fetch topics: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchTopicDetail(topicId: string): Promise<TopicDetail> {
  const response = await fetch(`${API_BASE_URL}/api/topics/${topicId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch topic details: ${response.statusText}`);
  }
  return response.json();
}

export async function sendChatMessage(topicId: string, question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ topic_id: topicId, question }),
  });
  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Our AI query capacity is currently full. Please try again in a few moments.");
    }
    throw new Error(`AI reasoning error: ${response.statusText}`);
  }
  return response.json();
}

export function getAudioUrl(topicId: string): string {
  return `${API_BASE_URL}/api/audio/${topicId}`;
}

export interface StreamChunk {
  type: 'token' | 'sources' | 'error' | 'done';
  token?: string;
  sources?: string[];
  detail?: string;
}

export async function sendChatMessageStream(
  topicId: string,
  question: string,
  onChunk: (chunk: StreamChunk) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ topic_id: topicId, question }),
  });

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Our AI query capacity is currently full. Please try again in a few moments.");
    }
    throw new Error(`AI reasoning error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Failed to open streaming response reader.');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      
      // Keep the last chunk in the buffer if it is incomplete
      buffer = parts.pop() || '';

      for (const part of parts) {
        const line = part.trim();
        if (line.startsWith('data: ')) {
          try {
            const parsed: StreamChunk = JSON.parse(line.slice(6));
            onChunk(parsed);
          } catch (err) {
            console.error('Failed to parse SSE JSON line:', line, err);
          }
        }
      }
    }
  } catch (err) {
    console.error('Error reading chat response stream:', err);
    throw err;
  } finally {
    reader.releaseLock();
  }
}

