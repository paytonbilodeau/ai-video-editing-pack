import Foundation
import Vision
import CoreImage
import AppKit

// Usage: swift segment.swift <input.png> <output-mask.png>
let args = CommandLine.arguments
guard args.count == 3 else { print("usage: segment.swift in out"); exit(1) }
let inURL = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])
guard !FileManager.default.fileExists(atPath: outURL.path) else { print("Output exists; choose a new path"); exit(2) }

guard let ciImage = CIImage(contentsOf: inURL) else { print("load fail"); exit(1) }
let request = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])
try handler.perform([request])
guard let result = request.results?.first else { print("no fg found"); exit(1) }
let maskPB = try result.generateScaledMaskForImage(forInstances: result.allInstances, from: handler)
let maskCI = CIImage(cvPixelBuffer: maskPB)
let ctx = CIContext()
guard let cg = ctx.createCGImage(maskCI, from: maskCI.extent) else { print("cg fail"); exit(1) }
let rep = NSBitmapImageRep(cgImage: cg)
guard let png = rep.representation(using: .png, properties: [:]) else { print("png fail"); exit(1) }
try png.write(to: outURL)
print("mask written \(cg.width)x\(cg.height)")
