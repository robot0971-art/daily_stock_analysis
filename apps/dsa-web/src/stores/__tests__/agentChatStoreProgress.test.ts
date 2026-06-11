import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAgentChatStore } from '../agentChatStore';

vi.mock('../../api/agent', () => ({
  agentApi: {
    getChatSessions: vi.fn(async () => []),
    getChatSessionMessages: vi.fn(async () => []),
    chatStream: vi.fn(),
  },
}));

const { agentApi } = await import('../../api/agent');
const encoder = new TextEncoder();

function createStreamResponse(lines: string[]) {
  return new Response(
    new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(lines.join('\n')));
        controller.close();
      },
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
    },
  );
}

beforeEach(() => {
  localStorage.clear();
  useAgentChatStore.setState({
    messages: [],
    loading: false,
    progressSteps: [],
    sessionId: 'session-test',
    sessions: [],
    sessionsLoading: false,
    chatError: null,
    currentRoute: '/chat',
    completionBadge: false,
    hasInitialLoad: true,
    abortController: null,
  });
  vi.clearAllMocks();
});

describe('agentChatStore progress and content normalization', () => {
  it('normalizes legacy Chinese stream progress messages before rendering', async () => {
    vi.mocked(agentApi.chatStream).mockResolvedValue(
      createStreamResponse([
        'data: {"type":"thinking","step":1,"message":"\\u6b63\\u5728\\u5236\\u5b9a\\u5206\\u6790\\u8def\\u5f84..."}',
        'data: {"type":"generating","step":2,"message":"\\u6b63\\u5728\\u751f\\u6210\\u6700\\u7ec8\\u5206\\u6790..."}',
        'data: {"type":"done","success":true,"content":"done"}',
      ]),
    );

    await useAgentChatStore
      .getState()
      .startStream({ message: 'status', session_id: 'session-test' }, { skillName: 'default' });

    const steps = useAgentChatStore.getState().messages[1].thinkingSteps || [];
    expect(steps.map((step) => step.message)).toEqual([
      '\ubd84\uc11d \uacbd\ub85c\ub97c \uc815\ud558\ub294 \uc911...',
      '\ucd5c\uc885 \ub2f5\ubcc0\uc744 \uc791\uc131\ud558\ub294 \uc911...',
    ]);
  });

  it('normalizes common Chinese fragments in completed assistant content', async () => {
    vi.mocked(agentApi.chatStream).mockResolvedValue(
      createStreamResponse([
        'data: {"type":"done","success":true,"content":"\\u76ee\\u524d \\u97e9\\u56fd \\u5e02\\u573a \\u4e0a\\u6da8, \\u65e5\\u5185 \\u6ce2\\u52a8, \\u591a\\u5934\\u6392\\u5217 \\u89c2\\u671b"}',
      ]),
    );

    await useAgentChatStore
      .getState()
      .startStream({ message: 'status', session_id: 'session-test' }, { skillName: 'default' });

    const content = useAgentChatStore.getState().messages[1].content;
    expect(content).toContain('\ud604\uc7ac');
    expect(content).toContain('\ud55c\uad6d');
    expect(content).toContain('\uc2dc\uc7a5');
    expect(content).toContain('\uc0c1\uc2b9');
    expect(content).toContain('\uc7a5\uc911');
    expect(content).toContain('\ubcc0\ub3d9');
    expect(content).toContain('\uc815\ubc30\uc5f4');
    expect(content).toContain('\uad00\ub9dd');
    expect(content).not.toContain('\u76ee\u524d');
    expect(content).not.toContain('\u5e02\u573a');
    expect(content).not.toContain('\u65e5\u5185');
    expect(content).not.toContain('\u6ce2\u52a8');
    expect(content).not.toContain('\u591a\u5934');
    expect(content).not.toContain('\u89c2\u671b');
  });
});
