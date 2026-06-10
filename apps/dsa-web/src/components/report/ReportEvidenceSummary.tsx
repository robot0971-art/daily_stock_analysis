import type React from 'react';
import { BarChart3, Database, FileText, Newspaper } from 'lucide-react';
import type {
  AnalysisMap,
  ReportDetails,
  ReportLanguage,
  RunDiagnosticComponent,
  RunDiagnosticComponentStatus,
  RunDiagnosticSummary,
} from '../../types/analysis';
import { Badge, Card, StatusDot } from '../common';
import { DashboardPanelHeader } from '../dashboard';
import { normalizeReportLanguage } from '../../utils/reportLanguage';

interface ReportEvidenceSummaryProps {
  analysisMap?: AnalysisMap;
  details?: ReportDetails;
  diagnosticSummary?: RunDiagnosticSummary;
  language?: ReportLanguage;
}

type EvidenceStatus = 'used' | 'fallback' | 'missing';
type EvidenceTone = 'success' | 'warning' | 'neutral';

interface EvidenceItem {
  id: string;
  title: string;
  status: EvidenceStatus;
  provider?: string;
  detail: string;
  icon: React.ComponentType<{ className?: string }>;
}

const STATUS_TEXT: Record<ReportLanguage, Record<EvidenceStatus, string>> = {
  ko: {
    used: '사용됨',
    fallback: '대체 경로',
    missing: '확인 필요',
  },
  en: {
    used: 'Used',
    fallback: 'Fallback',
    missing: 'Needs check',
  },
  zh: {
    used: '사용됨',
    fallback: '대체 경로',
    missing: '확인 필요',
  },
};

const TONE_BY_STATUS: Record<EvidenceStatus, EvidenceTone> = {
  used: 'success',
  fallback: 'warning',
  missing: 'neutral',
};

const BADGE_BY_STATUS: Record<EvidenceStatus, React.ComponentProps<typeof Badge>['variant']> = {
  used: 'success',
  fallback: 'warning',
  missing: 'default',
};

const providerFromComponent = (component?: RunDiagnosticComponent): string | undefined => {
  const provider = component?.details?.provider;
  return typeof provider === 'string' && provider.trim() ? provider.trim() : undefined;
};

