import Foundation
import Combine

struct ChatMessage: Identifiable {
    let id = UUID()
    let role: String
    let content: String
}

@MainActor
final class ViewModel: ObservableObject {
    // Browser State
    @Published var urlString: String = "https://www.google.com"
    @Published var currentURL: URL?

    // Chat State
    @Published var isChatPresented: Bool = false
    @Published var conversation: [ChatMessage] = []

    // Settings State
    @Published var isSettingsPresented: Bool = false

    // Backend Services
    @Published var log: String = ""
    private var task: Process?
    private var logPipe: Pipe?

    // LLM Service
    private var llmService: LLMService?

    init() {
        loadURL()
        setupLLMService()
        startEngine() // Automatically start the backend services
    }

    func setupLLMService() {
        let settings = SettingsService().loadSettings()
        switch settings.llmProvider {
        case .ollama:
            self.llmService = OllamaService()
            print("LLM Service: Ollama initialized.")
        case .gemini:
            if let apiKey = settings.geminiAPIKey, !apiKey.isEmpty {
                self.llmService = GeminiService(apiKey: apiKey)
                print("LLM Service: Gemini initialized.")
            } else {
                print("LLM Service: Gemini selected but API key is missing.")
                self.llmService = nil
            }
        }
    }

    func sendMessage(_ message: String) {
        guard let llmService = llmService else {
            conversation.append(ChatMessage(role: "System", content: "LLM service is not configured. Please check your settings."))
            return
        }

        let userMessage = ChatMessage(role: "User", content: message)
        conversation.append(userMessage)

        Task {
            let response = await llmService.sendMessage(message)
            let assistantMessage = ChatMessage(role: "Assistant", content: response)
            conversation.append(assistantMessage)
        }
    }

    func loadURL() {
        if let url = URL(string: urlString) {
            currentURL = url
        }
    }

    func startEngine() {
        guard task == nil else { return }
        let process = Process()
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        process.launchPath = "./va21_system/run.sh"
        process.arguments = []

        log.append("[VA21] Starting Engine...\n")

        do {
            try process.run()
            self.task = process
            self.logPipe = pipe
            readPipe(pipe)
        } catch {
            log.append("[ERR] Failed to start engine: \(error.localizedDescription)\n")
        }
    }

    func stopEngine() {
        task?.terminate()
        task = nil
        log.append("[VA21] Engine stopped by user.\n")
    }

    private func readPipe(_ pipe: Pipe) {
        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            guard let self else { return }
            let data = handle.availableData
            if let string = String(data: data, encoding: .utf8) {
                Task { @MainActor in
                    self.log.append(string)
                }
            }
            if self.task?.isRunning == true {
                self.readPipe(pipe)
            }
        }
    }
}
