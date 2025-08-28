import Foundation

protocol LLMService {
    func sendMessage(_ message: String) async -> String
}
