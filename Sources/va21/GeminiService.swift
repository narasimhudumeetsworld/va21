import Foundation
import GoogleGenerativeAI

class GeminiService: LLMService {
    private let generativeModel: GenerativeModel

    init(apiKey: String) {
        self.generativeModel = GenerativeModel(name: "gemini-pro", apiKey: apiKey)
    }

    func sendMessage(_ message: String) async -> String {
        do {
            let response = try await generativeModel.generateContent(message)
            return response.text ?? "No response from Gemini."
        } catch {
            return "Error communicating with Gemini: \(error.localizedDescription)"
        }
    }
}
