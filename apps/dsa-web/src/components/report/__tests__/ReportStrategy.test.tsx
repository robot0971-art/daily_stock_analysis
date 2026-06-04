import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ReportStrategy } from '../ReportStrategy';

describe('ReportStrategy', () => {
  it('renders US stock strategy prices as dollars', () => {
    render(
      <ReportStrategy
        stockCode="AAPL"
        language="ko"
        strategy={{
          idealBuy: '210원 부근 지지 확인 시 소량 진입',
          secondaryBuy: 'MA20(218.88) 회복 시 추가 진입',
          stopLoss: '보유 시 210원 이탈 지속 시 축소',
          takeProfit: 'MA5 회복 시 1차 목표',
        }}
      />,
    );

    expect(screen.getByText(/210달러 부근/)).toBeInTheDocument();
    expect(screen.getByText(/210달러 이탈/)).toBeInTheDocument();
    expect(screen.queryByText(/210원/)).not.toBeInTheDocument();
  });

  it('keeps Korean stock strategy prices as won', () => {
    render(
      <ReportStrategy
        stockCode="005930.KS"
        language="ko"
        strategy={{
          idealBuy: '71000원 부근 지지 확인',
        }}
      />,
    );

    expect(screen.getByText(/71000원/)).toBeInTheDocument();
  });
});
