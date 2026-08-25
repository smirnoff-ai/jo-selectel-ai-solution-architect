const KEY = "reflex.return";

export function rememberReturn(path: string) {
  sessionStorage.setItem(KEY, path);
}

export function takeReturn(): string {
  return sessionStorage.getItem(KEY) || "/desk";
}
