import Foundation

struct AppSettings: Codable {
    enum LLMProvider: String, Codable {
        case ollama = "Ollama"
        case gemini = "Gemini"
    }

    var llmProvider: LLMProvider
    var geminiAPIKey: String?
}

class SettingsService {
    private let settingsKey = "appSettings"
    private let userDefaults = UserDefaults.standard

    func save(settings: AppSettings) {
        // In a real app, the API key should be encrypted before saving.
        // For now, we are saving it directly, but this is not secure.
        if let encoded = try? JSONEncoder().encode(settings) {
            userDefaults.set(encoded, forKey: settingsKey)
            print("Settings saved.")
        }
    }

    func loadSettings() -> AppSettings {
        if let savedSettingsData = userDefaults.data(forKey: settingsKey),
           let decodedSettings = try? JSONDecoder().decode(AppSettings.self, from: savedSettingsData) {
            print("Settings loaded.")
            // In a real app, you would decrypt the API key here.
            return decodedSettings
        }
        print("No settings found, returning default settings.")
        // Return default settings if none are saved
        return AppSettings(llmProvider: .ollama, geminiAPIKey: nil)
    }
}
