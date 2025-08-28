import SwiftUI

struct SettingsView: View {
    @State private var selectedLLM: AppSettings.LLMProvider = .ollama
    @State private var geminiAPIKey: String = ""

    private let settingsService = SettingsService()

    var body: some View {
        VStack {
            Text("Settings")
                .font(.largeTitle)
                .padding()

            Form {
                Picker("Select LLM", selection: $selectedLLM) {
                    Text("Ollama").tag(AppSettings.LLMProvider.ollama)
                    Text("Gemini").tag(AppSettings.LLMProvider.gemini)
                }
                .pickerStyle(SegmentedPickerStyle())

                if selectedLLM == .gemini {
                    SecureField("Gemini API Key", text: $geminiAPIKey)
                }
            }

            Button("Save") {
                let newSettings = AppSettings(llmProvider: selectedLLM, geminiAPIKey: geminiAPIKey)
                settingsService.save(settings: newSettings)
            }
            .padding()

            Spacer()
        }
        .frame(minWidth: 400, minHeight: 300)
        .padding()
        .onAppear {
            let loadedSettings = settingsService.loadSettings()
            self.selectedLLM = loadedSettings.llmProvider
            self.geminiAPIKey = loadedSettings.geminiAPIKey ?? ""
        }
    }
}
