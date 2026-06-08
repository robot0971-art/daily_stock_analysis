import type React from 'react';
import type { ReportLanguage, ReportStrategy as ReportStrategyType } from '../../types/analysis';
import { Card } from '../common';
import { DashboardPanelHeader } from '../dashboard';
import { getReportText, normalizeReportLanguage } from '../../utils/reportLanguage';
import { localizeLegacyText } from '../../utils/legacyKoreanText';

interface ReportStrategyProps {
  strategy?: ReportStrategyType;
  language?: ReportLanguage;
  stockCode?: string;
}

interface StrategyItemProps {
  label: string;
  value?: string;
  tone: string;
}

const isUsStockCode = (stockCode?: string): boolean => {
  const normalized = (stockCode ?? '').trim().toUpperCase();
  return /^[A-Z]{1,5}(\.[A-Z])?$/.test(normalized) || normalized.endsWith('.US');
};

const formatStrategyValue = (value: string | undefined, stockCode?: string): string => {
  const localized = localizeLegacyText(value);
  if (!localized || !isUsStockCode(stockCode)) {
    return localized;
  }

  return localized
    .replace(/(\d[\d,.]*)\s*원/g, '$1달러')
    .replace(/(\d[\d,.]*)\s*\u97e9\u5143/g, '$1달러')
    .replace(/(\d[\d,.]*)\s*위안/g, '$1달러');
};

const StrategyItem: React.FC<StrategyItemProps> = ({
  label,
  value,
  tone,
}) => (
  <div className="home-subpanel home-strategy-card p-3" style={{ ['--home-strategy-tone' as string]: `var(${tone})` }}>
    <div className="flex flex-col">
      <span className="home-strategy-label mb-0.5 text-xs">{label}</span>
      <span className="home-strategy-value text-lg font-bold font-mono" style={!value ? { color: 'var(--text-muted-text)' } : undefined}>
        {value || '—'}
      </span>
    </div>
    <div
      className="absolute bottom-0 left-0 right-0 h-0.5"
      style={{ background: `linear-gradient(90deg, transparent, var(${tone}), transparent)` }}
    />
  </div>
);

/**
 */
export const ReportStrategy: React.FC<ReportStrategyProps> = ({ strategy, language = 'ko', stockCode }) => {
  if (!strategy) {
    return null;
  }

  const reportLanguage = normalizeReportLanguage(language);
  const text = getReportText(reportLanguage);

  const strategyItems = [
    {
      label: text.idealBuy,
      value: formatStrategyValue(strategy.idealBuy, stockCode),
      tone: '--home-strategy-buy',
    },
    {
      label: text.secondaryBuy,
      value: formatStrategyValue(strategy.secondaryBuy, stockCode),
      tone: '--home-strategy-secondary',
    },
    {
      label: text.stopLoss,
      value: formatStrategyValue(strategy.stopLoss, stockCode),
      tone: '--home-strategy-stop',
    },
    {
      label: text.takeProfit,
      value: formatStrategyValue(strategy.takeProfit, stockCode),
      tone: '--home-strategy-take',
    },
  ];

  return (
    <Card variant="bordered" padding="md" className="home-panel-card">
      <DashboardPanelHeader
        eyebrow={text.strategyPoints}
        title={text.sniperLevels}
        className="mb-3"
      />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {strategyItems.map((item) => (
          <StrategyItem key={item.label} {...item} />
        ))}
      </div>
    </Card>
  );
};
