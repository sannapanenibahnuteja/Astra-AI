export function nativeApi() {
  if (!window.pywebview?.api) throw new Error('Launch Bob.exe to connect to Windows, voice and local memory. This browser view is a UI preview.');
  return window.pywebview.api;
}
export const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
