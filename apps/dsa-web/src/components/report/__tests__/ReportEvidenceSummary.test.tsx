import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { RunDiagnosticSummary } from '../../../types/analysis';
import { ReportEvidenceSummary } from '../ReportEvidenceSummary';

const diagnosticSummary: RunDiagnosticSummary = {
  traceId: 'trace-1',
  taskId: 'task-1',
  queryId: 'query-1',
  stockCode: 'AAPL',
  status: 'normal',
  statusLabel: '정상',
  reason: '정상',
  copyText: 'diagnostics',
  components: {
    realtime_quote: {
      key: 'realtime_quote',
      label: '실시간 시세',
      status: 'ok',
      message: 'YfinanceFetcher 성공',
      details: {
        provider: 'YfinanceFetcher',
        record_count: 1,
      },
    },
    daily_data: {
      key: 'daily_data',
      label: '일봉 데이터',
      status: 'degraded',
      message: '보조 경로로 계속 진행',
      details: {
        provider: 'YfinanceFetcher',
        record_count: 30,
      },
    },
    news: {
      key: 'news',
      label: '뉴스 검색',
      status: 'ok',
      message: '뉴스 검색 결과 3건',
      details: {
        record_count: 3,
      },
    },
  },
};

describe('ReportEvidenceSummary', () => {
  it('renders source evidence for quote, daily data, news, and filings', () => {
    render(
      <ReportEvidenceSummary
        diagnosticSummary={diagnosticSummary}
        details={{
          contextSnapshot: {
            news_result_count: 3,
          },
          financialReport: {
            revenue: 100,
          },
        }}
        language="ko"
      />,
    );

    expect(screen.getByText('분석에 사용된 데이터')).toBeInTheDocument();
    expect(screen.getByText('실시간 시세')).toBeInTheDocument();
    expect(screen.getAllByText('YfinanceFetcher')).toHaveLength(2);
    expect(screen.getByText(/현재가 출처: YfinanceFetcher/)).toBeInTheDocument();
    expect(screen.getByText('일봉 데이터')).toBeInTheDocument();
    expect(screen.getByText(/일봉 30건/)).toBeInTheDocument();
    expect(screen.getByText('뉴스 검색')).toBeInTheDocument();
    expect(screen.getByText(/뉴스 3건/)).toBeInTheDocument();
    expect(screen.getByText('공시/재무')).toBeInTheDocument();
    expect(screen.getAllByText('사용됨').length).toBeGreaterThanOrEqual(3);
    expect(screen.getByText('대체 경로')).toBeInTheDocument();
  });

  it('shows missing evidence when source data is absent', () => {
    render(<ReportEvidenceSummary diagnosticSummary={diagnosticSummary} details={{}} language="ko" />);

    expect(screen.getByText('공시/재무')).toBeInTheDocument();
    expect(screen.getByText('재무 또는 공시 근거가 첨부되지 않았습니다.')).toBeInTheDocument();
    expect(screen.getByText('확인 필요')).toBeInTheDocument();
  });
});
