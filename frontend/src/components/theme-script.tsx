export function ThemeScript() {
  const code = `
    try {
      var t = localStorage.getItem("reflex.theme");
      if (t === "light") document.documentElement.classList.remove("dark");
      else document.documentElement.classList.add("dark");
    } catch (e) {}
  `;
  return <script dangerouslySetInnerHTML={{ __html: code }} />;
}
