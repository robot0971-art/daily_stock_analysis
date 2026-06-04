import apiClient from './index';
import { API_BASE_URL } from '../utils/constants';
import { createApiError, isApiRequestError, parseApiError } from './error';

export interface ChatStreamOptions {
  signal?: AbortSignal;
}

export interface ChatRequest {
  message: string;
  skills?: string[];
}

export interface ChatStreamRequest extends ChatRequest {
  session_id?: string;
  context?: unknown;
}

export interface ChatResponse {
  success: boolean;
  content: string;
  session_id: string;
  error?: string;
}

export interface SkillInfo {
  id: string;
  name: string;
  description: string;
}

export interface SkillsResponse {
  skills: SkillInfo[];
  default_skill_id: string;
}

const LOCALIZED_SKILLS: Record<string, Pick<SkillInfo, 'name' | 'description'>> = {
  bull_trend: {
    name: '기본 상승 추세',
    description: '상승 추세 지속 여부와 눌림 매수 기회를 함께 확인합니다.',
  },
  ma_golden_cross: {
    name: '이동평균 골든크로스',
    description: '이동평균선 교차와 거래량 확인 신호로 추세 전환 가능성을 봅니다.',
  },
  volume_breakout: {
    name: '거래량 돌파',
    description: '거래량을 동반한 저항 돌파가 실제 매수세인지 확인합니다.',
  },
  hot_theme: {
    name: '테마/정책 모멘텀',
    description: '정책, 산업, 시장 관심 테마의 강도와 확산 여부를 봅니다.',
  },
  shrink_pullback: {
    name: '거래량 감소 눌림목',
    description: '상승 추세 중 거래량이 줄어든 조정 구간의 재진입 가능성을 확인합니다.',
  },
  event_driven: {
    name: '이벤트 드리븐',
    description: '실적, 정책, 인수합병, 수주, 제품 출시 같은 촉매의 영향과 리스크를 평가합니다.',
  },
  box_oscillation: {
    name: '박스권 매매',
    description: '가격 박스권의 하단 매수와 상단 부담 구간을 구분합니다.',
  },
  growth_quality: {
    name: '성장 품질',
    description: '매출, 이익, ROE, 현금흐름, 산업 공간을 함께 보며 성장의 질을 평가합니다.',
  },
  bottom_volume: {
    name: '바닥 거래량 증가',
    description: '장기 하락 이후 바닥권 거래량 증가가 반전 신호인지 확인합니다.',
  },
  expectation_repricing: {
    name: '기대 재평가',
    description: '실적과 정책 기대, 밸류에이션 기대 변화로 재평가 가능성과 과열 리스크를 봅니다.',
  },
  chan_theory: {
    name: 'Chan 이론',
    description: '획, 선분, 중심 구조를 기준으로 추세 단계와 매매 지점을 봅니다.',
  },
  wave_theory: {
    name: '파동 이론',
    description: '상승 파동과 조정 파동 구조로 현재 위치와 잠재 목표가를 추정합니다.',
  },
  dragon_head: {
    name: '주도주 전략',
    description: '업종 순환 속에서 가장 강한 주도주와 후발주의 차이를 구분합니다.',
  },
  emotion_cycle: {
    name: '투자 심리 사이클',
    description: '시장 심리, 회전율, 거래량 구조로 공포와 과열 구간을 판단합니다.',
  },
  one_yang_three_yin: {
    name: '양봉 후 조정 패턴',
    description: '강한 양봉 이후 짧은 조정 패턴이 추세 지속 신호인지 확인합니다.',
  },
};

function localizeSkillInfo(skill: SkillInfo): SkillInfo {
  const localized = LOCALIZED_SKILLS[skill.id];
  return localized ? { ...skill, ...localized } : skill;
}

export interface ChatSessionItem {
  session_id: string;
  title: string;
  message_count: number;
  created_at: string | null;
  last_active: string | null;
}

export interface ChatSessionMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string | null;
}

export const agentApi = {
  async chat(payload: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/api/v1/agent/chat', payload, {
      timeout: 120000,
    });
    return response.data;
  },
  async getSkills(): Promise<SkillsResponse> {
    const response = await apiClient.get<SkillsResponse>('/api/v1/agent/skills');
    return {
      ...response.data,
      skills: response.data.skills.map(localizeSkillInfo),
    };
  },
  async getChatSessions(limit = 50): Promise<ChatSessionItem[]> {
    const response = await apiClient.get<{ sessions: ChatSessionItem[] }>('/api/v1/agent/chat/sessions', { params: { limit } });
    return response.data.sessions;
  },
  async getChatSessionMessages(sessionId: string): Promise<ChatSessionMessage[]> {
    const response = await apiClient.get<{ messages: ChatSessionMessage[] }>(`/api/v1/agent/chat/sessions/${sessionId}`);
    return response.data.messages;
  },
  async deleteChatSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/api/v1/agent/chat/sessions/${sessionId}`);
  },
  async sendChat(content: string): Promise<{ success: boolean }> {
    const response = await apiClient.post<{
      success: boolean;
      error?: string;
      message?: string;
    }>('/api/v1/agent/chat/send', { content });
    const data = response.data;
    if (data.success === false) {
      throw new Error(data.message || '전송 실패');
    }
    return { success: true };
  },
  async chatStream(
    payload: ChatStreamRequest,
    options?: ChatStreamOptions,
  ): Promise<Response> {
    const base = API_BASE_URL || '';
    const url = `${base}/api/v1/agent/chat/stream`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include',
        signal: options?.signal,
      });

      if (response.ok) {
        return response;
      }

      const contentType = response.headers.get('content-type') || '';
      let responseData: unknown = null;
      if (contentType.includes('application/json')) {
        responseData = await response.json().catch(() => null);
      } else {
        responseData = await response.text().catch(() => null);
      }

      const parsed = parseApiError({
        response: {
          status: response.status,
          statusText: response.statusText,
          data: responseData,
        },
      });
      throw createApiError(parsed, {
        response: {
          status: response.status,
          statusText: response.statusText,
          data: responseData,
        },
      });
    } catch (error: unknown) {
      if (isApiRequestError(error)) {
        throw error;
      }
      if (error instanceof Error && error.name === 'AbortError') {
        throw error;
      }

      const parsed = parseApiError(error);
      throw createApiError(parsed, { cause: error });
    }
  },
};
