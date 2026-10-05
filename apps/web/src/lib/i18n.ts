import type { PageKey } from "./routes";

export type Locale = "en" | "zh-CN";
type Copy = {
  nav: Record<PageKey, string>;
  titles: Record<PageKey, string>;
  subtitles: Record<PageKey, string>;
  kicker: string; skip: string; language: string; preview: string;
  unavailable: string; returnExplore: string;
  homeCards: string[]; homeActions: string[];
  empty: Record<string, string>;
  status: {
    checking: string; refresh: string; error: string; ok: string; degraded: string;
    database: string; vector: string; schema: string; mode: string;
    available: string; unavailable: string; current: string;
    session: string; start: string; clear: string; anonymous: string; privacy: string;
    sessionError: string;
  };
};

export const dictionaries: Record<Locale, Copy> = {
  en: {
    nav: { home: "Home", explore: "Explore", journey: "Journey", stories: "Stories", lens: "Lens", guide: "Guide", dna: "My interests", sources: "Sources", status: "Service status" },
    titles: { home: "FolkVerse China", explore: "Liaoning, a province of stories", journey: "Your cultural journey", stories: "The lantern path", lens: "A discovery in every detail", guide: "Your cultural companion", dna: "Your cultural interests", sources: "Every story has a source", status: "The museum, connected" },
    subtitles: { home: "Begin in Liaoning. Discover its traditions through reviewed exhibits and their sources.", explore: "From the coast to the mountains. Follow the evidence.", journey: "Discover how a learning route could fit your interests.", stories: "Listen. Choose. Become part of the tale.", lens: "Meet the story behind what you see.", guide: "Explore the collection while source-backed conversation is being prepared.", dna: "Choose what sparks your curiosity. Every interest is optional.", sources: "Cultural discovery begins with evidence.", status: "Check the connection behind your visit." },
    kicker: "AN INTERACTIVE AI CULTURAL MUSEUM", skip: "Skip to content", language: "Switch to Chinese",
    preview: "Foundation preview", unavailable: "This experience is not available yet.", returnExplore: "Return to the museum",
    homeCards: ["Discover Liaoning", "Follow a lantern", "Shape a learning route", "Meet your companion"],
    homeActions: ["Open the collection", "Read the story", "Preview a journey", "Meet the guide"],
    empty: {
      explore: "No reviewed regional exhibits have been published yet. The map scene is illustrative; it is not geographic navigation.",
      journey: "Journeys will connect published exhibits into a route that fits your learning time. No routes have been generated yet.",
      stories: "Stories will begin with reviewed cultural context and clearly labelled creative choices. Story text and narration are not available yet.",
      lens: "Object Lens will compare a photograph with an eligible museum catalog. Camera capture and recognition are not available yet.",
      guide: "Source-backed questions and answers will become available after the reviewed collection and guide service are connected. This fictional AI companion is decorative.",
      dna: "No interests have been collected. Choose your own cultural preferences; each is editable and optional.",
      sources: "No reviewed source records have been published yet. Every future exhibit and factual answer will link back to its evidence.",
    },
    status: { checking: "Checking services…", refresh: "Check again", error: "The museum service cannot be reached. Start the local API and try again.", ok: "Services connected", degraded: "Some services are unavailable", database: "Database", vector: "Vector extension", schema: "Database schema", mode: "Application mode", available: "Available", unavailable: "Unavailable", current: "Current", session: "Your anonymous visit", start: "Start a visit", clear: "End this visit", anonymous: "Anonymous visit active", privacy: "No account required. Behavioral tracking is off. Ending this visit revokes its session.", sessionError: "The visit could not be updated. Check the services and try again." },
  },
  "zh-CN": {
    nav: { home: "首页", explore: "探索", journey: "旅程", stories: "故事", lens: "识物", guide: "向导", dna: "我的兴趣", sources: "资料来源", status: "服务状态" },
    titles: { home: "华韵 AI · FolkVerse China", explore: "辽宁，一省故事", journey: "您的文化探索之旅", stories: "灯笼之路", lens: "在细节中发现文化", guide: "您的文化伙伴", dna: "您的文化兴趣图谱", sources: "每个故事，都有出处", status: "连接文化之旅" },
    subtitles: { home: "从辽宁出发，通过审核展览及其来源了解文化传统。", explore: "从海岸到群山，循着来源探索。", journey: "了解学习路线如何结合您的兴趣。", stories: "聆听、选择，走进故事。", lens: "了解眼前物件背后的故事。", guide: "有来源依据的对话正在准备中，您可以先探索馆藏。", dna: "选择让您好奇的主题，每项兴趣都由您决定。", sources: "文化探索，从可靠资料开始。", status: "查看支撑此次访问的服务连接。" },
    kicker: "交互式 AI 文化博物馆", skip: "跳转到内容", language: "Switch to English",
    preview: "基础预览", unavailable: "此功能尚未开放。", returnExplore: "返回博物馆",
    homeCards: ["走进辽宁", "追随灯笼", "规划学习路线", "认识文化伙伴"],
    homeActions: ["打开馆藏", "阅读故事", "预览文化旅程", "认识文化向导"],
    empty: {
      explore: "尚未发布经过审核的地区展览。地图场景仅作示意，不作为地理导航。",
      journey: "文化旅程将串联已发布的展览，并符合您的学习时间。目前尚未生成路线。",
      stories: "故事将基于经过审核的文化背景，创作分支会明确标注。目前暂无故事正文或旁白。",
      lens: "识物功能将把照片与符合使用条件的博物馆藏品目录进行比较。目前尚未开放拍摄与识别。",
      guide: "经过审核的资料库和向导服务连接后，将提供有来源依据的问答。此虚构 AI 形象仅用于装饰。",
      dna: "尚未收集兴趣信息。文化偏好将保持可编辑、可选择；兴趣图谱不代表血统或族群身份。",
      sources: "尚未发布经过审核的来源记录。未来的展览和事实性回答都将关联相应依据。",
    },
    status: { checking: "正在检查服务…", refresh: "重新检查", error: "无法连接博物馆服务。请启动本地 API 后重试。", ok: "服务已连接", degraded: "部分服务暂不可用", database: "数据库", vector: "向量扩展", schema: "数据库结构", mode: "应用模式", available: "可用", unavailable: "不可用", current: "已更新", session: "您的匿名访问", start: "开始访问", clear: "结束本次访问", anonymous: "匿名访问已开启", privacy: "无需注册账号。行为追踪已关闭；结束访问将撤销本次会话。", sessionError: "无法更新此次访问。请检查服务后重试。" },
  },
};
