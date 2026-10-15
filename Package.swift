// swift-tools-version: 5.9
import PackageDescription

// Compile both existing standalone macOS helpers for SwiftPM and CodeQL autobuild.
// Keep separate executable targets because each source has its own top-level entry.
let package = Package(
    name: "VibeEditorsNativeHelpers",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "person-segment", targets: ["PersonSegment"]),
        .executable(name: "vision-segment", targets: ["VisionSegment"]),
    ],
    targets: [
        .executableTarget(
            name: "PersonSegment",
            path: "Payton Editing System/motion/tools",
            sources: ["person_segment.swift"]
        ),
        .executableTarget(
            name: "VisionSegment",
            path: "Payton Editing System/motion/tools",
            sources: ["vision_segment.swift"]
        ),
    ],
    swiftLanguageVersions: [.v5]
)