const numberFromComponent = (component?: RunDiagnosticComponent, key = 'record_count'): number | undefined => {
  const value = component?.details?.[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
};

const getComponentStatus = (component?: RunDiagnosticComponent): RunDiagnosticComponentStatus | undefined => (
  component?.status
);

const evidenceStatusFromComponent = (
  component?: RunDiagnosticComponent,
  hasEvidence = false,
): EvidenceStatus => {
  const status = getComponentStatus(component);
  if (status === 'ok') return 'used';
  if (status === 'degraded') return 'fallback';
  if (hasEvidence) return 'used';
  return 'missing';
};

const hasObjectContent = (value: unknown): boolean => (
  Boolean(value) && typeof value === 'object' && Object.keys(value as Record<string, unknown>).length > 0
);

const getSnapshotObject = (details?: ReportDetails): Record<string, unknown> => {
  const snapshot = details?.contextSnapshot;
  return snapshot && typeof snapshot === 'object' ? snapshot : {};
};

const hasAnalysisMapSource = (analysisMap: AnalysisMap | undefined, id: string): boolean => (
  Array.isArray(analysisMap?.dataSources)
  && analysisMap.dataSources.some((source) => source.id === id && source.available)
);

const buildEvidenceItems = ({
  analysisMap,
  details,
  diagnosticSummary,
  language,
}: Required<Pick<ReportEvidenceSummaryProps, 'language'>> & Omit<ReportEvidenceSummaryProps, 'language'>): EvidenceItem[] => {
  const components = diagnosticSummary?.components || {};
  const realtime = components.realtime_quote;
  const daily = components.daily_data;
  const news = components.news;
  const snapshot = getSnapshotObject(details);
  const newsCount = numberFromComponent(news) ?? (
    typeof snapshot.news_result_count === 'number' ? snapshot.news_result_count : undefined
  );
  const hasNewsContent = Boolean(details?.newsContent?.trim());
  const hasNewsSource = hasAnalysisMapSource(analysisMap, 'news') || hasNewsContent || Boolean(newsCount && newsCount > 0);
  const hasFundamentalSource = (
    hasAnalysisMapSource(analysisMap, 'fundamental_context')
    || hasObjectContent(details?.financialReport)
    || hasObjectContent(details?.dividendMetrics)
    || hasObjectContent(snapshot.fundamental_context)
  );
  const hasRealtimeSource = hasAnalysisMapSource(analysisMap, 'realtime_quote');
  const hasDailySource = hasAnalysisMapSource(analysisMap, 'daily_history');
  const realtimeProvider = providerFromComponent(realtime);
  const dailyProvider = providerFromComponent(daily);
  const realtimeRecordCount = numberFromComponent(realtime);
  const dailyRecordCount = numberFromComponent(daily);
  const text = language === 'en'
    ? {
        realtimeDetail: realtimeProvider
          ? `Latest quote provider: ${realtimeProvider}`
          : 'Latest quote source is not clearly recorded.',
        dailyDetail: dailyRecordCount
          ? `${dailyRecordCount} daily bars used for trend and indicators.`
          : 'Daily price history is not clearly recorded.',
        newsDetail: newsCount && newsCount > 0
          ? `${newsCount} news items were found and linked to the analysis.`
          : hasNewsContent
            ? 'News text was included in the analysis context.'
            : 'No searchable news evidence was recorded.',
        filingDetail: hasFundamentalSource
          ? 'Financial, disclosure, or fundamental context is attached.'
          : 'Financial or filing evidence was not attached.',
      }
    : {
        realtimeDetail: realtimeProvider
          ? `현재가 출처: ${realtimeProvider}`
          : '현재가 출처가 명확히 기록되지 않았습니다.',
        dailyDetail: dailyRecordCount
          ? `일봉 ${dailyRecordCount}건을 추세와 지표 계산에 사용했습니다.`
          : '일봉 데이터 사용 기록이 명확하지 않습니다.',
        newsDetail: newsCount && newsCount > 0
          ? `뉴스 ${newsCount}건을 검색해 분석 근거에 연결했습니다.`
          : hasNewsContent
            ? '뉴스 본문이 분석 컨텍스트에 포함됐습니다.'
            : '검색된 뉴스 근거가 기록되지 않았습니다.',
        filingDetail: hasFundamentalSource
          ? '재무, 공시 또는 기본 정보 컨텍스트가 첨부됐습니다.'
          : '재무 또는 공시 근거가 첨부되지 않았습니다.',
      };

  return [
    {
      id: 'realtime',
      title: language === 'en' ? 'Realtime Quote' : '실시간 시세',
      status: evidenceStatusFromComponent(realtime, hasRealtimeSource),
      provider: realtimeProvider,
      detail: realtimeRecordCount ? `${text.realtimeDetail} (${realtimeRecordCount} records)` : text.realtimeDetail,
      icon: BarChart3,
    },
    {
      id: 'daily',
      title: language === 'en' ? 'Daily Price Data' : '일봉 데이터',
      status: evidenceStatusFromComponent(daily, hasDailySource),
      provider: dailyProvider,
      detail: text.dailyDetail,
      icon: Database,
    },
    {
      id: 'news',
      title: language === 'en' ? 'News Search' : '뉴스 검색',
      status: evidenceStatusFromComponent(news, hasNewsSource),
      provider: providerFromComponent(news),
      detail: text.newsDetail,
      icon: Newspaper,
    },
    {
      id: 'filing',
      title: language === 'en' ? 'Filings and Fundamentals' : '공시/재무',
      status: hasFundamentalSource ? 'used' : 'missing',
      detail: text.filingDetail,
      icon: FileText,
    },
  ];
};

export const ReportEvidenceSummary: React.FC<ReportEvidenceSummaryProps> = ({
  analysisMap,
  details,
  diagnosticSummary,
  language = 'ko',
}) => {
  const reportLanguage = normalizeReportLanguage(language);
  const items = buildEvidenceItems({
    analysisMap,
    details,
    diagnosticSummary,
    language: reportLanguage,
  });
  const hasAnyEvidence = items.some((item) => item.status !== 'missing');

  if (!hasAnyEvidence && !diagnosticSummary && !analysisMap && !details?.contextSnapshot) {
    return null;
  }

  return (
    <Card variant="bordered" padding="md" className="home-panel-card text-left">
      <DashboardPanelHeader
        eyebrow={reportLanguage === 'en' ? 'EVIDENCE' : '근거 요약'}
        title={reportLanguage === 'en' ? 'Data Used in This Analysis' : '분석에 사용된 데이터'}
        className="mb-3"
      />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => {
          const Icon = item.icon;
          const tone = TONE_BY_STATUS[item.status];
          return (
            <div key={item.id} className="home-subpanel p-3">
              <div className="mb-2 flex items-start justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2">
                  <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-cyan/20 bg-cyan/10 text-cyan">
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0">
                    <h3 className="truncate text-sm font-semibold text-foreground">{item.title}</h3>
                    {item.provider ? (
                      <p className="truncate text-xs text-muted-text">{item.provider}</p>
                    ) : null}
                  </div>
                </div>
                <Badge variant={BADGE_BY_STATUS[item.status]} className="shrink-0 shadow-none">
                  <StatusDot tone={tone} className="h-1.5 w-1.5" />
                  {STATUS_TEXT[reportLanguage][item.status]}
                </Badge>
              </div>
              <p className="text-xs leading-5 text-secondary-text">{item.detail}</p>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
