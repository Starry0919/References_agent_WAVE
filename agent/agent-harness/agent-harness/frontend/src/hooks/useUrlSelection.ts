import { useSearchParams } from "react-router-dom";

/**
 * Selected-object state as a URL search param (State Ownership Matrix,
 * architecture doc §18.2: "可分享导航状态 | URL | ... selected object ...
 * | 刷新与深链接可恢复"). Every Workspace stage that lets the user select
 * an object (hypothesis, candidate, finding, validation item) must use
 * this instead of local useState, so a refresh or a copied link restores
 * the same selection and drives the same Inspector content (Page 2 prompt
 * §22 "选中对象 ... 刷新、后退/前进、路由切换后必须验证 ... Inspector
 * selection 合理恢复").
 *
 * Uses `{ replace: true }` so clicking through objects does not spam
 * browser history - only the initial navigation to a stage is a history
 * entry, not every selection within it.
 */
export function useUrlSelection(paramKey = "selected"): [string | null, (id: string | null) => void] {
  const [params, setParams] = useSearchParams();
  const selected = params.get(paramKey);

  function setSelected(id: string | null) {
    const next = new URLSearchParams(params);
    if (id === null) next.delete(paramKey);
    else next.set(paramKey, id);
    setParams(next, { replace: true });
  }

  return [selected, setSelected];
}
