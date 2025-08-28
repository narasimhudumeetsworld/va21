import SwiftUI

struct ContentView: View {
    @StateObject private var vm = ViewModel()

    var body: some View {
        VStack {
            HStack {
                Button("Settings") {
                    vm.isSettingsPresented = true
                }

                TextField("Enter URL", text: $vm.urlString)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .onSubmit {
                        vm.loadURL()
                    }

                Button("Go") {
                    vm.loadURL()
                }

                Spacer()

                Button("Assistant") {
                    vm.isChatPresented = true
                }
            }
            .padding()

            if let url = vm.currentURL {
                WebView(url: url)
            } else {
                Spacer()
                Text("Enter a URL to begin.")
                    .font(.largeTitle)
                Spacer()
            }
        }
        .sheet(isPresented: $vm.isChatPresented) {
            ChatView(vm: vm)
        }
        .sheet(isPresented: $vm.isSettingsPresented) {
            SettingsView()
        }
    }
}
