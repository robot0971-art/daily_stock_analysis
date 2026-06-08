import type { SystemConfigDocLink } from '../types/systemConfig';

export interface SettingsHelpContent {
  title: string;
  summary?: string;
  usage?: string;
  valueNotes?: string[];
  impact?: string[];
  notes?: string[];
  docs?: SystemConfigDocLink[];
}

type SettingsHelpMap = Record<string, SettingsHelpContent>;

const settingsHelpKoKR: SettingsHelpMap = {};
const settingsHelpEnUS: SettingsHelpMap = {
  'settings.base.STOCK_LIST': {
    title: 'Watchlist',
    summary: 'Defines the stock codes used by analysis jobs and notification reports.',
    usage: 'Separate symbols with commas. Korean stocks can use 005930.KS/091990.KQ or six-digit KRX candidates, and US stocks can use ticker symbols such as AAPL.',
    valueNotes: [
      'Scheduled mode rereads the saved STOCK_LIST before each run.',
      'A temporary --stocks argument only affects that manual run.',
      'STOCK_GROUP_N should be a subset of STOCK_LIST and only affects grouped email routing.',
    ],
    impact: ['Affects analysis scope, notification content, and saved history reports.'],
    notes: ['Use English commas between symbols.', 'Save the setting before later tasks can read it.'],
  },
  'settings.ai_model.LITELLM_MODEL': {
    title: 'Primary Model',
    summary: 'Selects the default LLM model for regular analysis flows.',
    usage: 'Use provider/model format, such as deepseek/deepseek-v4-flash, gemini/gemini-3.1-pro-preview, or ollama/qwen3:8b.',
    valueNotes: [
      'Runtime priority is LITELLM_CONFIG > LLM_CHANNELS > legacy provider keys.',
      'When empty, the system tries to infer a model from available API keys or channels.',
      'Agent can use AGENT_LITELLM_MODEL; when empty, it inherits the primary model.',
    ],
    impact: ['Affects regular stock analysis, market review, report generation, and Agent calls without a dedicated model.'],
    notes: [
      'Without a provider prefix, LiteLLM may not know which API key to use.',
      'For Ollama, use OLLAMA_API_BASE or an Ollama channel instead of OPENAI_BASE_URL.',
    ],
  },
  'settings.ai_model.LLM_CHANNELS': {
    title: 'LLM Channels',
    summary: 'Declares model channels for multiple providers, keys, fallbacks, and visual channel management.',
    usage: 'Use comma-separated names such as deepseek,aihubmix; then configure LLM_<NAME>_BASE_URL, LLM_<NAME>_API_KEY(S), and LLM_<NAME>_MODELS for each channel.',
    valueNotes: [
      'Once channel mode is active, runtime selection reads channel configuration first.',
      'Environment variables injected by Docker or GitHub Actions can override values saved from the Web settings page.',
      'Saving in the channel editor updates submitted keys only and does not silently migrate all old config.',
    ],
    impact: ['Affects available sources for primary, Agent, fallback, and Vision models.'],
    notes: [
      'Do not expect legacy keys and Channels to be active at the same time.',
      'Custom channel names in GitHub Actions usually need explicit workflow env mappings.',
    ],
  },
  'settings.ai_model.AGENT_LITELLM_MODEL': {
    title: 'Agent Primary Model',
    summary: 'Sets a dedicated model for Agent workflows.',
    usage: 'Use provider/model format. When empty, Agent inherits the regular primary model.',
    valueNotes: ['Useful when Agent needs stronger reasoning or longer context.', 'Only affects Agent flows.'],
    impact: ['Affects Agent chat, strategy selection, and Agent tool calls.'],
    notes: ['Make sure the model is reachable through enabled channels, YAML routing, or legacy provider keys.'],
  },
  'settings.ai_model.LITELLM_FALLBACK_MODELS': {
    title: 'Fallback Models',
    summary: 'Models tried in order when the primary model fails.',
    usage: 'Use comma-separated provider/model values.',
    valueNotes: ['Fallbacks run only after primary model failures.', 'The channel editor removes unreachable managed-provider references on save.'],
    impact: ['Improves LLM availability, but can change cost, latency, and provider behavior.'],
    notes: ['Do not duplicate the primary model in the fallback list.'],
  },
  'settings.ai_model.LITELLM_CONFIG': {
    title: 'Advanced Routing YAML',
    summary: 'Points to a native LiteLLM YAML routing file for expert routing setups.',
    usage: 'Use a path reachable by the running process, such as ./litellm_config.yaml.',
    valueNotes: ['A valid model_list has higher priority than channels and legacy keys.', 'The Web channel editor does not edit the YAML file.'],
    impact: ['Affects model routing, fallbacks, and available model declarations.'],
    notes: ['If the YAML cannot be parsed, the system falls back to channels or legacy configuration.'],
  },
  'settings.ai_model.LLM_TEMPERATURE': {
    title: 'Temperature',
    summary: 'Controls output randomness.',
    usage: 'Use 0.0 to 2.0. Lower values are more deterministic; higher values are more varied.',
    valueNotes: ['Use low values for stable structured output.', '0.7 is the general default.'],
    impact: ['Affects report wording and structured-output stability.'],
    notes: ['Provider-specific limits can differ.'],
  },
  'settings.ai_model.provider_keys': {
    title: 'Provider API Key',
    summary: 'Configures credentials for model providers or gateways.',
    usage: 'Create a key in the provider console. Related multi-key variants use English commas for rotation or load balancing.',
    valueNotes: ['Secret fields are masked in the Web settings page.', 'Channel mode reads LLM_<NAME>_API_KEY(S) first.'],
    impact: ['Affects model calls, connection tests, and model discovery for the provider.'],
    notes: ['Do not expose real keys in issues, logs, or screenshots.'],
  },
  'settings.ai_model.OPENAI_BASE_URL': {
    title: 'OpenAI-compatible Base URL',
    summary: 'Sets the endpoint root for an OpenAI-compatible service.',
    usage: 'Often ends with /v1. Official APIs, gateways, and local services use different URLs.',
    valueNotes: ['The Base URL must match the API key provider.', 'Gemini or Anthropic official paths usually do not use OPENAI_BASE_URL.'],
    impact: ['Affects legacy OpenAI-compatible model calls.'],
    notes: ['In channel mode, prefer each channel-specific LLM_<NAME>_BASE_URL.'],
  },
  'settings.data_source.TUSHARE_TOKEN': {
    title: 'Tushare Token',
    summary: 'Token used for Tushare Pro data access.',
    usage: 'Paste the token from your Tushare account.',
    valueNotes: ['Available APIs depend on your Tushare permission level.'],
    impact: ['Legacy CN-market data only. It is not required for the KR/US-focused default workflow.'],
    notes: ['Do not commit the token or print it in public logs.'],
  },
  'settings.data_source.REALTIME_SOURCE_PRIORITY': {
    title: 'Realtime Source Priority',
    summary: 'Configures the provider order for realtime quotes.',
    usage: 'Use comma-separated provider names; the system tries them in order.',
    valueNotes: ['Earlier providers are preferred; failures fall back to later providers.'],
    impact: ['Affects current price, intraday analysis, and report fields that depend on realtime prices.'],
    notes: ['A single provider failure should fall back to the next source.'],
  },
  'settings.data_source.realtime_quotes': {
    title: 'Realtime Quotes',
    summary: 'Controls whether realtime quotes and intraday technical indicators are enabled.',
    usage: 'Switch fields use true/false. Provider order is configured separately by REALTIME_SOURCE_PRIORITY.',
    valueNotes: ['Disabling realtime quotes falls back toward historical close prices.', 'Realtime technical indicators use intraday prices.'],
    impact: ['Affects current price, technical indicators, intraday analysis, and report fields.'],
    notes: ['A single provider failure should fall back to the next source.'],
  },
  'settings.data_source.search_api_keys': {
    title: 'Search API Keys',
    summary: 'Configures third-party search services for news and web context.',
    usage: 'Multi-key fields use English commas.',
    valueNotes: ['Search results enrich news, announcements, and market context.'],
    impact: ['Affects news coverage and external information in reports or Agent flows.'],
    notes: ['Search services can differ in quota, rate limits, and regional availability.'],
  },
  'settings.data_source.SEARXNG_BASE_URLS': {
    title: 'SearXNG URLs',
    summary: 'Configures self-hosted or trusted SearXNG search instances.',
    usage: 'Use comma-separated URLs. Self-hosted instances should enable JSON output.',
    valueNotes: ['When public discovery is disabled, only these instances are used.'],
    impact: ['Affects fallback web search when commercial search keys are absent.'],
    notes: ['For production, prefer self-hosted or trusted instances over public ones.'],
  },
  'settings.data_source.ENABLE_CHIP_DISTRIBUTION': {
    title: 'Chip Distribution',
    summary: 'Toggles chip distribution analysis.',
    usage: 'Set false when cloud deployments or data sources are unstable.',
    valueNotes: ['Disabling reduces related data calls and failure noise.'],
    impact: ['Affects chip distribution and cost-area analysis in reports.'],
    notes: ['This feature depends on external data-source stability.'],
  },
  'settings.data_source.news_window': {
    title: 'News Window',
    summary: 'Controls how old news can be before it is excluded from analysis context.',
    usage: 'NEWS_MAX_AGE_DAYS sets the cap; NEWS_STRATEGY_PROFILE selects the profile.',
    valueNotes: ['The effective window is constrained by both values.'],
    impact: ['Affects news context size, freshness, and report length.'],
    notes: ['Too wide can include stale news; too narrow can miss slow-moving events.'],
  },
  'settings.notification.FEISHU_WEBHOOK_URL': {
    title: 'Feishu Webhook URL',
    summary: 'Sends analysis reports to a Feishu group through a custom bot webhook.',
    usage: 'Create a custom bot in the target Feishu group and paste the open-apis/bot/v2/hook webhook URL here.',
    valueNotes: [
      'If signing is enabled, also set FEISHU_WEBHOOK_SECRET.',
      'If keyword protection is enabled, also set FEISHU_WEBHOOK_KEYWORD; the sender prepends it automatically.',
      'FEISHU_APP_ID / FEISHU_APP_SECRET are for app, cloud-doc, or Stream Bot modes and do not enable group webhook delivery.',
    ],
    impact: ['Affects only the Feishu notification channel; delivery failure should not block the main analysis flow.'],
    notes: [
      'Do not use FEISHU_APP_SECRET as FEISHU_WEBHOOK_SECRET.',
      'If IP allowlisting is enabled in Feishu, add the outbound IP of your runtime environment.',
    ],
  },
  'settings.notification.webhooks': {
    title: 'Enterprise WeChat Webhook',
    summary: 'Configures an Enterprise WeChat group bot webhook for report delivery.',
    usage: 'Create a group bot in Enterprise WeChat and paste the Webhook URL that starts with qyapi.weixin.qq.com/cgi-bin/webhook/send.',
    valueNotes: ['Webhook URLs often contain sensitive tokens.', 'Platforms differ in message length, format, and rate limits.'],
    impact: ['Affects delivery for the corresponding webhook channel.'],
    notes: ['A single notification failure should not block the main analysis flow.'],
  },
  'settings.notification.CUSTOM_WEBHOOK_URLS': {
    title: 'Custom Webhooks',
    summary: 'Pushes reports to any service that accepts POST JSON.',
    usage: 'Use comma-separated URLs. CUSTOM_WEBHOOK_BODY_TEMPLATE can customize the JSON body.',
    valueNotes: ['The template must render to a JSON object.', 'Prefer $content_json and $title_json to avoid invalid JSON.'],
    impact: ['Affects AstrBot, NapCat, or self-hosted push integrations.'],
    notes: ['Validate one webhook before adding multiple targets.'],
  },
  'settings.notification.WEBHOOK_VERIFY_SSL': {
    title: 'Webhook SSL Verification',
    summary: 'Controls HTTPS certificate verification for webhook requests.',
    usage: 'Keep true by default. Use false only for trusted internal self-signed certificates.',
    valueNotes: ['Disabling verification weakens MITM protection.'],
    impact: ['Affects TLS verification for custom webhook HTTPS requests.'],
    notes: ['Do not disable SSL verification on public networks.'],
  },
  'settings.notification.telegram': {
    title: 'Telegram Delivery',
    summary: 'Sends reports through a Telegram Bot.',
    usage: 'Create a bot with @BotFather, then set Bot Token and Chat ID. Topic delivery can also set Thread ID.',
    valueNotes: ['The bot must be added to the target group and allowed to post.'],
    impact: ['Affects Telegram notifications.'],
    notes: ['Group Chat IDs are often negative or start with -100.'],
  },
  'settings.notification.email': {
    title: 'Email Delivery',
    summary: 'Sends analysis reports through SMTP.',
    usage: 'Set sender, SMTP authorization code, and comma-separated receivers.',
    valueNotes: ['EMAIL_PASSWORD is usually an app authorization code, not the web login password.', 'STOCK_GROUP_N and EMAIL_GROUP_N can route groups to different receivers.'],
    impact: ['Affects email reports, grouped recipients, and market-review emails.'],
    notes: ['Enable SMTP in the mailbox provider first.'],
  },
  'settings.notification.chat_bots': {
    title: 'Chat Platform Bots',
    summary: 'Configures Discord, Slack, Pushover, ServerChan, and similar channels.',
    usage: 'Choose Webhook or Bot Token mode for the platform; Bot mode usually also needs a channel ID.',
    valueNotes: ['When both Bot and Webhook are configured, existing code may prefer one mode.'],
    impact: ['Affects the corresponding chat notification channel.'],
    notes: ['Bot tokens, webhook URLs, and SendKeys are secrets.'],
  },
  'settings.notification.report_output': {
    title: 'Report Output',
    summary: 'Controls notification detail level, language, and template output.',
    usage: 'REPORT_TYPE supports simple/full/brief. REPORT_LANGUAGE supports ko/en/zh.',
    valueNotes: ['Report language affects default report and notification text, not the Web UI language.'],
    impact: ['Affects notification length, language, and readability.'],
    notes: ['Full reports can be long and may be split by some platforms.'],
  },
  'settings.system.WEBUI_HOST': {
    title: 'WebUI Host',
    summary: 'Controls the network address the WebUI service binds to.',
    usage: 'Use 127.0.0.1 for local-only access. Use 0.0.0.0 for cloud, Docker, or external access.',
    valueNotes: [
      'Current startup logic reads WEBUI_HOST when the host is the default 0.0.0.0; even an explicit --host 0.0.0.0 can still be overwritten by WEBUI_HOST in .env.',
      'Saving it from the settings page writes .env and reloads runtime config objects, but the running WebUI/API process will not rebind its host.',
      'Docker Compose commonly binds 0.0.0.0 inside the container; host access also depends on port mapping.',
    ],
    impact: ['Affects whether the WebUI can be reached locally, on the LAN, or from the public internet after restart.'],
    notes: [
      'Restart the process, Docker container, or service manager after changing WEBUI_HOST.',
      'Enable ADMIN_AUTH_ENABLED when exposing the service publicly.',
      'Behind a reverse proxy, also evaluate TRUST_X_FORWARDED_FOR for login rate limiting and real IP detection.',
    ],
  },
  'settings.system.WEBUI_PORT': {
    title: 'WebUI Port',
    summary: 'Controls the port the WebUI service listens on.',
    usage: 'Default is 8000. Use another port in the 1-65535 range when needed.',
    valueNotes: [
      'Docker or cloud access also depends on host port mappings and firewall rules.',
      'Saving from the settings page only writes .env; it does not rebind the running WebUI/API process.',
    ],
    impact: ['Affects the browser URL used to open WebUI after restart.'],
    notes: ['Restart the process, Docker container, or service manager after changing WEBUI_PORT.'],
  },
  'settings.system.ADMIN_AUTH_ENABLED': {
    title: 'Web Login Protection',
    summary: 'Enables admin password protection for WebUI.',
    usage: 'Use the WebUI auth settings entry to enable or disable this. Reset with python -m src.auth reset_password if needed.',
    valueNotes: ['Recommended for public, shared LAN, or reverse-proxy deployments.', 'This field is shown read-only in the generic config page to avoid bypassing the auth settings flow.'],
    impact: ['Affects WebUI login, settings access, and admin operations.'],
    notes: ['Make sure auth data is persisted in the deployment environment. Manual .env edits require a process restart or the auth settings flow to refresh state.'],
  },
  'settings.system.TRUST_X_FORWARDED_FOR': {
    title: 'Trust X-Forwarded-For',
    summary: 'Uses X-Forwarded-For for client IP detection behind a trusted reverse proxy.',
    usage: 'Set true only behind one trusted reverse proxy. Keep false for direct public access.',
    valueNotes: ['With multiple proxies or CDNs, rate-limit keys may collapse to edge proxy IPs.'],
    impact: ['Affects login rate limiting, auditing, and client IP detection.'],
    notes: ['Do not enable it on an untrusted proxy chain.'],
  },
  'settings.system.schedule': {
    title: 'Schedule',
    summary: 'Controls daily scheduled analysis and whether startup runs immediately.',
    usage: 'SCHEDULE_TIME uses HH:MM 24-hour format. SCHEDULE_ENABLED and SCHEDULE_RUN_IMMEDIATELY control schedule-mode startup behavior.',
    valueNotes: [
      'An already-running schedule mode reads a new SCHEDULE_TIME on the next scheduler check and rebuilds the daily job.',
      'SCHEDULE_ENABLED and SCHEDULE_RUN_IMMEDIATELY are startup-time settings; saving them does not start, stop, or rebuild the current scheduler.',
      'Scheduled runs read the currently saved STOCK_LIST.',
    ],
    impact: ['Affects automatic analysis frequency, startup behavior, and notification timing in schedule mode.'],
    notes: [
      'Check the runtime timezone, especially in containers and servers.',
      'If the current process was not started in schedule mode, saving these fields will not create a scheduler.',
    ],
  },
  'settings.system.RUN_IMMEDIATELY': {
    title: 'Run Immediately',
    summary: 'Controls whether non-schedule startup runs one analysis immediately.',
    usage: 'Set false when you want to start the service without analysis.',
    valueNotes: ['SCHEDULE_RUN_IMMEDIATELY controls schedule mode separately.'],
    impact: ['Affects the first analysis after service startup.'],
    notes: [
      'This is a startup-time setting for non-schedule mode; saving it will not trigger analysis in the running WebUI/API process.',
      'CLI arguments and run mode can also affect final behavior. Restart a non-schedule process for changes to take effect.',
    ],
  },
  'settings.system.TRADING_DAY_CHECK_ENABLED': {
    title: 'Trading Day Check',
    summary: 'Controls whether analysis is skipped on non-trading days.',
    usage: 'Default true. Set false or use --force-run to override.',
    valueNotes: ['Uses market calendars for Korean, US, and other supported markets.'],
    impact: ['Affects whether manual and scheduled runs execute on holidays.'],
    notes: ['Disabling it can produce reports with missing realtime quotes on closed markets.'],
  },
  'settings.system.HTTP_PROXY': {
    title: 'Network Proxy',
    summary: 'Sets a proxy for external API, model, or search requests.',
    usage: 'Use http://host:port format. HTTPS_PROXY can be used for HTTPS proxying.',
    valueNotes: ['Whether it applies depends on the underlying library and environment handling.'],
    impact: ['Affects data sources, LLM, search, and notification network calls.'],
    notes: ['Inside containers, 127.0.0.1 points to the container, not the host machine.'],
  },
  'settings.ai_model.anspire_llm': {
    title: 'Anspire LLM',
    summary: 'Configures Anspire Open as an OpenAI-compatible LLM provider.',
    usage: 'Set the Anspire API key and use an OpenAI-compatible model reference.',
    impact: ['Affects model calls routed through the Anspire channel or legacy provider settings.'],
  },
  'settings.ai_model.legacy_provider_params': {
    title: 'Legacy Provider Parameters',
    summary: 'Controls provider-specific values kept for backward-compatible model routing.',
    usage: 'Prefer LLM Channels for new configuration and keep legacy values only when older flows still need them.',
    impact: ['Can affect fallback model selection and provider adapter behavior.'],
  },
  'settings.data_source.BIAS_THRESHOLD': {
    title: 'Bias Threshold',
    summary: 'Sets the threshold used by market-bias checks and related diagnostics.',
    usage: 'Use a numeric value that matches the expected strategy sensitivity.',
    impact: ['Affects whether signals are treated as neutral or biased.'],
  },
  'settings.data_source.TICKFLOW_API_KEY': {
    title: 'TickFlow API Key',
    summary: 'Credential used for TickFlow data access when that source is enabled.',
    usage: 'Paste the provider key from your TickFlow account.',
    impact: ['Affects realtime or tick-level data paths that depend on TickFlow.'],
    notes: ['Do not expose the key in screenshots, logs, or issues.'],
  },
  'settings.data_source.pytdx': {
    title: 'PyTDX',
    summary: 'Controls legacy PyTDX data-source integration.',
    usage: 'Enable it only when the runtime can reach the configured PyTDX servers.',
    impact: ['Affects CN-market data fallback behavior.'],
  },
  'settings.report.REPORT_SUMMARY_ONLY': {
    title: 'Summary-only Report',
    summary: 'Controls whether generated reports are shortened to summary content.',
    usage: 'Enable it for compact notifications or faster reading.',
    impact: ['Affects report detail level and downstream notification body length.'],
  },
  'settings.report.REPORT_SHOW_LLM_MODEL': {
    title: 'Show Model in Report',
    summary: 'Controls whether report output includes the model name used for generation.',
    usage: 'Enable it when auditability matters; disable it for cleaner user-facing reports.',
    impact: ['Affects report and notification text only.'],
  },
  'settings.report.SINGLE_STOCK_NOTIFY': {
    title: 'Single-stock Notification',
    summary: 'Controls whether each analyzed stock can produce an individual notification.',
    usage: 'Disable it when you only want digest-style output.',
    impact: ['Affects notification volume and channel routing behavior.'],
  },
  'settings.report.REPORT_TEMPLATES_DIR': {
    title: 'Report Templates Directory',
    summary: 'Directory used for custom report templates.',
    usage: 'Use a path reachable by the running process.',
    impact: ['Affects report rendering when custom templates are enabled.'],
  },
  'settings.report.REPORT_RENDERER_ENABLED': {
    title: 'Report Renderer',
    summary: 'Enables the report renderer pipeline.',
    usage: 'Keep enabled for normal report generation unless troubleshooting renderer output.',
    impact: ['Affects rendered report content and visual report paths.'],
  },
  'settings.report.REPORT_INTEGRITY_ENABLED': {
    title: 'Report Integrity Checks',
    summary: 'Enables validation of report structure and required fields.',
    usage: 'Keep enabled to catch incomplete or malformed report output.',
    impact: ['Can block or flag reports that do not meet integrity requirements.'],
  },
  'settings.report.REPORT_HISTORY_COMPARE_N': {
    title: 'History Compare Count',
    summary: 'Number of previous reports used for history comparison.',
    usage: 'Use 0 to disable comparison or a small positive number for recent context.',
    impact: ['Affects report context, history reads, and output length.'],
  },
  'settings.report.MERGE_EMAIL_NOTIFICATION': {
    title: 'Merged Email Notification',
    summary: 'Controls whether email notifications are merged into a combined message.',
    usage: 'Enable it to reduce email count for batch analysis runs.',
    impact: ['Affects email notification grouping and content shape.'],
  },
  'settings.notification.channel_routing': {
    title: 'Notification Channel Routing',
    summary: 'Configures which notification channels receive specific report types or severities.',
    usage: 'Use routing rules to separate urgent alerts, digests, and regular reports.',
    impact: ['Affects destination channels and duplicate-notification behavior.'],
  },
  'settings.notification.dedup': {
    title: 'Notification Deduplication',
    summary: 'Controls suppression of repeated notifications within a deduplication window.',
    usage: 'Tune the window to reduce noise while preserving important repeated signals.',
    impact: ['Affects whether similar notifications are sent or skipped.'],
  },
  'settings.notification.quiet_hours': {
    title: 'Quiet Hours',
    summary: 'Controls time windows when non-urgent notifications should be held or skipped.',
    usage: 'Set local quiet-hour ranges for scheduled or digest-heavy workflows.',
    impact: ['Affects notification timing and delivery volume.'],
  },
  'settings.notification.MIN_SEVERITY': {
    title: 'Minimum Severity',
    summary: 'Minimum severity required before a notification is sent.',
    usage: 'Raise it to reduce noise or lower it to receive more routine updates.',
    impact: ['Affects alert and report notification filtering.'],
  },
  'settings.notification.DAILY_DIGEST_ENABLED': {
    title: 'Daily Digest',
    summary: 'Controls whether daily digest notifications are generated.',
    usage: 'Enable it for summarized scheduled results.',
    impact: ['Affects digest creation and notification workload.'],
  },
  'settings.system.ANALYSIS_DELAY': {
    title: 'Analysis Delay',
    summary: 'Delay between analysis tasks in batch runs.',
    usage: 'Increase it to reduce provider pressure or rate-limit risk.',
    impact: ['Affects total batch duration and external API request pacing.'],
  },
  'settings.system.DEBUG': {
    title: 'Debug Mode',
    summary: 'Enables additional diagnostic output.',
    usage: 'Use it for local troubleshooting, not for routine production runs.',
    impact: ['Affects logs and may expose more operational detail.'],
  },
  'settings.system.LOG_LEVEL': {
    title: 'Log Level',
    summary: 'Controls runtime logging verbosity.',
    usage: 'Use INFO for normal operation and DEBUG when investigating issues.',
    impact: ['Affects log volume and troubleshooting visibility.'],
  },
  'settings.system.MAX_WORKERS': {
    title: 'Maximum Workers',
    summary: 'Maximum worker count for concurrent analysis work.',
    usage: 'Increase cautiously according to provider limits and machine capacity.',
    impact: ['Affects throughput, resource usage, and rate-limit risk.'],
  },
  'settings.system.market_review': {
    title: 'Market Review',
    summary: 'Controls scheduled or optional market-review generation.',
    usage: 'Enable it when broad-market context should be included alongside stock reports.',
    impact: ['Affects scheduled work, LLM usage, and generated report content.'],
  },
  'settings.backtest.BACKTEST_ENABLED': {
    title: 'Backtest',
    summary: 'Controls whether backtest evaluation is enabled.',
    usage: 'Enable it when strategy or report decisions should include historical evaluation.',
    impact: ['Affects analysis runtime, history storage, and report context.'],
  },
  'settings.backtest.BACKTEST_ENGINE_VERSION': {
    title: 'Backtest Engine Version',
    summary: 'Selects the backtest engine behavior version.',
    usage: 'Keep the default unless intentionally testing a newer engine contract.',
    impact: ['Affects backtest calculations and comparability of historical results.'],
  },
  'settings.backtest.eval_params': {
    title: 'Backtest Evaluation Parameters',
    summary: 'Controls thresholds and options used by backtest evaluation.',
    usage: 'Tune only when you understand the effect on strategy scoring.',
    impact: ['Affects score interpretation, report context, and validation results.'],
  },
  'settings.agent.AGENT_MODE': {
    title: 'Agent Mode',
    summary: 'Controls whether Agent workflows are enabled and how they run.',
    usage: 'Use the default mode for regular analysis and enable advanced modes only when needed.',
    impact: ['Affects Agent routing, tool use, and LLM usage.'],
  },
  'settings.agent.AGENT_ARCH': {
    title: 'Agent Architecture',
    summary: 'Selects the Agent architecture or orchestration style.',
    usage: 'Keep the default unless testing a specific Agent implementation.',
    impact: ['Affects Agent planning, memory, and tool orchestration behavior.'],
  },
  'settings.agent.AGENT_MAX_STEPS': {
    title: 'Agent Max Steps',
    summary: 'Maximum number of Agent reasoning or tool steps.',
    usage: 'Raise it only when complex tasks need more tool iterations.',
    impact: ['Affects latency, cost, and termination behavior.'],
  },
  'settings.agent.AGENT_MEMORY_ENABLED': {
    title: 'Agent Memory',
    summary: 'Controls whether Agent memory is available.',
    usage: 'Enable it only when persistent context is desired.',
    impact: ['Affects personalization, context reuse, and storage behavior.'],
  },
  'settings.agent.AGENT_NL_ROUTING': {
    title: 'Natural-language Routing',
    summary: 'Controls whether natural-language intent routing is used for Agent tasks.',
    usage: 'Enable it for flexible user requests; disable it for stricter deterministic routing.',
    impact: ['Affects Agent route selection and predictability.'],
  },
  'settings.agent.AGENT_ORCHESTRATOR_MODE': {
    title: 'Agent Orchestrator Mode',
    summary: 'Selects how Agent orchestration is coordinated.',
    usage: 'Keep the default unless validating a specific orchestrator mode.',
    impact: ['Affects multi-step Agent execution and fallback behavior.'],
  },
  'settings.agent.AGENT_ORCHESTRATOR_TIMEOUT_S': {
    title: 'Agent Orchestrator Timeout',
    summary: 'Timeout in seconds for Agent orchestration.',
    usage: 'Increase it for slower providers or complex tool workflows.',
    impact: ['Affects when Agent tasks fail fast versus continue waiting.'],
  },
  'settings.agent.AGENT_RISK_OVERRIDE': {
    title: 'Agent Risk Override',
    summary: 'Controls whether Agent risk guards can be overridden.',
    usage: 'Keep disabled unless a controlled workflow explicitly requires it.',
    impact: ['Affects safety checks and operational risk handling.'],
  },
  'settings.agent.AGENT_SKILLS': {
    title: 'Agent Skills',
    summary: 'List of enabled Agent skills.',
    usage: 'Use comma-separated skill identifiers.',
    impact: ['Affects which specialized Agent capabilities can be selected.'],
  },
  'settings.agent.AGENT_SKILL_AUTOWEIGHT': {
    title: 'Skill Auto-weighting',
    summary: 'Controls whether Agent skill weighting is adjusted automatically.',
    usage: 'Enable it when skill choice should adapt to observed task fit.',
    impact: ['Affects Agent skill ranking and selection.'],
  },
  'settings.agent.AGENT_SKILL_DIR': {
    title: 'Agent Skill Directory',
    summary: 'Directory where Agent skills are loaded from.',
    usage: 'Use a path reachable by the running process.',
    impact: ['Affects skill discovery and Agent capability availability.'],
  },
  'settings.agent.AGENT_SKILL_ROUTING': {
    title: 'Skill Routing',
    summary: 'Controls how Agent tasks are routed to skills.',
    usage: 'Keep the default for normal operation and tune only for custom skill sets.',
    impact: ['Affects skill selection, fallback behavior, and Agent output.'],
  },
  'settings.agent.DEEP_RESEARCH': {
    title: 'Deep Research',
    summary: 'Controls whether deeper research workflows are enabled.',
    usage: 'Enable it for more thorough but slower analysis.',
    impact: ['Affects search usage, LLM cost, runtime, and report depth.'],
  },
  'settings.agent.EVENT_ALERT_RULES_JSON': {
    title: 'Event Alert Rules JSON',
    summary: 'JSON rules used by event alert monitoring.',
    usage: 'Provide valid JSON matching the event alert rule schema.',
    impact: ['Affects which events trigger alerts and notifications.'],
  },
  'settings.agent.context_compression': {
    title: 'Context Compression',
    summary: 'Controls whether Agent context is compressed during long workflows.',
    usage: 'Enable it to fit longer workflows into model context limits.',
    impact: ['Affects retained detail, cost, and long-task stability.'],
  },
  'settings.agent.event_monitor': {
    title: 'Event Monitor',
    summary: 'Controls Agent-backed event monitoring behavior.',
    usage: 'Enable it when event rules should be evaluated continuously or on schedule.',
    impact: ['Affects monitoring workload, alert generation, and notification volume.'],
  },
  'settings.llm_channel.channel_name': {
    title: 'Channel Name',
    summary: 'Generates the LLM_<NAME>_* environment variable names.',
    usage: 'Use lowercase letters, numbers, and underscores only. Saving also writes LLM_CHANNELS.',
    valueNotes: ['deepseek maps to LLM_DEEPSEEK_BASE_URL, LLM_DEEPSEEK_API_KEY(S), and LLM_DEEPSEEK_MODELS.'],
    impact: ['Affects env key names, runtime selection, and GitHub Actions mappings.'],
    notes: ['Renaming does not migrate every external environment variable automatically.'],
  },
  'settings.llm_channel.protocol': {
    title: 'Channel Protocol',
    summary: 'Declares which compatibility protocol the channel uses.',
    usage: 'OpenAI Compatible fits most gateways. Official Gemini, Anthropic, and DeepSeek can use their protocol.',
    valueNotes: ['Protocol affects model prefix normalization, connection tests, and discovery.'],
    impact: ['Affects request adapters, model parsing, and runtime model references.'],
    notes: ['Protocol, Base URL, and API Key must belong to the same service.'],
  },
  'settings.llm_channel.base_url': {
    title: 'Base URL',
    summary: 'Endpoint root for this channel.',
    usage: 'OpenAI-compatible services often use a /v1 URL. Some official SDK channels can leave it empty.',
    valueNotes: ['Provider presets are references; actual availability depends on account, region, and provider APIs.'],
    impact: ['Affects connection tests, model discovery, and all calls through the channel.'],
    notes: ['Do not mix one provider key with another provider Base URL.'],
  },
  'settings.llm_channel.api_key': {
    title: 'API Key',
    summary: 'Credential used by this channel.',
    usage: 'Use one key directly, or multiple keys separated by English commas.',
    valueNotes: ['Local unauthenticated services such as Ollama can leave it empty.'],
    impact: ['Affects connection tests, discovery, runtime calls, and key rotation.'],
    notes: ['Do not expose real keys in screenshots, logs, or issues.'],
  },
  'settings.llm_channel.models': {
    title: 'Channel Models',
    summary: 'Declares models available for runtime selection.',
    usage: 'Use model discovery when /models is supported, or manually enter comma-separated model names.',
    valueNotes: ['Runtime primary, Agent, Vision, and fallback choices reference this list.'],
    impact: ['Affects selectable models, stale-model cleanup, and routing.'],
    notes: ['Actual availability still depends on provider permissions and runtime tests.'],
  },
  'settings.llm_channel.capability_checks': {
    title: 'Runtime Capability Checks',
    summary: 'Manually checks JSON, tools, stream, or vision support for the current channel model.',
    usage: 'Select capabilities and run the check. It sends real LLM requests.',
    valueNotes: ['Multiple checks can take 20-40 seconds and may consume quota.'],
    impact: ['Only affects page diagnostics; it does not change saved configuration.'],
    notes: ['Capability labels are hints; runtime checks and real calls are the final signal.'],
  },
  'settings.llm_channel.temperature': {
    title: 'Temperature',
    summary: 'Unified runtime sampling temperature.',
    usage: 'Slider range is 0 to 2. Lower is steadier; higher is more random.',
    valueNotes: ['Saving writes LLM_TEMPERATURE.'],
    impact: ['Affects regular analysis, Agent output, and reports.'],
    notes: ['Lower it first when structured output is unstable.'],
  },
  'settings.llm_channel.primary_model': {
    title: 'Primary Model',
    summary: 'Default runtime model for regular analysis.',
    usage: 'Choose from enabled channel models. Auto uses the first available model.',
    valueNotes: ['Saving writes LITELLM_MODEL.'],
    impact: ['Affects stock analysis, market review, and default report generation.'],
    notes: ['Unreachable managed-provider models can be cleaned up on save.'],
  },
  'settings.llm_channel.agent_primary_model': {
    title: 'Agent Primary Model',
    summary: 'Dedicated primary model for Agent flows.',
    usage: 'Choose an independent model, or auto-inherit the regular primary model.',
    valueNotes: ['Saving writes AGENT_LITELLM_MODEL.'],
    impact: ['Affects Agent chat, strategy workflows, and tool calls.'],
    notes: ['A stronger Agent model can also increase cost and latency.'],
  },
  'settings.llm_channel.fallback_models': {
    title: 'Fallback Models',
    summary: 'Backup models used when the primary model fails.',
    usage: 'Check one or more models. The primary model is not duplicated into fallbacks.',
    valueNotes: ['Saving writes LITELLM_FALLBACK_MODELS.'],
    impact: ['Affects LLM failure recovery and cross-provider behavior.'],
    notes: ['Validate fallback models with connection tests or real calls first.'],
  },
  'settings.llm_channel.vision_model': {
    title: 'Vision Model',
    summary: 'Model used for image or screenshot inputs.',
    usage: 'Choose a model with image-input support, or use the automatic Vision default.',
    valueNotes: ['Saving writes VISION_MODEL.'],
    impact: ['Affects screenshot extraction and vision analysis.'],
    notes: ['Text-only models may not support vision; use capability checks to confirm.'],
  },
};

function getPreferredHelpMap(locale?: string | null): SettingsHelpMap {
  if (locale?.toLowerCase().startsWith('en')) {
    return settingsHelpEnUS;
  }
  return settingsHelpKoKR;
}

export function getSettingsHelpContent(
  helpKey?: string | null,
  fallbackDescription?: string,
  locale?: string | null,
): SettingsHelpContent | null {
  if (!helpKey) {
    return null;
  }

  const localized = getPreferredHelpMap(locale)[helpKey] ?? settingsHelpEnUS[helpKey];
  if (localized) {
    return localized;
  }

  if (fallbackDescription) {
    return {
      title: '설정 설명',
      summary: fallbackDescription,
    };
  }

  return null;
}
