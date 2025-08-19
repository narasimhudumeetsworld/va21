  import SwiftUI

  struct ContentView: View {
      @StateObject private var vm = ViewModel()

      var body: some View {
          VStack(alignment: .leading) {
              Text("VA21 Cockpit")
                  .font(.largeTitle)
                  .padding(.bottom)

              HStack {
                  Button("Start Engine") { vm.startEngine() }
                      .padding(.trailing)
                  Button("Stop Engine") { vm.stopEngine() }
              }
              .padding(.bottom)

              Text("Engine Output Log:")
                  .padding(.bottom, 2)

              ScrollView {
                  Text(vm.log)
                      .font(.system(.body, design: .monospaced))
                      .frame(maxWidth: .infinity, alignment: .leading)
                      .padding()
              }
              .frame(maxHeight: 400)

              Spacer()
          }
          .frame(minWidth: 600, minHeight: 500)
          .padding()
      }
  }
