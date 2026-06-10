import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TaskPanel } from '../TaskPanel';
import type { TaskInfo } from '../../../types/analysis';

const baseTask: TaskInfo = {
  taskId: 'task-1',
  stockCode: 'KR005930',
  stockName: '삼성전자',
  status: 'processing',
  progress: 40,
  message: '최신 시세를 가져오는 중',
  reportType: 'detailed',
  createdAt: '2026-03-21T08:00:00Z',
  startedAt: '2026-03-21T08:00:00Z',
};

describe('TaskPanel', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders active tasks with preserved dashboard panel styling', () => {
    vi.setSystemTime(new Date('2026-03-21T08:00:12Z'));

    const { container } = render(
      <TaskPanel
        tasks={[
          baseTask,
          {
            ...baseTask,
            taskId: 'task-2',
            stockCode: 'AAPL',
            stockName: 'Apple',
            status: 'pending',
            message: '분석 대기열에서 대기 중',
          },
        ]}
      />,
    );

    expect(screen.getByText('분석 작업')).toBeInTheDocument();
    expect(screen.getByText('1 진행 중')).toBeInTheDocument();
    expect(screen.getByText('1 대기 중')).toBeInTheDocument();
    expect(screen.getByText('삼성전자')).toBeInTheDocument();
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getAllByText('경과 12초')).toHaveLength(2);
    expect(screen.getByLabelText('작업 상태: 분석 중')).toBeInTheDocument();
    expect(container.querySelector('.home-panel-card')).toBeTruthy();
    expect(container.querySelector('.home-subpanel')).toBeTruthy();
  });

  it('displays market review tasks in Korean', () => {
    render(
      <TaskPanel
        tasks={[
          {
            ...baseTask,
            taskId: 'task-market',
            stockCode: 'market_review',
            stockName: '시장 리뷰 원본 이름',
          },
        ]}
      />,
    );

    expect(screen.getByText('시장 리뷰')).toBeInTheDocument();
    expect(screen.queryByText('시장 리뷰 원본 이름')).not.toBeInTheDocument();
  });

  it('shows long-running AI writing guidance during the LLM stage', () => {
    vi.setSystemTime(new Date('2026-03-21T08:01:05Z'));

    render(
      <TaskPanel
        tasks={[
          {
            ...baseTask,
            progress: 68,
            message: 'Apple Inc.: AI가 리포트를 작성하는 중입니다. 복잡한 분석은 몇 분 걸릴 수 있습니다.',
          },
        ]}
      />,
    );

    expect(screen.getByText(/AI가 리포트를 작성하는 중입니다/)).toBeInTheDocument();
    expect(screen.getByText('AI 리포트 작성 단계는 보통 1~2분 걸릴 수 있습니다.')).toBeInTheDocument();
    expect(screen.getByText('경과 1분 05초')).toBeInTheDocument();
  });

  it('does not render when there are no active tasks', () => {
    const { container } = render(
      <TaskPanel
        tasks={[
          {
            ...baseTask,
            status: 'completed',
          },
        ]}
      />,
    );

    expect(container).toBeEmptyDOMElement();
  });
});
