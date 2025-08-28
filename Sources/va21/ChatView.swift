import SwiftUI

struct ChatView: View {
    @ObservedObject var vm: ViewModel
    @State private var newMessage: String = ""

    var body: some View {
        VStack {
            Text("AI Assistant")
                .font(.largeTitle)
                .padding()

            ScrollView {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(vm.conversation) { message in
                        HStack {
                            if message.role == "User" {
                                Spacer()
                                Text(message.content)
                                    .padding()
                                    .background(Color.blue)
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                            } else {
                                Text(message.content)
                                    .padding()
                                    .background(Color(white: 0.9))
                                    .cornerRadius(10)
                                Spacer()
                            }
                        }
                    }
                }
                .padding()
            }

            HStack {
                TextField("Type a message...", text: $newMessage)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .onSubmit {
                        sendMessage()
                    }

                Button("Send") {
                    sendMessage()
                }
            }
            .padding()
        }
        .frame(minWidth: 400, minHeight: 500)
    }

    private func sendMessage() {
        guard !newMessage.isEmpty else { return }
        vm.sendMessage(newMessage)
        newMessage = ""
    }
}
