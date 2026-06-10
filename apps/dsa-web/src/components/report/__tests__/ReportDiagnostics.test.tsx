import { StrictMode } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { historyApi } from '../../../api/history';
import type { RunDiagnosticSummary } from '../../../types/analysis';
import { ReportDiagnostics } from '../ReportDiagnostics';

vi.mock('../../../api/history', () => ({
  historyApi: {
    getDiagnostics: vi.fn(),
  },
}));

const diagnosticSummary: RunDiagnosticSummary = {
  traceId: 'trace-1234567890abcdef',
  taskId: 'task-1',
  queryId: 'query-1',
  stockCode: '600519',
  triggerSource: 'web',
  status: 'degraded',
  statusLabel: '部分降级',
  reason: '实时行情 baostock 成功，前置数据源失败后已继续',
  copyText: 'trace_id: trace-1234567890abcdef\nreason: 实时行情 baostock 成功，前置数据源失败后已继续',
  components: {
    realtimeQuote: {
      key: 'realtime_quote',
      label: '实时行情',
      status: 'degraded',
      message: '实时行情 baostock 成功，前置数据源失败后已继续',
      details: {
        provider: 'baostock',
        attempts: 2,
      },
    },
    notification: {
      key: 'notification',
      label: '通知',
      status: 'not_configured',
      message: '通知未配置或本次跳过',
    },
  },
};

describe('ReportDiagnostics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it('loads historical diagnostics in a collapsed panel and copies sanitized text', async () => {
    vi.mocked(historyApi.getDiagnostics).mockResolvedValue(diagnosticSummary);

    render(<ReportDiagnostics recordId={1} />);

    expect(historyApi.getDiagnostics).toHaveBeenCalledWith(1);
    expect(await screen.findByText('데이터 신뢰도')).toBeInTheDocument();
    const panel = screen.getByTestId('run-diagnostics');
    expect(panel).not.toHaveAttribute('open');
    expect(screen.getAllByText('확인 필요').length).toBeGreaterThan(0);

    fireEvent.click(screen.getByText('데이터 신뢰도'));

    expect(panel).toHaveAttribute('open');
    expect(screen.getAllByText('실시간 시세: baostock 성공, 이전 데이터 소스 실패 후 계속 진행했습니다').length)
      .toBeGreaterThan(0);
    expect(screen.getByText('실시간 시세')).toBeInTheDocument();
    expect(screen.getByText('알림')).toBeInTheDocument();
    expect(screen.getByText('미설정')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: '진단 복사' }));

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        'trace_id: trace-1234567890abcdef\nreason: 실시간 시세: baostock 성공, 이전 데이터 소스 실패 후 계속 진행했습니다',
      );
    });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: '복사됨' })).toBeInTheDocument();
    });
  });

  it('uses the provided summary without fetching history diagnostics', () => {
    render(<ReportDiagnostics summary={diagnosticSummary} />);

    expect(historyApi.getDiagnostics).not.toHaveBeenCalled();
    expect(screen.getByText('데이터 신뢰도')).toBeInTheDocument();
    expect(screen.getAllByText('확인 필요').length).toBeGreaterThan(0);
  });

  it('refetches diagnostics after StrictMode cleans up the first effect run', async () => {
    vi.mocked(historyApi.getDiagnostics).mockResolvedValue(diagnosticSummary);

    render(
      <StrictMode>
        <ReportDiagnostics recordId={1} />
      </StrictMode>,
    );

    await waitFor(() => {
      expect(historyApi.getDiagnostics).toHaveBeenCalledTimes(2);
    });
    expect(await screen.findByText('데이터 신뢰도')).toBeInTheDocument();
  });
});
