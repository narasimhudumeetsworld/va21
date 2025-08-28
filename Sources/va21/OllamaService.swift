import Foundation
import Ollama

class OllamaService: LLMService {
    private let ollama: Ollama

    init() {
        // Assumes Ollama is running on the default host and port
        self.ollama = Ollama(host: "http://127.0.0.1:11434")
    }

    func sendMessage(_ message: String) async -> String {
        do {
            let request = Ollama.ChatRequest(model: "llama2", messages: [.init(role: .user, content: message)])
            let response = try await ollama.chat(request: request)
            return response.message?.content ?? "No response from Ollama."
        } catch {
            return "Error communicating with Ollama: \(error.localizedDescription)"
        }
    }
}
