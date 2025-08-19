  import Foundation
  import Combine

  @MainActor
  final class ViewModel: ObservableObject {
      @Published var log: String = ""

      private var task: Process?
      private var logPipe: Pipe?

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
