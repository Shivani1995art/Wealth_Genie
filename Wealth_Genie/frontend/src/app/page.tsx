import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-[#030712] text-gray-100 flex flex-col justify-between overflow-hidden">
      {/* Decorative Blur Backgrounds */}
      <div className="glow-blur-green top-[10%] left-[5%]" />
      <div className="glow-blur-indigo bottom-[20%] right-[10%]" />

      {/* Header */}
      <header className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-500/20">
            W
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Wealth Genie
          </span>
        </div>
        <nav className="flex items-center gap-4">
          <Link
            href="/login"
            className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 text-sm font-medium bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl shadow-lg shadow-emerald-500/20 transition-all duration-200"
          >
            Get Started
          </Link>
        </nav>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 max-w-7xl mx-auto px-6 flex flex-col justify-center items-center text-center py-20">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-semibold text-emerald-400 mb-8 backdrop-blur-sm animate-pulse">
          ✨ Introducing Wealth Genie MVP
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 max-w-4xl leading-tight">
          Your Intelligent{" "}
          <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-indigo-400 bg-clip-text text-transparent">
            AI Personal Financial Coach
          </span>
        </h1>

        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mb-10 leading-relaxed">
          Upload bank statements, credit card bills, and salary slips. Our specialized AI agents analyze your debt, savings, and budget patterns to deliver a unified, deterministic advisory report.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center w-full max-w-md mb-20">
          <Link
            href="/register"
            className="w-full sm:w-auto px-8 py-4 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-2xl shadow-xl shadow-emerald-500/20 transition-all duration-200 flex justify-center items-center gap-2"
          >
            Create Free Account
          </Link>
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white font-semibold rounded-2xl border border-white/10 transition-all duration-200 flex justify-center items-center"
          >
            Try Demo Login
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
          {/* Feature 1 */}
          <div className="glass-panel p-8 rounded-3xl text-left hover:border-white/20 transition-all duration-300 group">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold mb-6 group-hover:scale-110 transition-transform">
              📊
            </div>
            <h2 className="text-xl font-bold mb-3 text-white">Universal Parser</h2>
            <p className="text-gray-400 text-sm leading-relaxed">
              Upload any standard PDF document (statements, bills, slips). Our universal extractor parses them directly into a structured, unified profile schema.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="glass-panel p-8 rounded-3xl text-left hover:border-white/20 transition-all duration-300 group">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold mb-6 group-hover:scale-110 transition-transform">
              🤖
            </div>
            <h2 className="text-xl font-bold mb-3 text-white">Specialist Agents</h2>
            <p className="text-gray-400 text-sm leading-relaxed">
              Three autonomous specialist agents analyze your debt (payoffs, interest), savings (emergency funds), and budget (categories, trends) independently.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="glass-panel p-8 rounded-3xl text-left hover:border-white/20 transition-all duration-300 group">
            <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 font-bold mb-6 group-hover:scale-110 transition-transform">
              🧠
            </div>
            <h2 className="text-xl font-bold mb-3 text-white">AI CFO Synthesis</h2>
            <p className="text-gray-400 text-sm leading-relaxed">
              The AI CFO synthesizes individual specialist reports into a single, unified financial health dashboard, report, and conversational Q&A assistant.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center border-t border-white/5 gap-4">
        <p className="text-sm text-gray-500">
          © {new Date().getFullYear()} Wealth Genie. Built for secure, privacy-first personal finance.
        </p>
        <div className="flex gap-6 text-sm text-gray-500">
          <a href="#" className="hover:text-gray-300 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-gray-300 transition-colors">Terms of Service</a>
        </div>
      </footer>
    </div>
  );
}
