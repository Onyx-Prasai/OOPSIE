document.addEventListener("DOMContentLoaded", () => {
  const errorInput = document.getElementById("errorInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const results = document.getElementById("results");
  const plainEnglishText = document.getElementById("plainEnglishText");
  const likelyCauseText = document.getElementById("likelyCauseText");
  const repairPromptText = document.getElementById("repairPromptText");
  const verificationList = document.getElementById("verificationList");
  const copyPromptBtn = document.getElementById("copyPromptBtn");

  // Load pending error from context menu selection if available
  if (chrome.storage && chrome.storage.local) {
    chrome.storage.local.get("pendingError", (data) => {
      if (data.pendingError) {
        errorInput.value = data.pendingError;
        chrome.storage.local.remove("pendingError");
      }
    });
  }

  analyzeBtn.addEventListener("click", () => {
    const text = errorInput.value.trim();
    if (!text) return;

    analyzeBtn.textContent = "Analyzing Engine...";
    analyzeBtn.disabled = true;

    setTimeout(() => {
      let explanation = "Your app encountered a missing dependency or invalid configuration.";
      let cause = "The package or environment variable needed by your app is missing.";
      let prompt = `My project encounters the error:\n"${text.substring(0, 120)}..."\n\nPlease check dependencies and configuration, fix the underlying import or setup, and make minimal targeted changes without modifying unrelated UI features.`;
      let checklist = ["Run npm install or update env keys", "Restart local dev server", "Verify feature functionality"];

      if (text.includes("Module not found") || text.includes("supabase")) {
        explanation = "Your app is trying to use Supabase, but the Supabase client package '@supabase/supabase-js' is not installed.";
        cause = "AI generated Supabase code, but the package was not installed in package.json.";
        prompt = `My project displays: "Module not found: Can't resolve '@supabase/supabase-js'". Inspect package.json, install @supabase/supabase-js using your package manager, and verify the import paths. Make the smallest possible change.`;
        checklist = ["Verify @supabase/supabase-js is in package.json", "Restart npm run dev", "Check console errors cleared"];
      } else if (text.includes("NEXT_PUBLIC_") || text.includes("api key") || text.includes("process.env")) {
        explanation = "Your code requires an environment variable that is missing or undefined.";
        cause = "The key was not added to .env.local or client variables are missing the NEXT_PUBLIC_ prefix.";
        prompt = `My Next.js project fails with missing environment variables. Inspect process.env references, ensure client keys use NEXT_PUBLIC_, and update .env.example with placeholder names. Do not commit actual secrets.`;
        checklist = ["Check .env.local exists in root", "Ensure NEXT_PUBLIC_ prefix for client keys", "Restart dev server"];
      }

      plainEnglishText.textContent = explanation;
      likelyCauseText.textContent = cause;
      repairPromptText.textContent = prompt;
      verificationList.innerHTML = checklist.map(item => `<li>✅ ${item}</li>`).join("");

      results.classList.remove("hidden");
      analyzeBtn.textContent = "Analyze Chaos 🪄";
      analyzeBtn.disabled = false;
    }, 600);
  });

  copyPromptBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(repairPromptText.textContent);
    copyPromptBtn.textContent = "Copied! ✨";
    setTimeout(() => {
      copyPromptBtn.textContent = "Copy Prompt 📋";
    }, 2000);
  });
});
