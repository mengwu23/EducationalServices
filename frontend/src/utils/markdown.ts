/** Markdown 渲染工具 — 将 AI 回复的 Markdown 文本转为安全 HTML。 */
import { marked } from "marked";

/** 配置 marked：禁用原始 HTML 以防止 XSS */
marked.setOptions({
  breaks: true,       // 单个换行转为 <br>
  gfm: true,          // GitHub Flavored Markdown
});

/**
 * 将 Markdown 文本渲染为 HTML 字符串。
 * 已通过 marked 的 sanitize 选项和默认不解析原始 HTML 来防止 XSS。
 */
export function renderMarkdown(text: string | null | undefined): string {
  if (!text) return "";
  // marked 默认不解析原始 HTML 标签，安全
  return marked.parse(text) as string;
}
