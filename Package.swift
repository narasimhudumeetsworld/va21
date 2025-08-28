// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "va21",
    platforms: [
        .macOS(.v12)
    ],
    dependencies: [
        .package(url: "https://github.com/google/generative-ai-swift.git", from: "0.4.0"),
        .package(url: "https://github.com/ollama-swift/ollama-swift.git", from: "0.1.0")
    ],
    targets: [
        .executableTarget(
            name: "va21",
            dependencies: [
                .product(name: "GoogleGenerativeAI", package: "generative-ai-swift"),
                .product(name: "Ollama", package: "ollama-swift")
            ]
        )
    ]
)
