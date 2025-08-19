  // swift-tools-version:5.7
  import PackageDescription

  let package = Package(
      name: "va21",
      platforms: [.macOS(.v13)],
      products: [.executable(name: "va21", targets: ["va21"])],
      dependencies: [],
      targets: [.executableTarget(name: "va21", dependencies: [])]
  )
