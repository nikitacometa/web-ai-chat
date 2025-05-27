export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">AI Satisfy</h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Build AI-powered applications that actually satisfy your users. No
          more frustrating chatbots. Just intelligent solutions.
        </p>
        <div className="space-x-4">
          <a
            href="/with-app/demo"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            View Demo App
          </a>
          <a
            href="https://chat.aisatisfy.me"
            className="inline-block bg-gray-200 text-gray-800 px-8 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            Try Chat
          </a>
        </div>
      </div>

      {/* App Types Section */}
      <div className="container mx-auto px-4 py-16 bg-white">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Explore Our Apps
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="border rounded-lg p-6 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🔬</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Research</h3>
            <p className="text-gray-600 mb-4">
              AI-powered research papers and analysis
            </p>
            <a
              href="/research/research_ai_agent_libraries"
              className="text-blue-600 hover:underline"
            >
              View Example →
            </a>
          </div>

          <div className="border rounded-lg p-6 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">💻</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Apps</h3>
            <p className="text-gray-600 mb-4">Interactive AI applications</p>
            <a
              href="/app/example_app"
              className="text-blue-600 hover:underline"
            >
              Coming Soon →
            </a>
          </div>

          <div className="border rounded-lg p-6 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🎨</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Images</h3>
            <p className="text-gray-600 mb-4">
              AI-generated images and visualizations
            </p>
            <a
              href="/image/example_visualization"
              className="text-blue-600 hover:underline"
            >
              Coming Soon →
            </a>
          </div>

          <div className="border rounded-lg p-6 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📄</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Documents</h3>
            <p className="text-gray-600 mb-4">
              AI-enhanced documents and reports
            </p>
            <a
              href="/doc/example_report"
              className="text-blue-600 hover:underline"
            >
              Coming Soon →
            </a>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Why AI Satisfy?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🤖</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Smart AI Integration</h3>
            <p className="text-gray-600">
              Powered by state-of-the-art language models that understand
              context and nuance.
            </p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
            <p className="text-gray-600">
              Built on modern infrastructure for instant responses and real-time
              interactions.
            </p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🎨</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Customizable</h3>
            <p className="text-gray-600">
              Tailor the AI experience to match your brand and user needs
              perfectly.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gray-100 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Satisfy Your Users?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Join thousands of developers building better AI experiences.
          </p>
          <a
            href="https://api.aisatisfy.me/docs"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Explore API Docs
          </a>
        </div>
      </div>
    </div>
  );
}
